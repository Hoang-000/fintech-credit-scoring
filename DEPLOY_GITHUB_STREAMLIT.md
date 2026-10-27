# HƯỚNG DẪN CẬP NHẬT GITHUB VÀ TRIỂN KHAI STREAMLIT

## A. Cập nhật repository `fintech-credit-scoring` đang có

**Không chỉ thay `app.py`!** Phiên bản mới có thêm `ui_components.py` và `style.css`.

1. Tải bản ZIP hoàn chỉnh, nhấp chuột phải và chọn **Extract All / Giải nén**.
2. Mở GitHub, vào repository `fintech-credit-scoring` mà bạn đang sử dụng.
3. Chọn **Add file → Upload files**. Kéo các file **bên trong thư mục giải nén** vào thư mục gốc của repository (không tải riêng file ZIP và không để mọi thứ nằm trong thư mục con).
4. Đảm bảo các file sau nằm **cùng cấp**: `app.py`, `credit_engine.py`, `ui_components.py`, `style.css`, `requirements.txt`, hai file `.joblib`, file `.csv` và file `.json`.
5. Chọn **Commit changes** để lưu thay đổi.
6. Nếu `.streamlit/config.toml` không tải lên được do Windows ẩn thư mục dấu chấm, trên GitHub chọn **Add file → Create new file**, đặt tên `.streamlit/config.toml`, sao chép nội dung từ file mẫu và Commit.
7. Quay lại Streamlit Cloud, chọn **Manage app**. Kiểm tra Logs và chọn **Reboot app** nếu ứng dụng chưa tự cập nhật. Việc sửa `requirements.txt` sẽ kích hoạt cài lại thư viện.

## B. Triển khai ứng dụng mới (nếu cần thay Python)

1. Truy cập [share.streamlit.io](https://share.streamlit.io) và đăng nhập bằng GitHub.
2. Chọn **Create app → Yup, I have an app**.
3. Repository: `fintech-credit-scoring`; Branch: `main`; Main file path: `app.py`.
4. Chọn **Advanced settings → Python 3.12 → Save**.
5. Nhấn **Deploy**, mở link `.streamlit.app` của bạn.

**Quan trọng:** Theo tài liệu Streamlit, sau khi ứng dụng đã deploy, phiên bản Python của ứng dụng đó không thể thay đổi trực tiếp. Nếu ứng dụng cũ đang ở Python 3.13/3.14 và không tương thích với mô hình scikit-learn đã lưu, bạn cần ghi lại URL, **xóa ứng dụng trên Streamlit Cloud rồi tạo lại** với Python 3.12. Không cần xóa repository GitHub.

## C. Kiểm tra file `requirements.txt`

File phải nằm cùng cấp `app.py`:

```text
streamlit==1.50.0
pandas>=2.2.3,<3.0
numpy>=1.26.4,<2.0
scikit-learn==1.6.1
joblib>=1.4.2,<2.0
```

Phiên bản này **không cần Plotly**.

## D. Kiểm tra sau khi deploy

- [ ] Dashboard hiển thị 2.000 hồ sơ: 740 duyệt, 246 xem xét, 1.014 từ chối.
- [ ] Có thanh menu trái và giao diện hồng–trắng–tím mận.
- [ ] Tra cứu được khách hàng bằng mã hồ sơ và lọc trạng thái.
- [ ] Mở được trang chấm điểm mới, không lỗi tải hai file `.joblib`.
- [ ] TC01 mặc định: dữ liệu AI mẫu cho `P_risk` khoảng 7,36% và đề xuất duyệt (số thực tế phụ thuộc đầu vào và môi trường).
- [ ] TC02: CIC Nhóm 4 → từ chối; TC03: DTI 83,3% → từ chối.
- [ ] TC04: chưa eKYC → từ chối; TC05: đối tác `pending` → xem xét thêm.
- [ ] Tải được báo cáo kết quả JSON.

## E. Xử lý lỗi thường gặp

| Lỗi hiển thị | Cách kiểm tra |
|---|---|
| `No module named 'plotly'` | Đang chạy `app.py` cũ. Trong bản mới không có import Plotly. Kiểm tra lại branch và file app được chọn. |
| `No module named 'ui_components'` | Chưa tải `ui_components.py` lên cùng cấp `app.py`. |
| `No module named 'credit_engine'` | Chưa tải `credit_engine.py` lên thư mục gốc. |
| `No module named 'sklearn'` | Thiếu/đặt sai `requirements.txt`, hoặc cài thư viện thất bại; xem build logs. |
| `_RemainderColsList`, `SimpleImputer` | Mô hình lưu bằng scikit-learn 1.6.1. Chọn Python 3.12 và cài đúng phiên bản. |
| `FileNotFoundError` của CSV/Joblib | File dữ liệu chưa tải lên hoặc nằm nhầm thư mục con. |
| Giao diện chưa đổi màu | Thiếu `style.css` hoặc `.streamlit/config.toml`; kiểm tra tên file và reload trang. |

Hướng dẫn chính thức: [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).
