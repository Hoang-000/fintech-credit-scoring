# BÁO CÁO KIỂM THỬ NỘI BỘ – FINLAB CREDIT V3

**Tình trạng:** Hoàn thành kiểm tra mã nguồn, dữ liệu, logic và bản dựng giao diện tham khảo. Chưa triển khai và kiểm tra trên tài khoản Streamlit Community Cloud của người dùng.

## 1. Kiểm tra các tệp

- Đã xác minh có đầy đủ `app.py`, `credit_engine.py`, `ui_components.py`, `style.css`, `requirements.txt`, hai file `.joblib`, CSV và JSON cấu hình.
- Tệp mô hình, pipeline, dữ liệu CSV và JSON được **giữ nguyên từ nhóm**; không huấn luyện lại hoặc thay đổi nội dung.
- `app.py` không còn bất kỳ lệnh `import plotly` nào. Dashboard có biểu đồ riêng bằng HTML/CSS và NumPy.
- Đường dẫn được xác định từ thư mục chứa mã nguồn, không còn phụ thuộc đường dẫn Colab `/content/...`.

## 2. Kiểm thử logic

- **12/12 bài kiểm thử tự động đạt**: gồm 8 kiểm thử R01–R10 và 4 kiểm thử giao diện/dữ liệu.
- Kiểm tra cú pháp `app.py`, `credit_engine.py`, `ui_components.py`: thành công.
- Chạy kiểm tra mô phỏng 3 phân hệ bằng Streamlit stub: không phát hiện lỗi luồng mã nguồn.

## 3. Kiểm thử mô hình với dữ liệu mẫu

- Đầu vào mô hình: **22 đặc trưng Home Credit**.
- Sau tiền xử lý: **27 đặc trưng**.
- Mô hình: **Logistic Regression**, dự đoán lớp rủi ro `TARGET=1`.
- Hồ sơ AI mặc định (dùng trung vị đã lưu trong pipeline): `P_risk` khoảng **7,36%** ở môi trường kiểm tra.
- Kiểm thử năm kịch bản: TC01 đề xuất duyệt; TC02 từ chối do CIC; TC03 từ chối do DTI; TC04 từ chối do eKYC; TC05 yêu cầu xem xét thêm.

**Giới hạn của kiểm thử mô hình:** Môi trường thử nghiệm tại đây có scikit-learn phiên bản mới hơn 1.6.1, nên đã sử dụng thủ thuật tương thích *chỉ trong script kiểm thử* để đọc pipeline cũ. Thủ thuật đó **không được đưa vào mã triển khai**. Bản triển khai yêu cầu Python 3.12 và `scikit-learn==1.6.1` nhằm sử dụng đúng phiên bản gốc.

## 4. Kiểm tra dữ liệu tĩnh

- Số hồ sơ: **2.000**.
- Đề xuất duyệt: **740 (37,0%)**.
- Đề xuất từ chối: **1.014 (50,7%)**.
- Xem xét thêm: **246 (12,3%)** – gồm 124 chờ bổ sung và 122 xem xét thêm.
- Phân bổ này nhất quán với số liệu của Chương 2.

## 5. Kiểm tra giao diện

- Đã kiểm tra bản xem trước tĩnh của các thành phần UI bằng trình duyệt Chromium: màu hồng – tím mận – trắng, menu trái, thẻ KPI, biểu đồ donut và histogram hiển thị rõ.
- Ảnh minh họa là **bản dựng các thành phần**, không phải ảnh chụp toàn bộ ứng dụng Streamlit đã triển khai.
- Do môi trường kiểm thử không cài được Streamlit từ kho thư viện, **chưa thể xác nhận tương tác đồ họa thực tế** trên Streamlit Cloud. Người triển khai cần chạy checklist trong `DEPLOY_GITHUB_STREAMLIT.md`.

## 6. Lưu ý về nội dung học thuật

Ứng dụng là mô phỏng. `P_risk` của 2.000 hồ sơ trong CSV được lấy mẫu từ tập kiểm thử Home Credit, không phải dự đoán thực hiện cho từng hồ sơ MoMo. Chức năng hồ sơ mới mới thực thi mô hình AI trực tiếp. Không có kết nối với hệ thống cho vay, CIC hoặc MoMo thực tế.
