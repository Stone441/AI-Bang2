"""Conservative omission guard for explicitly requested operational actions.

This detects a narrow source structure, not arbitrary semantic completeness.
It can reject a missing passage; it cannot authorize, manufacture facts, approve
a proposal or override a model's failed support/coverage verdict.
"""
import re
from .retrieval import tokens, SUBJECT_NEUTRAL

ACTION_REQUESTS = frozenset({'mitigation', 'mitigations', 'remediation', 'procedure',
    'runbook', 'safeguard', 'safeguards', 'workaround', 'workarounds', 'measures',
    'steps', 'actions'})
ACTION_ROLE = re.compile(r'\b(?:runbook|playbook|mitigation|remediation|procedure|workaround|response steps)\b', re.I)
OPERATION = re.compile(r'\b(?:inspect|check|verify|increase|reduce|disable|enable|restart|rollback|revert|rotate|isolate|switch|route|pause|drain|scale|apply|restore|limit|notify)\b|\bfollow\b[^.\n]{0,80}\b(?:procedure|runbook|playbook)\b', re.I)


def required_action_sources(question, evidence):
    terms = tokens(question)
    if not set(re.findall(r'[a-z]+', question.lower())) & ACTION_REQUESTS:
        return set()
    # Owner/date/approval-only questions do not ask for the operational steps.
    if not re.search(r'\b(?:what|which|how|list|describe|summarize|give)\b', question, re.I):
        return set()
    if re.search(r'\b(?:who|whose|owner|owns|when)\b', question, re.I):
        return set()
    anchors = terms - SUBJECT_NEUTRAL - ACTION_REQUESTS - {'how', 'list', 'describe', 'summarize', 'give'}
    if not anchors:
        return set()  # Ambiguous subject: this narrow guard makes no inference.
    return {e.evidence_id for e in evidence
            if anchors & tokens(e.title+'\n'+e.text)
            and ACTION_ROLE.search(e.title+'\n'+e.text) and OPERATION.search(e.text)}
