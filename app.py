"""FinLab Credit: simulated AI + rule-based credit scoring (educational demo).

Run: streamlit run app.py
Python: 3.12 (required for the pinned scikit-learn training artifacts).
No Plotly dependency, external API, real MoMo/CIC data, or model-probability fallback.
"""
import json
import numpy as np
import pandas as pd
import streamlit as st

from credit_engine import (
    ROOT, load_artifacts, load_rule_config, numeric_medians,
    predict_risk, evaluate_credit,
)
from ui_components import (
    brand, hero, page_heading, metric_tile, decision_distribution,
    score_histogram, decision_banner, score_ring, workflow_steps,
    disclaimer, footer,
)

st.set_page_config(
    page_title="FinLab Credit | Demo AI & Big Data",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_file = ROOT / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

PAGES = (
    "Tổng quan hệ thống",
    "Tra cứu hồ sơ",
    "Chấm điểm AI trực tiếp",
)

EXPECTED = {
    "Đề xuất duyệt": 740,
    "Đề xuất từ chối theo quy tắc mô phỏng": 1014,
    "Xem xét thêm / Chờ bổ sung thông tin": 124,
    "Xem xét thêm": 122,
}

SCENARIOS = {
    "TC01 · Đạt điều kiện quy tắc": {
        "f_age": 27, "f_ekyc": True, "f_partner": "eligible", "f_cic": "Nhóm 1",
        "f_dpd": 0, "f_income": 20_000_000, "f_debt": 1_000_000, "f_inst": 1_000_000,
        "f_repay": 90, "f_wallet_txn": 25,
    },
    "TC02 · Nợ xấu CIC Nhóm 4": {
        "f_age": 27, "f_ekyc": True, "f_partner": "eligible", "f_cic": "Nhóm 4",
        "f_dpd": 0, "f_income": 20_000_000, "f_debt": 1_000_000, "f_inst": 1_000_000,
        "f_repay": 90, "f_wallet_txn": 25,
    },
    "TC03 · DTI vượt 50%": {
        "f_age": 27, "f_ekyc": True, "f_partner": "eligible", "f_cic": "Nhóm 1",
        "f_dpd": 0, "f_income": 12_000_000, "f_debt": 8_000_000, "f_inst": 2_000_000,
        "f_repay": 90, "f_wallet_txn": 25,
    },
    "TC04 · Chưa xác minh eKYC": {
        "f_age": 27, "f_ekyc": False, "f_partner": "eligible", "f_cic": "Nhóm 1",
        "f_dpd": 0, "f_income": 20_000_000, "f_debt": 1_000_000, "f_inst": 1_000_000,
        "f_repay": 90, "f_wallet_txn": 25,
    },
    "TC05 · Đối tác chưa xác minh": {
        "f_age": 27, "f_ekyc": True, "f_partner": "pending", "f_cic": "Nhóm 1",
        "f_dpd": 0, "f_income": 20_000_000, "f_debt": 1_000_000, "f_inst": 1_000_000,
        "f_repay": 90, "f_wallet_txn": 25,
    },
}


@st.cache_data(show_spinner=False)
def get_data():
    df = pd.read_csv(ROOT / "momo_loan_simulation_results.csv")
    required = set([
        "momo_customer_id", "age_sim", "ekyc_verified_sim", "identity_match_sim",
        "cic_group_sim", "monthly_income_sim", "current_monthly_debt_sim",
        "proposed_monthly_installment_sim", "DTI", "S_rule", "S_AI",
        "S_final", "AI_p_risk", "Decision", "Reason", "monthly_txn_count_sim",
    ])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError("Tệp CSV thiếu cột: " + ", ".join(missing))
    if df.empty:
        raise ValueError("Tệp CSV không có hồ sơ nào.")
    return df


@st.cache_data(show_spinner=False)
def get_rules():
    return load_rule_config(ROOT)


@st.cache_resource(show_spinner="Đang tải mô hình Logistic Regression...")
def get_ai_resources():
    pipeline, model = load_artifacts(ROOT)
    return pipeline, model, numeric_medians(pipeline)


def set_page(page):
    st.session_state["navigation"] = page


def inject_sidebar():
    with st.sidebar:
        st.markdown(brand(), unsafe_allow_html=True)
        st.markdown('<div class="w365-small-title">Không gian làm việc</div>',
                    unsafe_allow_html=True)
        if "navigation" not in st.session_state:
            st.session_state["navigation"] = PAGES[0]
        page = st.radio("Phân hệ", PAGES, key="navigation", label_visibility="collapsed")
        st.markdown('<div class="w365-small-title" style="margin-top:28px">Trạng thái dự án</div>',
                    unsafe_allow_html=True)
        st.markdown('''<div class="w365-side-note"><b>● Bản nghiên cứu học thuật</b><br>
        2.000 hồ sơ mô phỏng<br>R01–R10 · Logistic Regression<br>
        <span style="font-size:.72rem">Không kết nối hệ thống MoMo hoặc CIC thực tế.</span>
        </div>''', unsafe_allow_html=True)
        st.caption("Học phần Công nghệ dịch vụ tài chính · Học viện Ngân hàng")
    return page


def render_intro():
    st.markdown(hero(
        "Chấm điểm tín dụng, trực quan và minh bạch.",
    ), unsafe_allow_html=True)


def render_footer():
    st.markdown(footer(), unsafe_allow_html=True)


def render_dashboard():
    st.markdown(page_heading(
        "Tổng quan hệ thống",
        "Phân tích kết quả 2.000 hồ sơ và khám phá các phân hệ thử nghiệm.",
        "DỮ LIỆU GIẢ LẬP",
    ), unsafe_allow_html=True)
    try:
        df=get_data()
    except Exception as exc:
        st.error("Không thể đọc dữ liệu mô phỏng. Hãy kiểm tra file CSV tại thư mục gốc.")
        st.exception(exc)
        st.stop()
    n=len(df)
    counts=df["Decision"].value_counts()
    n_ok=int(counts.get("Đề xuất duyệt",0))
    n_no=int(counts.get("Đề xuất từ chối theo quy tắc mô phỏng",0))
    n_review=n-n_ok-n_no
    cols=st.columns(4)
    tiles=[
        ("Tổng hồ sơ",f"{n:,}","Bộ kết quả MoMo giả lập","▦"),
        ("Đề xuất duyệt",f"{n_ok:,}",f"{n_ok/n:.1%} tổng hồ sơ","✓"),
        ("Cần xem xét",f"{n_review:,}",f"{n_review/n:.1%} tổng hồ sơ","↻"),
        ("Đề xuất từ chối",f"{n_no:,}",f"{n_no/n:.1%} tổng hồ sơ","!"),
    ]
    for col,fields in zip(cols,tiles):
        with col:
            st.markdown(metric_tile(*fields),unsafe_allow_html=True)
    st.write("")
    left,right=st.columns([1,1],gap="medium")
    with left:
        st.markdown(decision_distribution(counts),unsafe_allow_html=True)
    with right:
        st.markdown(score_histogram(pd.to_numeric(df["S_final"],errors="coerce")),
                    unsafe_allow_html=True)

    st.markdown('<div class="w365-kicker" style="margin-top:12px">LỐI TẮT CÔNG VIỆC</div>',
                unsafe_allow_html=True)
    c1,c2,c3=st.columns([1,1,1])
    with c1:
        st.button("🔎  Tra cứu khách hàng", use_container_width=True,
                  on_click=set_page, args=(PAGES[1],))
    with c2:
        st.button("✨  Chấm điểm AI mới", type="primary", use_container_width=True,
                  on_click=set_page, args=(PAGES[2],))
    with c3:
        st.download_button("⬇  Tải kết quả CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           file_name="momo_loan_simulation_results.csv", mime="text/csv",
                           use_container_width=True)

    st.markdown("### Đối chiếu kết quả với Chương 2")
    check = pd.DataFrame([
        {
            "Kết quả mô phỏng":key,
            "Chương 2 (hồ sơ)":expected,
            "CSV (hồ sơ)":int(counts.get(key,0)),
            "Đối chiếu":"Khớp" if int(counts.get(key,0))==expected else "Khác",
        }
        for key,expected in EXPECTED.items()
    ])
    st.dataframe(check, hide_index=True, use_container_width=True)
    st.markdown(disclaimer(
        "Lưu ý nghiên cứu: các xác suất AI trong 2.000 hồ sơ là giá trị được lấy mẫu từ dự đoán trên tập kiểm thử; KHÔNG phải dự đoán riêng cho từng người dùng. Kết quả được giữ nguyên như dữ liệu gốc."
    ),unsafe_allow_html=True)

    with st.expander("Kiến trúc 6 tầng theo mục 2.2.1 của báo cáo"):
        st.markdown('''| Tầng | Thành phần trong nghiên cứu và demo |
|---|---|
| 1. Giao diện | Streamlit: Dashboard, tra cứu và nhập hồ sơ mới |
| 2. Nguồn dữ liệu | 5 bảng và 2.000 hồ sơ giả lập |
| 3. ETL / Big Data | Làm sạch, ghép dữ liệu theo SK_ID_CURR trong Colab (offline) |
| 4. Tiền xử lý | SimpleImputer, StandardScaler, OneHotEncoder trong pipeline |
| 5. AI & quy tắc | Logistic Regression, R01–R10, điểm S_final |
| 6. Giải ngân & giám sát | Chưa triển khai, chỉ mô tả theo quy trình nghiệp vụ |''')
        st.caption("Demo không vận hành Kafka, Spark hay kho dữ liệu lớn trực tuyến.")
    st.markdown("### Danh sách hồ sơ mô phỏng")
    cols=["momo_customer_id","age_sim","monthly_income_sim","DTI",
          "S_rule","S_AI","S_final","Decision"]
    st.dataframe(df[cols],use_container_width=True,hide_index=True,height=350)


def render_customer_lookup():
    st.markdown(page_heading(
        "Tra cứu hồ sơ khách hàng",
        "Xem kết quả đã được tính và lưu từ dữ liệu mô phỏng; không chạy lại AI tại trang này.",
        "KẾT QUẢ LƯU SẴN",
    ), unsafe_allow_html=True)
    try:
        df=get_data()
    except Exception as exc:
        st.error("Không mở được dữ liệu giả lập.")
        st.exception(exc)
        st.stop()
    c1,c2=st.columns([1,2],gap="small")
    with c1:
        label_filter=st.selectbox("Lọc theo kết quả",[
            "Tất cả kết quả", "Đề xuất duyệt", "Xem xét thêm",
            "Đề xuất từ chối theo quy tắc mô phỏng",
        ])
    if label_filter=="Tất cả kết quả":
        filtered=df
    elif label_filter=="Xem xét thêm":
        filtered=df[df["Decision"].str.startswith("Xem xét thêm")]
    else:
        filtered=df[df["Decision"]==label_filter]
    with c2:
        cust_id=st.selectbox("Chọn mã hồ sơ giả lập",filtered["momo_customer_id"].tolist())
    row=filtered.loc[filtered["momo_customer_id"]==cust_id].iloc[0]

    st.markdown(disclaimer(
        "Các bản ghi trong phân hệ này là hồ sơ giả lập. P_risk được gán bằng cách lấy mẫu từ phân bố dự đoán; không phải dự đoán cá nhân cho hồ sơ đang tra cứu."
    ),unsafe_allow_html=True)
    l,r=st.columns([1.1,1],gap="medium")
    with l:
        st.markdown("### Thông tin hồ sơ")
        details=pd.DataFrame([
            ("Mã hồ sơ",row["momo_customer_id"]),
            ("Tuổi",f"{int(row['age_sim'])} tuổi"),
            ("eKYC","Đã xác minh" if row["ekyc_verified_sim"] else "Chưa xác minh"),
            ("Khớp định danh","Trùng khớp" if row["identity_match_sim"] else "Không khớp"),
            ("Nhóm nợ CIC",row["cic_group_sim"]),
            ("Thu nhập hàng tháng",f"{row['monthly_income_sim']:,.0f} VNĐ"),
            ("Tổng nghĩa vụ trả nợ",f"{row['current_monthly_debt_sim']+row['proposed_monthly_installment_sim']:,.0f} VNĐ"),
            ("Tỷ lệ DTI",f"{row['DTI']:.1%}"),
            ("Số giao dịch ví/tháng",f"{int(row['monthly_txn_count_sim'])}"),
        ],columns=["Chỉ tiêu","Giá trị"])
        st.dataframe(details,hide_index=True,use_container_width=True,height=350)
    with r:
        st.markdown("### Kết quả đã lưu")
        st.markdown(decision_banner(row["Decision"],row["Reason"]),unsafe_allow_html=True)
        st.markdown(score_ring(row["S_final"]),unsafe_allow_html=True)
        x,y,z=st.columns(3)
        x.metric("S_rule",f"{row['S_rule']:.1f}")
        y.metric("S_AI",f"{row['S_AI']:.1f}")
        z.metric("P_risk lấy mẫu",f"{row['AI_p_risk']:.1%}")


def initialize_form(medians):
    if "scenario" not in st.session_state:
        st.session_state["scenario"] = list(SCENARIOS)[0]
    defaults = {
        "f_age":27, "f_ekyc":True, "f_id_match":True, "f_mandatory":True,
        "f_partner":"eligible", "f_cic":"Nhóm 1", "f_dpd":0,
        "f_income":20_000_000, "f_debt":1_000_000, "f_inst":1_000_000,
        "f_repay":90, "f_has_wallet":True, "f_wallet_txn":25,
        "ai_income":float(medians["AMT_INCOME_TOTAL"]),
        "ai_credit":float(medians["AMT_CREDIT"]),
        "ai_annuity":float(medians["AMT_ANNUITY"]),
        "ai_employment":5.0, "ai_children":0,
        "ai_gender":"Không cung cấp", "ai_car":False, "ai_realty":True,
        "ai_ext_enabled":False, "ai_ext1":0.5,"ai_ext2":0.5,"ai_ext3":0.5,
    }
    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key]=value


