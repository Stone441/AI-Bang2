"""Private acceptance adapter; reviewer-only diagnostic, never a product answer."""
import json

class QuoteGate:
 name='diagnostic-review-only-no-user-answer'
 def __init__(self,base,case):self.base=base;self.case=case;self.transport=base.transport
 def generate_with_provenance(self,question,evidence,request_id,provenance,authorize,observe=None):
  from brain.sectioned_answer import SectionedAnswerReview
  from brain.synthesis import validate_claim
  target=next((e for e in evidence if e.resource_id==self.case['source_resource_id']),None)
  if target is None or target.version!=self.case['source_version']:raise RuntimeError('Gate evidence unavailable or changed')
  claim=json.loads(json.dumps(self.case['claim']))
  claim['evidence_ids']=[target.evidence_id];claim['supports'][0]['evidence_id']=target.evidence_id
  validate_claim(claim,[target])
  authorize('review_dispatch')
  review=SectionedAnswerReview(self.base._key,self.base.ledger,synthetic_only=True,transport=self.transport,today=self.base._today(),claims=[claim],parts=self.case['parts'],temperature=self.base.temperature,reasoning_effort='none',output_tokens=8192)
  result=review.generate(question,[target],request_id=request_id,provenance=provenance,observe=observe,stage='review')
  # Diagnostic only. Do not publish a synthetic draft as a generated answer.
  return {'claims':[],'uncertainties':[],'model_call':result['model_call']}

def install_probe(engine, base, case):
    # Keep the engine's ordinary authorization path; never add this adapter to
    # the single-source-review allowlist or weaken that production restriction.
    engine.source_review_dispatch = 'legacy'
    engine.model = QuoteGate(base, case)
    return engine.model
