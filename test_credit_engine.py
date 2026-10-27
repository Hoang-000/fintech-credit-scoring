import unittest
from credit_engine import load_rule_config, evaluate_credit

CONFIG = load_rule_config()
BASE = {
    'age_sim': 27,
    'ekyc_verified_sim': 1,
    'identity_match_sim': 1,
    'mandatory_data_complete_sim': 1,
    'partner_eligibility_sim': 'eligible',
    'cic_group_sim': 'Nhóm 1',
    'days_past_due_sim': 0,
    'monthly_income_sim': 20_000_000,
    'current_monthly_debt_sim': 1_000_000,
    'proposed_monthly_installment_sim': 1_000_000,
    'repayment_history_score_sim': 90,
    'wallet_data_available_sim': 1,
    'monthly_txn_count_sim': 25,
}

class TestCreditRules(unittest.TestCase):
    def check(self, changes, expected, p_risk=0.07):
        row = {**BASE, **changes}
        ans = evaluate_credit(row, p_risk, CONFIG)
        self.assertEqual(ans['Decision'], expected)
        return ans

    def test_01_good_case(self):
        output = self.check({}, 'Đề xuất duyệt')
        self.assertAlmostEqual(output['DTI'], 0.1)
        self.assertGreaterEqual(output['S_final'], 80)

    def test_02_bad_cic(self):
        self.check({'cic_group_sim': 'Nhóm 4'}, 'Đề xuất từ chối theo quy tắc mô phỏng')

    def test_03_high_dti(self):
        output=self.check({'monthly_income_sim': 12_000_000, 'current_monthly_debt_sim': 8_000_000, 'proposed_monthly_installment_sim': 2_000_000}, 'Đề xuất từ chối theo quy tắc mô phỏng')
        self.assertGreaterEqual(output['DTI'], .5)

    def test_04_ekyc_failed(self):
        self.check({'ekyc_verified_sim': 0}, 'Đề xuất từ chối theo quy tắc mô phỏng')

    def test_05_partner_pending(self):
        self.check({'partner_eligibility_sim':'pending'}, 'Xem xét thêm / Chờ bổ sung thông tin')

    def test_06_higher_ai_risk_needs_review(self):
        self.check({}, 'Xem xét thêm', p_risk=.15)

    def test_07_high_ai_risk_rejected(self):
        self.check({}, 'Đề xuất từ chối theo quy tắc mô phỏng', p_risk=.30)

    def test_08_missing_mandatory_data(self):
        self.check({'mandatory_data_complete_sim':0},'Xem xét thêm / Chờ bổ sung thông tin')

if __name__=='__main__':
    unittest.main()
