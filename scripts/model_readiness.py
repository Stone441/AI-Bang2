"""Offline model price readiness only; no credentials, ledger or API access."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from brain.deepseek import (MODEL, PRICE_DATE, PRICE_SOURCE, INPUT_RATE,
                            OUTPUT_RATE, PriceReviewRequired, check_price_review)
from brain.runtime_version import runtime_version


def main():
    try:
        check_price_review()
        status, action, exit_code = 'price_review_current', None, 0
    except PriceReviewRequired as error:
        status, action, exit_code = 'model_price_review_required', str(error), 2
    print(json.dumps({'status': status, 'action': action, 'model': MODEL,
                     'review_date_sgt': PRICE_DATE.isoformat(),
                     'current_date_sgt': datetime.now(ZoneInfo('Asia/Singapore')).date().isoformat(),
                     'price_source': PRICE_SOURCE,
                     'peak_micro_usd_per_million': {'input_cache_miss': INPUT_RATE, 'output': OUTPUT_RATE},
                     'runtime_version': runtime_version(),
                     'scope': 'Price readiness only; native access, budget availability and live model not tested.'}, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
