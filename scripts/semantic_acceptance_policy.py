"""Local acceptance-run stopping policy; no model, credentials or ledger access."""


class AcceptanceStop(RuntimeError):
    pass


class AcceptanceRun:
    def __init__(self, case_ids):
        self.remaining = set(case_ids)
        if not self.remaining or len(self.remaining) != len(case_ids):
            raise ValueError('Unique frozen cases required')
        self.pending = None
        self.awaiting_assessment = None
        self.assessments = {}
        self.failures = 0
        self.stopped = False

    def begin(self, case_id):
        if self.stopped or self.pending is not None or self.awaiting_assessment is not None or case_id not in self.remaining:
            raise AcceptanceStop('Stopped, active, or already attempted case')
        self.remaining.remove(case_id)
        self.pending = case_id

    def finish(self, case_id, http_status, answer, grant):
        if self.pending != case_id:
            self.stopped = True
            raise AcceptanceStop('Unmatched completion')
        self.pending = None
        if grant['unknown'] or http_status != 200:
            self.stopped = True
            raise AcceptanceStop('Unknown usage or HTTP failure; no retry')
        if answer.get('answer_status') == 'evidence_only' or answer.get('review_status') != 'accepted':
            self.failures += 1
        self.awaiting_assessment = case_id
        if self.failures >= 2:
            self.stopped = True
            raise AcceptanceStop('Repeated synthesis failure; no further dispatch')

    def assess(self, case_id, *, passed, evidence):
        """Record an independent oracle/source check before any next dispatch.

        Model review acceptance is not this assessment. The runner's operator
        supplies a durable evidence reference after checking the actual answer.
        A failed business assessment ends the run without retry.
        """
        if (self.stopped or self.awaiting_assessment != case_id
                or type(passed) is not bool or not isinstance(evidence, str)
                or not evidence.strip()):
            self.stopped = True
            raise AcceptanceStop('Missing or unmatched independent assessment')
        self.assessments[case_id] = {'passed': passed, 'evidence': evidence}
        self.awaiting_assessment = None
        if not passed:
            self.stopped = True
            raise AcceptanceStop('Business acceptance failed; no further dispatch')
