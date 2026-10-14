"""Exact structural retrieval, legacy history, and source contract regression."""
import unittest
from brain.retrieval import spans, window_evidence, resolve_window, ranked_windows, tokens
from brain.structure import structural_spans, quote_parts
from scripts.business_validation import build_world
import test_retrieval as legacy
import test_whole_source_review as whole
from brain.synthesis import DeepSeekStructuredSourceReviewModel


class StructuralUnits(unittest.TestCase):
    def test_observed_archive_separates_historical_and_current_decisions_from_entries(self):
        world,_=build_world();resource=world.resources['BV-11']
        ranked=ranked_windows(resource,tokens('What caused the ledger migration incident, was it DNS?'),strategy='structured')
        selected=[resource['text'][a:b] for _,a,b in ranked]
        self.assertTrue(any('DNS was a historical webhook hypothesis.' in p for p in selected))
        self.assertTrue(any('shadow table' in p for p in selected))
        relevant=[p for p in selected if 'DNS was' in p or 'shadow table' in p]
        self.assertFalse(any('Archived migration rehearsal entry' in p for p in relevant))

    def test_tables_lists_and_adjacent_qualifications_are_indivisible(self):
        blocks=[
            '# Scope\nPilot only.\n\nAccount\tApproval\nBusiness\tYes\n\nPersonal\tNo\n\nOnly the listed pilot accounts qualify.\n\n',
            '# Operations\nApproved recovery steps:\n\n- Inspect the queue.\n- Follow the approved procedure.\n\nDo not perform these steps in production.\n\n',
            '# State\nThe pilot is approved.\n\nHowever, GA remains unapproved.\n\n']
        text=''.join(blocks)+'# Archive\n'+('Unrelated historical entry.\n'*200)
        parts=[text[a:b] for a,b in structural_spans(text)]
        for block in blocks:self.assertIn(block,parts)
        self.assertEqual(''.join(parts),text)

    def test_exact_offsets_heading_ancestry_and_legacy_resolve(self):
        world,_=build_world();r=world.resources['BV-11']
        for strategy in ('fixed','structured'):
            for a,b in spans(r['text'],strategy):
                eid,locator,text=window_evidence(r,a,b,strategy)
                self.assertEqual(resolve_window(r,eid),(locator,text))
                self.assertEqual(text,r['text'][a:b])
                for heading in locator.get('section_context',[]):
                    self.assertEqual(heading['text'],r['text'][heading['start']:heading['end']])
        for eid in ('BV-11@1#s1:1:2401','BV-11@1#s1:0:999999','BV-11@1#s2:0:2400'):
            with self.assertRaises(ValueError):resolve_window(r,eid)

    def test_short_and_oversized_units_are_not_clipped(self):
        for text in ('Short document unchanged.', 'Long unbroken prose '*1000):
            self.assertEqual(structural_spans(text),[(0,len(text))])
        table='Scope\tStatus\n'+('Pilot\tUnapproved\n'*1500)
        self.assertEqual(structural_spans(table),[(0,len(table))])

    def test_quotes_preserve_unicode_words_and_all_bytes(self):
        for text in ('Sentence with qualifications. '*90, '表格\t范围\t未批准。\n'*120,
                     'Records without punctuation '*90, 'x'*601):
            parts=quote_parts(text)
            self.assertEqual(''.join(parts),text)
            self.assertTrue(all(12<=len(p.strip()) and len(p)<=600 for p in parts))
            if text!='x'*601:
                for left,right in zip(parts,parts[1:]):
                    self.assertFalse(left[-1].isalnum() and right[0].isalnum())


class StructuredSecurity(legacy.RetrievalWindows):
    def setUp(self):
        super().setUp();self.engine.window_strategy='structured';self.engine.history_read_mode='batch'

    def test_old_history_and_windows_remain_accessible_after_switch(self):
        self.engine.window_strategy='fixed';answer=self.ask()
        self.engine.window_strategy='structured'
        self.assertEqual(self.engine.safe_history(self.actor,answer['request_id']),[answer])
        for e in answer['evidence']:
            self.assertEqual(self.engine.evidence(self.actor,e['evidence_id'])['text'],e['text'])


class StructuredReview(whole.WholeReview):
    def candidate(self):
        from brain.deepseek import PRICE_DATE
        return DeepSeekStructuredSourceReviewModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=self.transport,today=PRICE_DATE,
            reasoning_effort='none',output_tokens=8192)

    def engine(self):
        engine,world=super().engine();engine.window_strategy='structured'
        return engine,world
