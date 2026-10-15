from datetime import timedelta
import unittest
from unittest.mock import patch
from brain.deepseek import PRICE_DATE, PriceReviewRequired, check_price_review
from brain.run_state import runtime_status
from brain.server import App
from brain.contracts import Actor


class PriceReadiness(unittest.TestCase):
    def test_runtime_reports_daily_model_pause_without_a_model_call(self):
        app=App()
        try:
            app.engine.model.name='deepseek-flash-test'
            with patch('brain.deepseek.check_price_review',side_effect=PriceReviewRequired('private detail')):
                result=runtime_status(app,Actor('eng_a'),None)
            self.assertEqual(result['model_readiness']['code'],'model_price_review_required')
            self.assertFalse(result['model_readiness']['ready'])
            self.assertNotIn('private detail',str(result))
            self.assertEqual(app.engine.model.calls,[])
        finally:app.store.db.close()

    def test_review_date_is_not_a_rolling_expiry_bypass(self):
        check_price_review(PRICE_DATE)
        with self.assertRaises(PriceReviewRequired):check_price_review(PRICE_DATE+timedelta(days=1))