def scenario_changed():
    for k,v in SCENARIOS[st.session_state["scenario"]].items():
        st.session_state[k]=v
    st.session_state.pop("latest_evaluation",None)


def audit_rules(result):
    rows=[]
    for code,label in [
        ("R01","Giới hạn tuổi"),("R02","eKYC"),("R03","Đủ dữ liệu bắt buộc"),
        ("R04","Điều kiện đối tác"),("R05","Khớp định danh"),
        ("R06","Nhóm nợ CIC"),("R07","Ngày quá hạn"),
        ("R08","Tỷ lệ DTI"),("R09","Lịch sử trả nợ"),
        ("R10","Hoạt động ví"),
    ]:
        status="Đạt"; detail="Không có vi phạm"
        for field,new_status in (("rejections","Từ chối"),
                                 ("manual_checks","Cần kiểm tra"),
                                 ("warnings","Cảnh báo")):
            matched=[m for m in result[field] if str(m).startswith(code+":")]
            if matched:
                status=new_status
                detail="; ".join(matched)
                break
        rows.append({"Mã":code,"Nhóm quy tắc":label,"Trạng thái":status,"Giải thích":detail})
    return pd.DataFrame(rows)


def render_new_scoring():
    st.markdown(page_heading(
        "Chấm điểm tín dụng trực tiếp",
        "AI THỰC THI · MÔ PHỎNG NGHIỆP VỤ",
    ),unsafe_allow_html=True)
    st.markdown(workflow_steps(),unsafe_allow_html=True)
    try:
        pipeline, model, medians=get_ai_resources()
        config=get_rules()
    except Exception as exc:
        st.error("Không thể tải mô hình AI. Ứng dụng sẽ không tự tạo xác suất rủi ro giả.")
        with st.expander("Xem chi tiết lỗi và cách xử lý"):
            st.exception(exc)
            st.code("scikit-learn==1.6.1\nPython 3.12",language="text")
            st.caption("Hãy kiểm tra hai file .joblib và dependencies trong requirements.txt.")
        st.stop()

    st.markdown(disclaimer(
        "Đây là mô hình nghiên cứu: phần điều kiện tín dụng dùng VNĐ giả lập; phần AI dùng đơn vị gốc của dữ liệu. Hai nhóm giá trị tiền được nhập riêng, không tự động đổi đơn vị. Kết quả chỉ hỗ trợ minh họa ra quyết định, không có giá trị phê duyệt khoản vay thực tế."
    ),unsafe_allow_html=True)

    initialize_form(medians)
    st.selectbox("Chọn kịch bản thử nghiệm của Chương 3",list(SCENARIOS),
                 key="scenario",on_change=scenario_changed)

    with st.form("credit_form",clear_on_submit=False):
        st.markdown("### A. Hồ sơ nghiệp vụ (đơn vị VNĐ giả lập)")
        left,right=st.columns(2,gap="large")
        with left:
            age=st.slider("Tuổi khách hàng",16,65,key="f_age")
            ekyc=st.checkbox("Đã hoàn thành xác minh eKYC",key="f_ekyc")
            id_match=st.checkbox("Thông tin định danh trùng khớp",key="f_id_match")
            mandatory=st.checkbox("Đã cung cấp đủ dữ liệu bắt buộc",key="f_mandatory")
            partner=st.selectbox("Trạng thái từ đối tác cho vay",
                                 ["eligible","pending","ineligible","unknown"],key="f_partner")
            cic=st.selectbox("Nhóm nợ CIC giả lập",
                             ["Nhóm 1","Nhóm 2","Nhóm 3","Nhóm 4","Nhóm 5","Không có lịch sử"],key="f_cic")
            dpd=st.selectbox("Số ngày quá hạn (DPD)",[0,5,15,30,45,90],key="f_dpd")
        with right:
            income=st.number_input("Thu nhập/tháng (VNĐ)",min_value=100_000,max_value=200_000_000,
                                   step=500_000,key="f_income")
            debt=st.number_input("Nợ phải trả hiện tại/tháng (VNĐ)",min_value=0,max_value=150_000_000,
                                 step=500_000,key="f_debt")
            inst=st.number_input("Trả góp dự kiến/tháng (VNĐ)",min_value=0,max_value=150_000_000,
                                 step=500_000,key="f_inst")
            repay=st.slider("Điểm lịch sử trả nợ giả lập",0,100,key="f_repay")
            has_wallet=st.checkbox("Có dữ liệu hoạt động ví",key="f_has_wallet")
            wallet_txn=st.slider("Số giao dịch ví mỗi tháng",0,120,key="f_wallet_txn")

        st.divider()
        st.markdown("### B. Dữ liệu đầu vào AI")
        st.caption("Giá trị mặc định của AMT_* lấy từ trung vị tập huấn luyện đã lưu trong pipeline; không phải quy đổi từ VNĐ.")
        a,b,c=st.columns(3)
        with a:
            ai_income=st.number_input("AMT_INCOME_TOTAL",min_value=0.0,step=10_000.0,key="ai_income")
        with b:
            ai_credit=st.number_input("AMT_CREDIT",min_value=0.0,step=10_000.0,key="ai_credit")
        with c:
            ai_annuity=st.number_input("AMT_ANNUITY",min_value=0.0,step=1_000.0,key="ai_annuity")
        with st.expander("Đặc trưng Home Credit nâng cao (không bắt buộc)"):
            x,y,z=st.columns(3)
            with x:
                employment=st.number_input("Số năm làm việc",min_value=0.0,max_value=45.0,
                                           step=0.5,key="ai_employment")
            with y:
                children=st.number_input("CNT_CHILDREN",min_value=0,max_value=15,key="ai_children")
            with z:
                gender=st.selectbox("CODE_GENDER",["Không cung cấp","F","M"],key="ai_gender")
            car=st.checkbox("FLAG_OWN_CAR: Có xe",key="ai_car")
            realty=st.checkbox("FLAG_OWN_REALTY: Có bất động sản",key="ai_realty")
            enabled=st.checkbox("Sử dụng 3 giá trị EXT_SOURCE (nếu có)",key="ai_ext_enabled")
            s1,s2,s3=st.columns(3)
            with s1:
                ext1=st.slider("EXT_SOURCE_1",0.0,1.0,step=0.01,key="ai_ext1")
            with s2:
                ext2=st.slider("EXT_SOURCE_2",0.0,1.0,step=0.01,key="ai_ext2")
            with s3:
                ext3=st.slider("EXT_SOURCE_3",0.0,1.0,step=0.01,key="ai_ext3")
            st.caption("Các đặc trưng không được cung cấp sẽ dùng phép điền khuyết đã học trên dữ liệu Train.")
        submitted=st.form_submit_button("✨  Chạy mô hình AI & chấm điểm tín dụng",
                                        type="primary",use_container_width=True)

    if submitted:
        ai_form={
            "age":age,"children":children,"employment_years":employment,
            "code_gender": np.nan if gender=="Không cung cấp" else gender,
            "own_car":car,"own_realty":realty,
            "ai_income":ai_income,"ai_credit":ai_credit,"ai_annuity":ai_annuity,
            "ext_source_1":ext1 if enabled else np.nan,
            "ext_source_2":ext2 if enabled else np.nan,
            "ext_source_3":ext3 if enabled else np.nan,
        }
        business_row={
            "age_sim":age,"ekyc_verified_sim":int(ekyc),"identity_match_sim":int(id_match),
            "mandatory_data_complete_sim":int(mandatory),"partner_eligibility_sim":partner,
            "cic_group_sim":cic,"days_past_due_sim":dpd,
            "monthly_income_sim":float(income),"current_monthly_debt_sim":float(debt),
            "proposed_monthly_installment_sim":float(inst),
            "repayment_history_score_sim":repay,"wallet_data_available_sim":int(has_wallet),
            "monthly_txn_count_sim":wallet_txn,
        }
        try:
            p_risk,payload=predict_risk(pipeline,model,ai_form)
            result=evaluate_credit(business_row,p_risk,config)
            st.session_state["latest_evaluation"]={
                "scenario":st.session_state["scenario"],
                "p_risk":p_risk,"result":result,"input":business_row,
            }
        except Exception as exc:
            st.session_state.pop("latest_evaluation",None)
            st.error("Không thể thực hiện dự đoán. Hệ thống KHÔNG thay thế bằng giá trị AI giả.")
            with st.expander("Chi tiết lỗi kỹ thuật"):
                st.exception(exc)

    current=st.session_state.get("latest_evaluation")
    if current:
        result=current["result"]
        p_risk=current["p_risk"]
        st.divider()
        st.markdown(page_heading(
            "Kết quả đánh giá hồ sơ",
            "Dự đoán vừa chạy trên mô hình được lưu từ Google Colab, sau đó áp dụng các quy tắc học thuật.",
            current["scenario"],
        ),unsafe_allow_html=True)
        st.markdown(decision_banner(result["Decision"],result["Reason"]),
                    unsafe_allow_html=True)
        st.caption("Kết quả của lần chấm điểm gần nhất. Sau khi chỉnh sửa thông tin, hãy nhấn chấm điểm lại.")
        x,y,z,t=st.columns(4)
        x.metric("P_risk (Home Credit)",f"{p_risk:.2%}")
        y.metric("S_rule",f"{result['S_rule']:.1f} / 100")
        z.metric("S_AI",f"{result['S_AI']:.1f} / 100")
        t.metric("S_final",f"{result['S_final']:.1f} / 100")
        l,r=st.columns([1,1],gap="medium")
        with l:
            st.markdown(score_ring(result["S_final"]),unsafe_allow_html=True)
            st.metric("DTI – Tỷ lệ nghĩa vụ trả nợ",f"{result['DTI']:.1%}")
        with r:
            st.markdown("#### Công thức và ngưỡng quyết định")
            st.latex(r"S_{AI}=100\times(1-P_{risk})")
            st.latex(r"S_{final}=0.6\times S_{rule}+0.4\times S_{AI}")
            st.caption("Theo file rule_configuration.json: duyệt khi điểm ≥80 và P_risk ≤10%, cùng các điều kiện bắt buộc; từ chối nếu P_risk ≥25% hoặc điểm <60.")
        with st.expander("Chi tiết 10 quy tắc nghiệp vụ R01–R10",expanded=True):
            st.dataframe(audit_rules(result),hide_index=True,use_container_width=True)
        export={
            "scenario":current["scenario"],"study":"Home Credit + MoMo synthetic",
            "p_risk":round(p_risk,6),
            "S_rule":result["S_rule"],"S_AI":result["S_AI"],
            "S_final":result["S_final"],"DTI":round(result["DTI"],6),
            "Decision":result["Decision"],"Reason":result["Reason"],
            "rule_rejections":result["rejections"],
            "rule_warnings":result["warnings"],
            "rule_manual_checks":result["manual_checks"],
        }
        st.download_button("⬇  Tải báo cáo kết quả hồ sơ (JSON)",
                           data=json.dumps(export,ensure_ascii=False,indent=2),
                           file_name="finlab_credit_evaluation.json",mime="application/json")
    else:
        st.markdown(disclaimer(
            "Nhấn nút chấm điểm để chạy mô hình Logistic Regression. Nếu mô hình không tương thích thư viện, ứng dụng sẽ hiển thị lỗi, không tạo xác suất rủi ro giả."
        ),unsafe_allow_html=True)


render_intro()
page=inject_sidebar()
if page==PAGES[0]:
    render_dashboard()
elif page==PAGES[1]:
    render_customer_lookup()
else:
    render_new_scoring()
render_footer()
