"""Academic credit-scoring demo. The business data are simulated, not real MoMo records.

The trained estimator and preprocessing pipeline were exported from the user's
Google Colab notebook (scikit-learn 1.6.1). We use them as-is, never substitute
an invented fallback probability when inference fails.
"""
from pathlib import Path
import json
import math
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def load_rule_config(directory=ROOT):
    with open(Path(directory) / "rule_configuration.json", encoding="utf-8") as fh:
        return json.load(fh)


def load_artifacts(directory=ROOT):
    directory = Path(directory)
    pipeline = joblib.load(directory / "preprocessor_pipeline.joblib")
    model = joblib.load(directory / "best_credit_model.joblib")
    if not hasattr(pipeline, "feature_names_in_"):
        raise ValueError("Pipeline thiếu feature_names_in_; cần xuất lại từ Colab.")
    transformed_count = len(pipeline.get_feature_names_out())
    if transformed_count != model.n_features_in_:
        raise ValueError(
            f"Không khớp số chiều pipeline ({transformed_count}) và mô hình ({model.n_features_in_})."
        )
    return pipeline, model


def numeric_medians(pipeline):
    """Get the model's fitted TRAIN medians; not fabricated currency conversions."""
    fitted = pipeline.named_transformers_["num"].named_steps["imputer"]
    cols = pipeline.transformers_[0][2]
    return {k: float(v) for k, v in zip(cols, fitted.statistics_)}


def make_ai_payload(pipeline, form):
    """Build exactly the 22 Home Credit training features.

    The monetary inputs below are in the ORIGINAL Home Credit training units.
    We do not treat VND simulation amounts as having those same units.
    Unknown indicators are left NaN for training-fitted imputation.
    """
    known = {
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": form.get("code_gender", np.nan),
        "FLAG_OWN_CAR": "Y" if form.get("own_car", False) else "N",
        "FLAG_OWN_REALTY": "Y" if form.get("own_realty", True) else "N",
        "CNT_CHILDREN": int(form["children"]),
        "AMT_INCOME_TOTAL": float(form["ai_income"]),
        "AMT_CREDIT": float(form["ai_credit"]),
        "AMT_ANNUITY": float(form["ai_annuity"]),
        "DAYS_BIRTH": -round(float(form["age"]) * 365),
        "DAYS_EMPLOYED": -round(float(form["employment_years"]) * 365),
        "EXT_SOURCE_1": form.get("ext_source_1", np.nan),
        "EXT_SOURCE_2": form.get("ext_source_2", np.nan),
        "EXT_SOURCE_3": form.get("ext_source_3", np.nan),
        "BUREAU_loan_count": form.get("bureau_loans", np.nan),
        "BUREAU_active_count": form.get("bureau_active", np.nan),
        "BUREAU_debt_sum": form.get("bureau_debt", np.nan),
        "BUREAU_past_due_ratio_mean": form.get("bureau_overdue_ratio", np.nan),
        "PREV_app_count": form.get("prev_apps", np.nan),
        "PREV_approved_count": form.get("prev_approved", np.nan),
        "PREV_amt_applied_mean": form.get("prev_amt", np.nan),
        "INST_payment_count": form.get("inst_count", np.nan),
        "INST_pay_diff_mean": form.get("inst_payment_diff", np.nan),
    }
    columns = list(pipeline.feature_names_in_)
    absent = [c for c in columns if c not in known]
    if absent:
        raise ValueError(f"Thiếu các biến AI: {absent}")
    payload = pd.DataFrame([known], columns=columns)
    if payload.shape != (1, 22):
        raise ValueError("Dữ liệu AI không đúng 22 đặc trưng ban đầu.")
    return payload


def predict_risk(pipeline, model, form):
    payload = make_ai_payload(pipeline, form)
    features = pipeline.transform(payload)
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("Mô hình không có lớp rủi ro TARGET=1.")
    probs = model.predict_proba(features)
    p_risk = float(probs[0, classes.index(1)])
    if not math.isfinite(p_risk) or not (0 <= p_risk <= 1):
        raise ValueError("Xác suất AI không hợp lệ.")
    return p_risk, payload


