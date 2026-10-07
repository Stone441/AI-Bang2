"""Conservative grammar for the documented inquiry; no model-generated SQL."""
import re
from datetime import datetime, timedelta, timezone


def parse_inquiry(question, as_of=None):
    if not isinstance(question,str) or len(question)>500: raise ValueError('Invalid inquiry')
    resource=re.fullmatch(r'Who accessed ([A-Za-z0-9][A-Za-z0-9_:./-]{0,199}) in the last (\d{1,2}) days\??',question.strip(),re.I)
    if resource:
        days=int(resource[2])
        if not 1<=days<=90:raise ValueError('Range must be 1–90 days')
        end=as_of or datetime.now(timezone.utc)
        return {'resource_id':resource[1],'start_time':(end-timedelta(days=days)).isoformat(),
                'end_time':end.isoformat(),'resource_scope':'payment-service','page_size':50}
    match=re.fullmatch(r'Show (?:everything|events) (jdoe|eng_a|eng_b|product_ops) accessed related to payment-service in the last (\d{1,2}) days\.?',question.strip(),re.I)
    if not match: raise ValueError('Use the supported inquiry template or structured filters')
    days=int(match[2])
    if not 1<=days<=90: raise ValueError('Range must be 1–90 days')
    end=as_of or datetime.now(timezone.utc)
    return {'actor':match[1].lower(),'start_time':(end-timedelta(days=days)).isoformat(),
            'end_time':end.isoformat(),'resource_scope':'payment-service','page_size':50}
