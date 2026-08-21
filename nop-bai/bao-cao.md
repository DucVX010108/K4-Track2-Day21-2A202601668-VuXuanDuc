# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Vũ Xuân Đức |
| MSSV | 2A202601668 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/DucVX010108/K4-Track2-Day21-2A202601668-VuXuanDuc |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |
| 3 | 50 | 0.05 | 3 | 0.6256 | 0.8540 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ tham số ở lần chạy 2 đạt `f1_score` cao nhất (0.7149) trên tập đánh giá holdout và vượt qua ngưỡng chất lượng (0.65). Mặc dù lần chạy 1 (bộ tham số gốc) có accuracy cao hơn (0.8780 so với 0.8740), f1_score của lần 2 lại vượt trội hơn, chứng minh mô hình lần 2 nhận diện chính xác lớp thiểu số (thu nhập cao > 50K) tốt hơn thay vì chỉ dự đoán thiên vị lớp đa số. Ngược lại, lần chạy 3 với `n_estimators=50` và `learning_rate=0.05` cho f1_score chỉ đạt 0.6256 (bị chặn bởi quality gate). Việc tăng `n_estimators` lên 200 kết hợp với `max_depth=5` và `learning_rate=0.1` giúp thuật toán Gradient Boosting nắm bắt tốt các mối quan hệ phi tuyến phức tạp giữa các đặc trưng như học vấn, nghề nghiệp và số giờ làm việc mà vẫn duy trì khả năng tổng quát hóa tốt.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult Income có sự mất cân bằng lớp rõ rệt với khoảng 75% số mẫu thuộc nhóm thu nhập thấp (<= 50K) và chỉ 25% thuộc nhóm thu nhập cao (> 50K). Trong tình huống này, một mô hình thô sơ luôn đoán nhãn "thu nhập thấp" cho mọi trường hợp vẫn dễ dàng đạt độ chính xác accuracy 75%, nhưng hoàn toàn vô dụng trong thực tế vì tỷ lệ phát hiện khách hàng thu nhập cao bằng 0.

Chỉ số F1-score trên lớp dương (thu nhập cao) là trung bình điều hòa giữa Precision và Recall, phản ánh chính xác khả năng nhận diện đúng đối tượng mục tiêu đồng thời hạn chế dự đoán sai. Chúng ta tuyệt đối không dùng `average="weighted"` hay `average="macro"` khi gọi hàm `f1_score` vì cách tính trọng số sẽ bị lớp đa số 75% kéo điểm lên, làm sai lệch và che giấu năng lực thực sự của mô hình trên nhóm khách hàng tiềm năng.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Gọi API trên VM báo lỗi `Could not connect to server`. | Thiếu model trên Storage và lệch phiên bản `scikit-learn` giữa local (1.4.2) và VM (1.7.2) gây sập service. | Upload model lên Storage, cài đặt đúng `scikit-learn==1.4.2` và cập nhật file `serve.py` trên VM. |
| GCP chặn tạo Service Account key file JSON. | Chính sách bảo mật Organization Policy (`disableServiceAccountKeyCreation`) của GCP. | Cấu hình quyền đọc Storage phù hợp cho DVC và tự động chuyển giao artifact model qua SSH deploy. |
| Lỗi cú pháp JSON decode khi chạy `curl.exe` trên PowerShell. | PowerShell tự động loại bỏ dấu ngoặc kép khi truyền tham số `-d` chứa chuỗi JSON. | Bọc toàn bộ chuỗi JSON trong dấu nháy đơn `'` ở ngoài cùng để PowerShell giữ nguyên định dạng. |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu từ `train_batch2.csv` (tổng cộng 44.722 mẫu), F1-score của mô hình tăng từ 0.7149 lên 0.7354 và accuracy tăng từ 0.8740 lên 0.8820. Do dữ liệu bổ sung có cùng phân phối với tập dữ liệu ban đầu, mức tăng là vừa phải nhưng giúp mô hình ổn định và tổng quát hóa tốt hơn. Kết quả quan trọng nhất là toàn bộ quy trình CI/CD tự động kích hoạt, huấn luyện và cập nhật mô hình lên VM thành công ngay khi có commit dữ liệu mới.
