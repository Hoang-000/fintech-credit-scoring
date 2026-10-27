# FINLAB CREDIT | DEMO CHẤM ĐIỂM TÍN DỤNG

**Học phần:** Công nghệ dịch vụ tài chính – Học viện Ngân hàng.

Đây là **ứng dụng nghiên cứu, mô phỏng** quy trình chấm điểm tín dụng trong bối cảnh ví điện tử. Ứng dụng **không thuộc MoMo**, không kết nối MoMo/CIC, không thực hiện eKYC hoặc giải ngân thật và không đưa ra quyết định cấp tín dụng có hiệu lực.

## Các phân hệ

1. **Tổng quan hệ thống:** 2.000 hồ sơ giả lập, thống kê kết quả, biểu đồ và bảng đối chiếu Chương 2.
2. **Tra cứu hồ sơ:** xem thông tin và các kết quả đã lưu trong CSV. `AI_p_risk` trong CSV là xác suất *lấy mẫu từ tập kiểm thử*, không phải dự báo riêng cho từng hồ sơ giả lập.
3. **Chấm điểm AI trực tiếp:** dùng `preprocessor_pipeline.joblib` và `best_credit_model.joblib`, thực thi Logistic Regression được huấn luyện trên Home Credit, sau đó áp dụng R01–R10 và điểm tổng hợp.

## Giao diện

Lấy cảm hứng từ Workspace 365: nền trắng, hồng pastel, hồng nổi bật, tím mận, thanh điều hướng trái và các thẻ dashboard bo góc. Không sao chép logo hoặc thương hiệu Workspace 365.

Màu giao diện: `#D90A63`, `#481346`, `#FBE8F0`, `#F7F6F9`.

## Cải tiến so với phiên bản trước

- **Bỏ hoàn toàn Plotly** và lỗi `ModuleNotFoundError: plotly`. Các biểu đồ dùng HTML/CSS và NumPy.
- Đọc file theo đường dẫn tương đối từ `app.py`, không dùng `/content/...` của Google Colab.
- Tách giao diện thành `ui_components.py`, phong cách thành `style.css`.
- Chọn được 5 tình huống demo; thay tình huống sẽ nạp lại dữ liệu đầu vào quy tắc.
- Hiển thị `P_risk`, `S_rule`, `S_AI`, `S_final`, `DTI` và bảng kiểm tra R01–R10.
- Không tự động gán **xác suất rủi ro giả** nếu mô hình AI bị lỗi.
- Giữ nguyên 2 file `.joblib`, CSV và file JSON do nhóm cung cấp.

## Cấu trúc để đưa lên GitHub

```text
fintech-credit-scoring/
  app.py
  credit_engine.py
  ui_components.py
  style.css
  requirements.txt
  best_credit_model.joblib
  preprocessor_pipeline.joblib
  momo_loan_simulation_results.csv
  rule_configuration.json
  .streamlit/config.toml
  tests/test_credit_engine.py
  tests/test_ui_components.py
  README.md
  DEPLOY_GITHUB_STREAMLIT.md
  CHUONG_3_KICH_BAN_DEMO.md
  TEST_REPORT.md
```

**Lưu ý:** Tất cả các file trên (ngoại trừ các file tài liệu, kiểm thử có thể để trong thư mục của chúng) phải được giữ nguyên cấu trúc. Đặc biệt `ui_components.py`, `style.css`, `credit_engine.py` và `requirements.txt` cần ở cùng cấp với `app.py`.

## Triển khai

Xem [DEPLOY_GITHUB_STREAMLIT.md](DEPLOY_GITHUB_STREAMLIT.md). **Chọn Python 3.12** trong Advanced settings khi tạo ứng dụng trên Streamlit Community Cloud. File `requirements.txt` đã cố định `scikit-learn==1.6.1` để tương thích với mô hình do nhóm xuất từ Colab.

Chạy thử trên máy có Python 3.12:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Nguyên lý chấm điểm

Theo notebook và Chương 2:

```text
S_AI    = 100 * (1 - P_risk)
S_final = 0.6 * S_rule + 0.4 * S_AI
```

Theo `rule_configuration.json`: đề xuất duyệt nếu không vi phạm điều kiện bắt buộc, `S_final ≥ 80` và `P_risk ≤ 10%`; đề xuất từ chối nếu vi phạm điều kiện loại trừ, `S_final < 60` hoặc `P_risk ≥ 25%`. Hồ sơ còn lại được đưa vào diện xem xét.

**Điểm cần thống nhất với giảng viên:** Bảng R04 ở Chương 2 có cách diễn đạt chưa nhất quán với phần mô tả quy tắc loại trừ. Phiên bản demo giữ logic của code nhóm: `ineligible` → từ chối; `pending/unknown` → xem xét thêm. Nếu nhóm đổi chính sách, cần cập nhật đồng thời báo cáo và code.

## Giới hạn thực nghiệm

- Home Credit là dữ liệu huấn luyện AI; MoMo là **bối cảnh giả định**, không phải nguồn dữ liệu huấn luyện.
- Xác suất `AI_p_risk` của 2.000 hồ sơ được lấy mẫu từ dự đoán trên tập kiểm thử Home Credit, không phải dự đoán riêng từng người dùng ví.
- Số tiền trong quy tắc nghiệp vụ dùng VNĐ giả lập. Các biến `AMT_*` của AI dùng đơn vị gốc trong tập Home Credit; không tự động quy đổi.
- Kiến trúc 6 tầng là mô hình tham chiếu; ETL được thực hiện offline trong Colab. Demo không chạy Spark, Kafka, eKYC thật hay giải ngân thật.
- Chỉ tải những file `.joblib` từ nguồn tin cậy. Định dạng pickle/joblib có thể thực thi mã khi tải.