def evaluate_credit(row, p_risk, config):
    """Rules from FINTECH.ipynb, refined to honor rule_configuration.json.

    60% S_rule + 40% S_AI. No automated real-world lending approval.
    R01-R10 are the implemented rules in the provided app; do not claim 18.
    """
    p_risk = float(p_risk)
    if not math.isfinite(p_risk) or not 0.0 <= p_risk <= 1.0:
        raise ValueError("p_risk phải trong [0,1]")
    rejections, warnings, manual_checks = [], [], []
    age_min, age_max = config["age_limits"]["min"], config["age_limits"]["max"]
    good_dti = float(config["dti_thresholds"]["good"])
    danger_dti = float(config["dti_thresholds"]["danger"])
    weights = config["score_weights"]
    thr = config["decision_thresholds"]

    age = int(row["age_sim"])
    if not age_min <= age <= age_max:
        rejections.append(f"R01: Tuổi không nằm trong khoảng {age_min}-{age_max}")
    if int(row["ekyc_verified_sim"]) == 0:
        rejections.append("R02: Chưa xác minh eKYC")
    if int(row["mandatory_data_complete_sim"]) == 0:
        manual_checks.append("R03: Thiếu dữ liệu hồ sơ bắt buộc")
    partner = row["partner_eligibility_sim"]
    if partner == "ineligible":
        rejections.append("R04: Đối tác xác định không đủ điều kiện")
    elif partner in ("pending", "unknown"):
        manual_checks.append(f"R04: Trạng thái đối tác cần xác minh ({partner})")
    if int(row["identity_match_sim"]) == 0:
        rejections.append("R05: Thông tin định danh không trùng khớp")
    cic = row["cic_group_sim"]
    if cic in ("Nhóm 3", "Nhóm 4", "Nhóm 5"):
        rejections.append(f"R06: Nhóm nợ CIC rủi ro ({cic})")
    elif cic == "Nhóm 2":
        warnings.append("R06: Nhóm nợ CIC cần lưu ý (Nhóm 2)")
    dpd = int(row["days_past_due_sim"])
    if dpd > 30:
        rejections.append(f"R07: Quá hạn {dpd} ngày (>30)")
    elif dpd > 0:
        warnings.append(f"R07: Từng quá hạn {dpd} ngày")

    income = float(row["monthly_income_sim"])
    debt = float(row["current_monthly_debt_sim"])
    installment = float(row["proposed_monthly_installment_sim"])
    if income <= 0 or debt < 0 or installment < 0:
        raise ValueError("Thu nhập phải >0; các khoản phải trả không được âm.")
    dti = (debt + installment) / income
    dti_status = "Đạt"
    if dti >= danger_dti:
        dti_status = "Nguy cơ cao"
        rejections.append(f"R08: DTI {dti:.1%} >= {danger_dti:.0%}")
    elif dti >= good_dti:
        dti_status = "Cảnh báo"
        warnings.append(f"R08: DTI {dti:.1%} >= {good_dti:.0%}")
    repayment = float(row["repayment_history_score_sim"])
    wallet_txn = int(row["monthly_txn_count_sim"])
    if repayment < 50:
        warnings.append("R09: Điểm lịch sử trả nợ dưới 50")
    if int(row["wallet_data_available_sim"]) == 1 and wallet_txn < 3:
        warnings.append("R10: Hoạt động ví dưới 3 giao dịch/tháng")

    # Original app's 5 score groups, parameterized from the supplied JSON weights.
    s_rule = (
        (weights["dpd_history"] if dpd == 0 else weights["dpd_history"] * 15 / 35 if dpd <= 15 else 0)
        + (weights["dti_ratio"] if dti < good_dti else weights["dti_ratio"] * 12 / 25 if dti < danger_dti else 0)
        + (weights["repayment_score"] if repayment >= 80 else weights["repayment_score"] / 2 if repayment >= 60 else 0)
        + (weights["income_level"] if income >= 12_000_000 else weights["income_level"] / 2 if income >= 6_000_000 else weights["income_level"] / 5)
        + (weights["wallet_activity"] if wallet_txn >= 15 else weights["wallet_activity"] / 2 if wallet_txn >= 5 else 0)
    )
    s_ai = 100 * (1 - p_risk)
    s_final = 0.6 * s_rule + 0.4 * s_ai

    if rejections:
        decision = "Đề xuất từ chối theo quy tắc mô phỏng"
        reason = "; ".join(rejections)
    elif manual_checks:
        decision = "Xem xét thêm / Chờ bổ sung thông tin"
        reason = "; ".join(manual_checks)
    elif s_final < thr["manual_review_min_score"] or p_risk >= thr["min_ai_p_risk_for_reject"]:
        decision = "Đề xuất từ chối theo quy tắc mô phỏng"
        reason = f"S_final={s_final:.1f} dưới ngưỡng, hoặc P_risk={p_risk:.1%} cao"
    elif s_final >= thr["approve_min_score"] and p_risk <= thr["max_ai_p_risk_for_approve"]:
        decision = "Đề xuất duyệt"
        reason = f"S_final={s_final:.1f} đạt ngưỡng và P_risk={p_risk:.1%} thấp"
    else:
        decision = "Xem xét thêm"
        reason = f"S_final={s_final:.1f}; P_risk={p_risk:.1%} cần kiểm tra thêm"

    return {
        "S_rule": round(float(s_rule), 2), "S_AI": round(float(s_ai), 2),
        "S_final": round(float(s_final), 2), "DTI": float(dti),
        "DTI_Status": dti_status, "Decision": decision, "Reason": reason,
        "rejections": rejections, "warnings": warnings,
        "manual_checks": manual_checks, "P_risk": p_risk,
    }
