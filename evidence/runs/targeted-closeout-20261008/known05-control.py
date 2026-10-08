"""One explicit scoped contrast; old questions/oracle/output untouched."""
from pathlib import Path
from scripts.business_validation import run
case={'id':'known05_payment_service_control','actor':'product_ops','question':'For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?','expected_behavior':'answer','required_evidence':['J-02','J-03','C-02'],'required_claim_spans':['PAY-102','Done','PAY-103','In Progress','not approved'],'forbidden_evidence':['C-03','J-01-comment-sec','BV-27']}
run(Path(__file__).parent/'known05-control-final',strategy='bm25',live_model=True,selected_cases=[case],temperature=0,reasoning_effort='low',output_tokens=8192)
