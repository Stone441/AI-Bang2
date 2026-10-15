"""Local acceptance-run stopping policy; no model, credentials or ledger access."""


class AcceptanceStop(RuntimeError):
    pass


class AcceptanceRun:
    def __init__(self, case_ids):
        self.remaining = set(case_ids)
        if not self.remaining or len(self.remaining) != len(case_ids):
            raise ValueError('Unique frozen cases required')
        self.pending = None
        self.failures = 0
        self.stopped = False

    def begin(self, case_id):
        if self.stopped or self.pending is not None or case_id not in self.remaining:
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
        if self.failures >= 2:
            self.stopped = True
            raise AcceptanceStop('Repeated synthesis failure; no further dispatch')
