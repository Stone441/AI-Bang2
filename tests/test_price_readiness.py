from datetime import timedelta
import unittest
from unittest.mock import patch
from brain.deepseek import PRICE_DATE, check_price_review
from brain.run_state import runtime_status
from brain.server import App
from brain.contracts import Actor


class PriceReadiness(unittest.TestCase):
    def test_runtime_remains_ready_on_a_future_date_without_a_model_call(self):
        app=App()
        try:
            app.engine.model.name='deepseek-flash-test'
            with patch('brain.deepseek.datetime') as clock:
                clock.now.return_value.date.return_value=PRICE_DATE+timedelta(days=365)
                result=runtime_status(app,Actor('eng_a'),None)
            self.assertTrue(result['model_readiness']['ready'])
            self.assertEqual(result['model_readiness']['price_reference_date_sgt'],PRICE_DATE.isoformat())
            self.assertEqual(app.engine.model.calls,[])
        finally:app.store.db.close()

    def test_legacy_check_never_expires_by_date(self):
        for offset in (-1,0,1,365,3650):
            check_price_review(PRICE_DATE+timedelta(days=offset))
