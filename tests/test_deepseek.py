import copy
import json
import tempfile
import threading
import unittest
import contextlib
import io
from unittest.mock import patch
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

from brain.budget import BudgetLedger, BudgetExceeded
from brain.contracts import Evidence, Actor
from brain.deepseek import DeepSeekEvidenceModel, ModelUnavailable, PRICE_DATE, ENDPOINT, cost_upper
from brain.engine import Engine
from brain.audit import Audit
from brain.sources import FixtureWorld
from brain.store import Store


class Transport:
    def __init__(self):
        self.calls = []
        self.error = False
        self.response = {'model': 'deepseek-flash', 'usage': {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 120},
                         'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': '{"evidence_ids":["drive:test@1"]}'}}]}

    def _send(self, request):
        self.calls.append(request)
        if self.error: raise RuntimeError('Upstream error must not escape')
        return 200, copy.deepcopy(self.response)


class DeepSeekBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'budget.sqlite')
        self.ledger = BudgetLedger(self.path)
        self.transport = Transport()
        self.model = DeepSeekEvidenceModel('synthetic-not-a-key', self.ledger, synthetic_only=True,
                                           transport=self.transport, today=PRICE_DATE)
        self.evidence = Evidence('drive:test@1', 'drive:test', 1, 'drive', 'Synthetic', {},
                                 '[SYNTHETIC] GA not approved.', '2026-10-05', '2026-10-05', 'https://example.com')

    def tearDown(self):
        self.ledger.close(); self.tmp.cleanup()

    def test_budgeted_fixed_endpoint_selection_derives_text_from_evidence(self):
        result = self.model.generate('Is GA approved?', [self.evidence])
        self.assertEqual(result['claims'], [{'text': self.evidence.text, 'evidence_ids': [self.evidence.evidence_id]}])
        request = self.transport.calls[0]
        self.assertEqual(request.full_url, ENDPOINT)
        payload = json.loads(request.data)
        self.assertEqual(payload['thinking'], {'type': 'disabled'})
        self.assertFalse(payload['stream']); self.assertNotIn('tools', payload)
        self.assertEqual(payload['response_format'], {'type': 'json_object'})
        self.assertNotIn('source_url', payload['messages'][1]['content'])
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], cost_upper(100, 20))

    def test_no_evidence_or_unmarked_content_never_sent(self):
        self.assertEqual(self.model.generate('Question', [])['claims'], [])
        with self.assertRaises(ModelUnavailable):
            self.model.generate('Question', [replace(self.evidence, text='Private business data')])
        self.assertEqual(self.transport.calls, [])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'], 0)

    def test_approved_atlassian_banner_reaches_model_without_rewriting_evidence(self):
        banner = 'SYNTHETIC COMPETITION TEST DATA — not an actual company record.'
        for source, fid in [('confluence', 'C-01'), ('confluence', 'C-02'), ('jira', 'J-02'), ('jira', 'J-03')]:
            with self.subTest(source=source, fixture=fid):
                evidence = replace(self.evidence, source=source,
                                   text=banner + '\nFixture ID: ' + fid + '\nGA not approved.')
                result = self.model.generate('Is GA approved?', [evidence])
                self.assertEqual(result['claims'][0]['text'], evidence.text)
                payload = json.loads(self.transport.calls[-1].data)
                self.assertEqual(json.loads(payload['messages'][1]['content'])['evidence'][0]['text'], evidence.text)

    def test_legacy_banner_missing_fixture_wrong_source_or_title_only_never_sent(self):
        banner = 'SYNTHETIC COMPETITION TEST DATA — not an actual company record.'
        for source, text in [('confluence', banner), ('confluence', banner + '\nFixture ID: C-99'),
                             ('drive', banner + '\nFixture ID: C-01'),
                             ('jira', banner + '\nFixture ID: C-01'),
                             ('confluence', banner + '\nFixture ID: J-03'),
                             ('jira', 'Fixture ID: J-03\nPrivate business data'),
                             ('confluence', 'Fixture ID: C-01\nPrivate business data')]:
            with self.subTest(source=source, text=text):
                with self.assertRaises(ModelUnavailable):
                    self.model.generate('Question', [replace(self.evidence, source=source, title='[SYNTHETIC]', text=text)])
        self.assertEqual(self.transport.calls, [])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'], 0)

    def test_timeout_keeps_reservation_across_restart_and_hides_error(self):
        self.transport.error = True
        with self.assertRaises(ModelUnavailable) as caught: self.model.generate('Question', [self.evidence])
        self.assertNotIn('Upstream', str(caught.exception))
        self.ledger.close(); self.ledger = BudgetLedger(self.path)
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'], self.model.reservation)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)

    def test_budget_exhaustion_prevents_network(self):
        self.ledger.reserve(BudgetLedger.APPROVED_MAX)
        with self.assertRaises(BudgetExceeded): self.model.generate('Question', [self.evidence])
        self.assertEqual(self.transport.calls, [])

    def test_unknown_usage_retains_full_reservation(self):
        for usage in ({}, {'prompt_tokens': True, 'completion_tokens': 1, 'total_tokens': 2},
                      {'prompt_tokens': 10, 'completion_tokens': 2, 'total_tokens': 13}):
            with self.subTest(usage=usage):
                self.transport.response['usage'] = usage
                with self.assertRaises(ModelUnavailable): self.model.generate('Question', [self.evidence])
        self.assertEqual(self.ledger.summary()['pending_requests'], 3)
        self.transport.response['usage'] = {'prompt_tokens': 100, 'completion_tokens': 1025, 'total_tokens': 1125}
        with self.assertRaises(ModelUnavailable): self.model.generate('Question', [self.evidence])
        self.assertTrue(self.ledger.summary()['blocked_for_review'])
        with self.assertRaises(BudgetExceeded): self.model.generate('Question', [self.evidence])

    def test_unknown_duplicate_forged_or_free_form_output_rejected_but_usage_charged(self):
        for content in ('{"evidence_ids":["restricted@1"]}', '{"evidence_ids":["drive:test@1","drive:test@1"]}',
                        '{"evidence_ids":[],"fact":"GA approved"}', '{"evidence_ids":[],"evidence_ids":[]}',
                        '{"evidence_ids":"drive:test@1"}', 'not json'):
            with self.subTest(content=content):
                self.transport.response['choices'][0]['message']['content'] = content
                with self.assertRaises(ModelUnavailable): self.model.generate('Question', [self.evidence])
        self.assertEqual(self.ledger.summary()['pending_requests'], 0)
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 6 * cost_upper(100, 20))

    def test_truncated_tool_or_wrong_model_output_is_not_an_answer(self):
        for field, value in [('finish_reason', 'length'), ('tool_calls', [{'function': 'write'}]), ('model', 'other')]:
            response = copy.deepcopy(self.transport.response)
            if field == 'model': self.transport.response[field] = value
            elif field == 'tool_calls': self.transport.response['choices'][0]['message'][field] = value
            else: self.transport.response['choices'][0][field] = value
            with self.assertRaises(ModelUnavailable): self.model.generate('Question', [self.evidence])
            self.transport.response = response

    def test_price_date_and_approval_guard(self):
        for kwargs in ({'synthetic_only': False, 'today': PRICE_DATE}, {'synthetic_only': True, 'today': PRICE_DATE + timedelta(days=1)},
                       {'synthetic_only': True, 'today': PRICE_DATE - timedelta(days=1)}):
            with self.assertRaises(ValueError): DeepSeekEvidenceModel('synthetic-not-a-key', self.ledger, **kwargs)

    def test_cross_midnight_request_blocked_before_budget_or_network(self):
        from brain.deepseek import PriceReviewRequired
        # The runtime clock advances; no production override/date rollback.
        with patch('brain.deepseek.datetime') as clock:
            clock.now.return_value.date.return_value = PRICE_DATE
            model = DeepSeekEvidenceModel('synthetic-not-a-key', self.ledger,
                                          synthetic_only=True, transport=self.transport)
            clock.now.return_value.date.return_value = PRICE_DATE + timedelta(days=1)
            with self.assertRaises(PriceReviewRequired) as caught:
                model.generate('Question', [self.evidence])
        self.assertIn('Preserve the existing USD20', str(caught.exception))
        self.assertEqual(self.transport.calls, [])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'], 0)
        self.assertEqual(self.ledger.db.execute('SELECT COUNT(*) FROM model_calls').fetchone()[0], 0)

    def test_reviewed_restart_keeps_existing_budget_and_allows_mock_request(self):
        from brain.deepseek import check_price_review, PriceReviewRequired
        existing = self.ledger.reserve(1234, query_id='a' * 32, model='deepseek-flash')
        self.ledger.dispatch(existing)
        next_day = PRICE_DATE + timedelta(days=1)
        with patch('brain.deepseek.datetime') as clock:
            clock.now.return_value.date.return_value = next_day
            with self.assertRaises(PriceReviewRequired): check_price_review()
            # Simulates a documented re-review of the same rates, then startup.
            with patch('brain.deepseek.PRICE_DATE', next_day):
                check_price_review()
                model = DeepSeekEvidenceModel('synthetic-not-a-key', self.ledger,
                                              synthetic_only=True, transport=self.transport)
                model.generate('Question', [self.evidence])
        self.assertEqual(len(self.transport.calls), 1)
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'], 1234 + cost_upper(100, 20))
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)

    def test_expired_startup_stops_before_listener_credentials_and_source_calls(self):
        from brain.operator_web import main
        output = io.StringIO()
        with patch('brain.deepseek.datetime') as clock, contextlib.redirect_stdout(output), \
             patch('brain.operator_web.create_server') as server, \
             patch('scripts.confluence_probe.load_reader') as reader:
            clock.now.return_value.date.return_value = PRICE_DATE + timedelta(days=1)
            self.assertEqual(main(['--config', 'missing', '--model', 'deepseek', '--live']), 2)
        server.assert_not_called(); reader.assert_not_called()
        self.assertIn('model_price_review_required', output.getvalue())
        self.assertIn('USD20 ledger', output.getvalue())

    def test_operator_price_guard_precedes_credentials_and_no_live_is_no_send(self):
        from brain.operator_web import main
        with contextlib.redirect_stdout(io.StringIO()), patch('brain.operator_web.create_server') as server, \
             patch('brain.deepseek.check_price_review', side_effect=ValueError('stale')):
            self.assertEqual(main(['--config', 'missing', '--model', 'deepseek']), 2)
            self.assertEqual(main(['--config', 'missing', '--model', 'deepseek', '--live']), 2)
            server.assert_not_called()

    def test_web_worker_thread_can_use_durable_budget(self):
        failures = []
        def worker():
            try: self.model.generate('Question', [self.evidence])
            except Exception as error: failures.append(type(error).__name__)
        thread = threading.Thread(target=worker); thread.start(); thread.join()
        self.assertEqual(failures, [])
        self.assertEqual(self.ledger.summary()['pending_requests'], 0)

    def test_engine_denied_evidence_never_reaches_provider(self):
        world = FixtureWorld(); store = Store(); store.initialize(world)
        engine = Engine(store, world, Audit(store), self.model)
        # Real Engine identity and ACL boundary; unauthorized resources must not
        # be sent merely because the provider supports a live endpoint.
        world.revoked.update(('eng_b', rid) for rid in world.resources)
        response = engine.query(Actor('eng_b'), 'payment-service retry root cause')
        self.assertEqual(response['evidence'], [])
        self.assertEqual(self.transport.calls, [])
        store.db.close()

    def test_engine_live_selection_still_enforces_actor_acl_and_post_generation_revocation(self):
        for revoke in (False, True):
            with self.subTest(revoke=revoke):
                world = FixtureWorld()
                for resource in world.resources.values(): resource['text'] = '[SYNTHETIC] ' + resource['text']
                store = Store(); store.initialize(world)
                audit = Audit(store)
                engine = Engine(store, world, audit, self.model, mode='fixture_live_model_selection')
                captured = []
                def send(request):
                    supplied = json.loads(json.loads(request.data)['messages'][1]['content'])['evidence']
                    captured.extend(e['evidence_id'] for e in supplied)
                    chosen = supplied[0]['evidence_id']
                    response = copy.deepcopy(self.transport.response)
                    response['choices'][0]['message']['content'] = json.dumps({'evidence_ids': [chosen]})
                    if revoke: world.revoked.add(('eng_b', chosen.rsplit('@', 1)[0]))
                    return 200, response
                self.transport._send = send
                try:
                    if revoke:
                        with self.assertRaises(PermissionError): engine.query(Actor('eng_b'), 'payment-service retry incident')
                        self.assertFalse(any(e['event_type'] == 'response_committed' for e in audit.export()))
                    else:
                        answer = engine.query(Actor('eng_b'), 'payment-service retry incident')
                        self.assertEqual(len(answer['claims']), 1)
                        self.assertEqual(answer['uncertainties'], [self.model.answer_notice])
                        self.assertEqual(answer['model'], self.model.name)
                    self.assertTrue(captured)
                    self.assertNotIn('S-01@1', captured)  # eng_b cannot read private incident channel.
                finally: store.db.close()

    def test_operator_http_model_selection_and_same_session_revoke(self):
        import test_operator_web
        import test_http
        from brain.server import create_server
        app, source = test_operator_web.setup_app()
        original_get = source.get
        def synthetic_get(url, authorization):
            status, body = original_get(url, authorization)
            if body and 'body' in body:
                body['body']['storage']['value'] = '<p>[SYNTHETIC] Runbook budget version 1</p>'
            return status, body
        source.get = synthetic_get
        self.transport.response['choices'][0]['message']['content'] = '{"evidence_ids":["confluence:98564@1"]}'
        app.engine.model = self.model
        app.engine.mode = 'confluence_mock_http_mock_model_selection'
        self.server = create_server(app)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True); thread.start()
        self.cookie = ''; self.csrf = ''
        request = lambda path, data=None: test_http.HTTP.request(self, path, data)
        try:
            self.assertEqual(request('/api/query', {'question': 'runbook'})[0], 403)
            status, login = request('/api/operator/login', {'ticket': app.bootstrap_ticket()})
            self.assertEqual(status, 200); self.csrf = login['csrf']
            self.assertEqual(request('/api/query', {'question': 'runbook', 'role': 'admin'})[0], 400)
            status, answer = request('/api/query', {'question': 'runbook'})
            self.assertEqual(status, 200); self.assertEqual(answer['model'], self.model.name)
            self.assertEqual(answer['claims'][0]['text'], '[SYNTHETIC] Runbook budget version 1')
            self.assertEqual(len(self.transport.calls), 1)
            source.allowed.clear()
            # Advance only the fixture's rate-limit timestamp; preserve the
            # same authenticated cookie, CSRF token and real ACL checks.
            for session in app.sessions.values(): session['last_query'] = 0
            status, after = request('/api/query', {'question': 'runbook'})
            self.assertEqual(status, 200); self.assertEqual(after['evidence'], [])
            self.assertEqual(len(self.transport.calls), 1)
            status, history = request('/api/history')
            self.assertEqual(status, 200)
            self.assertTrue(next(r for r in history['history'] if r['request_id'] == answer['request_id'])['unavailable'])
            self.assertEqual(request('/api/evidence/confluence:98564@1')[0], 403)
            status, exported = request('/api/export/' + answer['request_id'])
            self.assertEqual(status, 404)
            self.assertEqual(exported, {'error':'Unavailable'})
            self.assertNotIn('Runbook budget version 1', json.dumps(exported))
        finally:
            self.server.shutdown(); self.server.server_close(); thread.join(); app.store.db.close()
