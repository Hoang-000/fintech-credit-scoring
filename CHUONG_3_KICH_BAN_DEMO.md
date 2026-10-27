# CHƯƠNG 3 – HƯỚNG DẪN DEMO VÀ VIẾT PHẦN THỬ NGHIỆM

## 3.1. Thử nghiệm/Demo thực tế

### 3.1.1. Mục tiêu thử nghiệm

Thử nghiệm nhằm minh họa quy trình tiếp nhận, phân tích và hỗ trợ xét duyệt hồ sơ; kiểm tra khả năng thực thi mô hình Logistic Regression đã huấn luyện; kiểm tra bộ quy tắc R01–R10, công thức tính điểm và phân loại hồ sơ; đồng thời đánh giá khả năng tra cứu và trình bày dữ liệu mô phỏng trên giao diện Streamlit.

### 3.1.2. Môi trường và nguồn dữ liệu

- **Huấn luyện:** Google Colab; mô hình Logistic Regression và pipeline tiền xử lý xuất thành hai file `.joblib`.
- **Ứng dụng:** Streamlit, Python 3.12, scikit-learn 1.6.1.
- **Dữ liệu:** 5 bảng Home Credit đã được xử lý trong Colab; 2.000 hồ sơ MoMo **giả lập** trong CSV.
- **Giới hạn:** Không kết nối MoMo/CIC thật; không thực hiện eKYC, ký số hoặc giải ngân thực tế.

### 3.1.3. Kịch bản thử nghiệm

**Màn hình 1 – Dashboard:** Hiển thị 2.000 hồ sơ, gồm 740 đề xuất duyệt (37,0%), 1.014 đề xuất từ chối (50,7%) và 246 xem xét thêm (12,3%). Mở bảng đối chiếu kết quả Chương 2 và chụp ảnh.

**Màn hình 2 – Tra cứu:** Lọc trạng thái, chọn mã hồ sơ và xem điểm `S_rule`, `S_AI`, `S_final`, tỷ lệ DTI cùng lý do. Đây là kết quả đã lưu, không chạy lại mô hình riêng cho hồ sơ này.

**Màn hình 3 – Chấm điểm trực tiếp:** Chọn TC01–TC05, nhấn **Chạy mô hình AI & chấm điểm tín dụng**, xem `P_risk`, `S_rule`, `S_AI`, `S_final` và từng quy tắc.

| Kịch bản | Thông tin thay đổi | Kết quả kỳ vọng |
|---|---|---|
| TC01 | 27 tuổi; hoàn thành eKYC; CIC Nhóm 1; DTI 10% | Đề xuất duyệt nếu AI cũng đạt ngưỡng |
| TC02 | CIC Nhóm 4 | Đề xuất từ chối – R06 |
| TC03 | Nghĩa vụ trả nợ 10 triệu / thu nhập 12 triệu | Đề xuất từ chối – R08; DTI 83,3% |
| TC04 | Chưa hoàn thành eKYC | Đề xuất từ chối – R02 |
| TC05 | Trạng thái đối tác `pending` | Xem xét thêm – R04 |

### 3.1.4. Đánh giá kết quả

Sau khi triển khai trên Streamlit Cloud, chụp ảnh giao diện tổng quan, tra cứu và từng kịch bản, sau đó lập bảng: *mã kịch bản – dữ liệu thay đổi – P_risk – điểm tổng hợp – quyết định – ảnh minh chứng*. **Không tự đặt xác suất AI**; lấy trực tiếp kết quả hiển thị trên ứng dụng.

Trong quá trình kiểm thử mã nguồn, 8/8 bài kiểm thử logic đạt yêu cầu. Mức độ hoạt động trên tài khoản Streamlit Cloud cần được nhóm xác nhận qua bản deploy thực tế.

## 3.2. Đề xuất, khuyến nghị và ý tưởng cải tiến

**Thứ nhất, nâng cao chất lượng và tính phù hợp của dữ liệu.** Mô hình được huấn luyện trên Home Credit, không phải dữ liệu MoMo; cần dữ liệu đại diện, được thu thập hợp pháp và quy trình đánh giá phù hợp với bối cảnh triển khai.

**Thứ hai, đồng nhất đơn vị và cấu trúc đầu vào.** Hiện tại bộ quy tắc xử lý số tiền VNĐ giả lập, còn mô hình sử dụng giá trị `AMT_*` từ Home Credit. Trước khi áp dụng thực tế phải thiết lập phương pháp chuyển đổi, kiểm tra sự tương thích của các biến và huấn luyện/hiệu chỉnh mô hình phù hợp.

**Thứ ba, tăng tính minh bạch.** Duy trì bảng kiểm tra R01–R10; có thể nghiên cứu SHAP hoặc phương pháp giải thích phù hợp để phân tích ảnh hưởng của đặc trưng đối với mô hình.

**Thứ tư, hoàn thiện quản trị rủi ro.** Tăng cường kiểm tra gian lận, bảo vệ dữ liệu cá nhân, phân quyền, lưu vết, kiểm tra khả năng thiên lệch và giám sát chất lượng dự đoán.

**Thứ năm, nâng cấp hạ tầng dữ liệu.** Hệ thống hiện minh họa ETL offline trong Colab. Có thể nghiên cứu Spark, Kafka hoặc kho đặc trưng khi có khối lượng dữ liệu và nguồn lực triển khai phù hợp; không trình bày các công nghệ này như những thành phần đã chạy thật.

**Thứ sáu, đánh giá mô hình trước khi mở rộng.** Theo dõi ROC-AUC, PR-AUC, khả năng hiệu chỉnh xác suất, sai lệch theo nhóm khách hàng và chất lượng vận hành. Chỉ công bố kết quả đo đã được kiểm chứng.

## Ghi nhớ khi bảo vệ

- `S_AI = 100 × (1 − P_risk)`.
- `S_final = 0,6 × S_rule + 0,4 × S_AI`.
- Dashboard dùng **xác suất lấy mẫu**; chức năng chấm điểm hồ sơ mới mới chạy AI trực tiếp.
- Quyết định tín dụng thật thuộc về tổ chức cho vay có thẩm quyền.
- Mô hình 6 tầng ở Chương 2 có các tầng nghiệp vụ chưa triển khai trong demo, đặc biệt giải ngân và giám sát thực tế.
