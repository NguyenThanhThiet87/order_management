# Mini ERP Order Management System

> **Dự án kiểm tra kỹ thuật (Technical Test) - Frappe Framework v15**  
> **Ứng dụng:** `order_management`  
> **Tác giả:** Nguyễn Thành Thiết  
> **Repository:** [https://github.com/NguyenThanhThiet87/order_management](https://github.com/NguyenThanhThiet87/order_management)  

---

## 1. Giới thiệu tổng quan

Ứng dụng **`order_management`** là một ứng dụng độc lập (standalone custom app) chạy trên nền tảng **Frappe Framework v15**, được thiết kế để quản lý đơn bán hàng và báo cáo doanh thu theo đúng các tiêu chuẩn và yêu cầu khắt khe của bài kiểm tra kỹ thuật:

1. **Quản lý Đơn hàng (`Sales Order` DocType):**
   - Lưu trữ thông tin đơn hàng gồm: Khách hàng, Mặt hàng, Số lượng, Đơn giá, Thành tiền và Trạng thái.
   - Đặt mã đơn hàng tự động theo mẫu: `ORD-.#####` (ví dụ: `ORD-00001`, `ORD-00023`).
   - Tự động tính Thành tiền = `Số lượng × Đơn giá` ở cả tầng Client (xem trước mượt mà) và Backend Python (bảo vệ toàn vẹn dữ liệu).
   - Ràng buộc dữ liệu nghiêm ngặt: `Số lượng > 0`, `Đơn giá > 0`.
2. **Quy tắc vòng đời trạng thái đơn hàng (Status Lifecycle):**
   - Đơn mới tạo luôn có trạng thái mặc định là **Mới**.
   - Từ **Mới**, đơn hàng chỉ được phép chuyển sang **Đã giao** hoặc **Hủy**.
   - **Quy tắc bất biến:** Một khi đơn hàng đã chuyển sang **Đã giao** hoặc **Hủy**, hệ thống sẽ khóa toàn bộ (read-only), **KHÔNG cho phép chỉnh sửa bất kỳ thông tin nào, KHÔNG cho phép đổi trạng thái, và KHÔNG cho phép xóa** (được kiểm soát chặt chẽ ở cả controller backend và client script giao diện).
3. **Báo cáo Doanh thu theo ngày (`Daily Revenue Report`):**
   - Báo cáo dạng Script Report chuẩn Frappe, truy vấn trực tiếp từ cơ sở dữ liệu.
   - Thống kê theo ngày tạo đơn (`DATE(creation)`).
   - Chỉ lọc và tính các đơn hàng có trạng thái **Đã giao** (hoàn toàn loại bỏ đơn Mới hoặc Hủy).
   - Thể hiện rõ: **Số lượng đơn hàng** và **Tổng doanh thu** theo từng ngày.
   - Tích hợp **Biểu đồ cột (Bar Chart)** biến động doanh thu và các **Thẻ tóm tắt chỉ số (Summary Cards)**.
4. **Kiểm thử tự động (Automated Unit Tests):**
   - 12 bài kiểm thử tự động đạt 100% tỷ lệ vượt qua (`Ran 12 tests ... OK`), bao phủ toàn bộ các trường hợp biên và luồng nghiệp vụ.

---

## 2. Yêu cầu môi trường

- **Hệ điều hành:** Linux / Ubuntu 22.04 LTS (hoặc WSL2 trên Windows)
- **Python:** 3.10 hoặc 3.11
- **Node.js:** v18 hoặc v20 LTS & Yarn 1.22+
- **Cơ sở dữ liệu:** MariaDB 10.6+ hoặc 11.x (cấu hình character set `utf8mb4`)
- **Frappe Framework:** Phiên bản v15

---

## 3. Hướng dẫn cài đặt vào một Frappe Bench bất kỳ

Bạn có thể dễ dàng cài đặt ứng dụng này vào bất kỳ Bench Frappe v15 nào thông qua các lệnh tiêu chuẩn sau:

```bash
# 1. Di chuyển vào thư mục frappe-bench của bạn
cd /path/to/frappe-bench

# 2. Tải mã nguồn ứng dụng từ GitHub
bench get-app https://github.com/NguyenThanhThiet87/order_management.git

# 3. Cài đặt app vào site mục tiêu của bạn (thay 'your-site.localhost' bằng tên site của bạn)
bench --site your-site.localhost install-app order_management

# 4. Chạy migrate để tạo bảng DocType và nạp cấu hình Report
bench --site your-site.localhost migrate

# 5. Xóa cache và build asset (nếu cần)
bench --site your-site.localhost clear-cache
bench build --app order_management
```

Sau khi hoàn tất, mở trình duyệt truy cập vào site Frappe của bạn để trải nghiệm ứng dụng.

---

## 4. Hướng dẫn chạy kiểm thử tự động (Automated Tests)

Ứng dụng đi kèm bộ kiểm thử tự động toàn diện được viết bằng `FrappeTestCase`. Để chạy toàn bộ test suite:

```bash
# Chạy tất cả test cases của ứng dụng order_management
bench --site your-site.localhost run-tests --app order_management
```

Hoặc chạy chi tiết từng module:

```bash
# 1. Chạy 9 bài test cho DocType Sales Order (Tính tiền, Ràng buộc số lượng/đơn giá, Vòng đời trạng thái, Chặn xóa)
bench --site your-site.localhost run-tests --module order_management.order_management.doctype.sales_order.test_sales_order

# 2. Chạy 3 bài test cho Báo cáo doanh thu Daily Revenue (Lọc đơn đã giao, Tính tổng doanh thu, Bộ lọc thời gian)
bench --site your-site.localhost run-tests --module order_management.order_management.report.daily_revenue.test_daily_revenue
```

**Kết quả kiểm thử thực tế:**
```text
............
----------------------------------------------------------------------
Ran 12 tests in 0.419s

OK
```

---

## 5. Giả định và Lưu ý kỹ thuật (Technical Assumptions)

1. **Thiết kế Single-item Sales Order:**
   - Theo đúng đặc tả bài test: Mỗi đơn hàng chỉ gồm một mặt hàng cụ thể kèm số lượng và đơn giá. Do đó, các trường thông tin được đặt trực tiếp trên DocType `Sales Order` chính, không phân tách bảng con (child table) hay doctype danh mục phụ, giúp cấu trúc cơ sở dữ liệu tinh gọn và truy vấn báo cáo đạt hiệu năng tối đa.
2. **Nguyên tắc "Never Trust the Client":**
   - Trường `amount` (Thành tiền) trên giao diện được đặt thuộc tính `read_only: 1`.
   - Tại backend `sales_order.py`, hàm `calculate_amount()` luôn tính toán lại trước khi lưu (`cint(self.quantity) * flt(self.unit_price)`) để triệt tiêu hoàn toàn nguy cơ gian lận qua REST API.
3. **Bảo mật tính toàn vẹn trạng thái đơn hàng:**
   - Trong `sales_order.py`, hàm `prevent_modification_on_closed_orders()` kiểm tra trạng thái trước khi lưu (`old_doc = self.get_doc_before_save()`). Nếu trạng thái cũ đã là `Đã giao` hoặc `Hủy`, mọi thao tác ghi đè đều bị ném ngoại lệ `frappe.ValidationError`.
   - Hàm `on_trash()` chặn hoàn toàn việc xóa chứng từ khi đơn đã giao hoặc hủy.
4. **UX/UI trên Frappe Desk:**
   - Tích hợp Client Script [sales_order.js](order_management/order_management/doctype/sales_order/sales_order.js) tự động thêm 2 nút thao tác nhanh **Đã giao** (màu xanh lá) và **Hủy đơn** (màu đỏ) kèm hộp thoại xác nhận khi đơn đang ở trạng thái `Mới`.
   - Tự động khóa toàn bộ trường (`frm.set_read_only()`) và ẩn nút Save (`frm.disable_save()`) khi đơn ở trạng thái kết thúc.
   - Tích hợp [sales_order_list.js](order_management/order_management/doctype/sales_order/sales_order_list.js) hiển thị các huy hiệu trạng thái trực quan trên màn hình danh sách (Mới = Xanh dương, Đã giao = Xanh lá, Hủy = Đỏ).

---

## 6. Hướng dẫn nghiệm thu 3 luồng nghiệp vụ chính

### Luồng 1: Tạo đơn hàng & Tự động tính Thành tiền
1. Truy cập Desk $\rightarrow$ Tìm kiếm **Sales Order** $\rightarrow$ Bấm **+ Add Sales Order**.
2. Nhập:
   - Khách hàng: `Công ty ABC`
   - Mặt hàng: `Máy tính xách tay ThinkPad`
   - Số lượng: `3`
   - Đơn giá: `20,000,000`
3. Quan sát: Trường **Thành tiền** ngay lập tức tự động hiển thị `60,000,000 VND`.
4. Bấm **Save**: Đơn hàng được tạo thành công với mã `ORD-xxxxx` và trạng thái khởi tạo là `Mới`.

### Luồng 2: Đổi trạng thái $\rightarrow$ 'Đã giao' $\rightarrow$ Khóa bất biến
1. Tại đơn hàng vừa tạo (đang ở trạng thái `Mới`), bấm nút **Đã giao** trên thanh tiêu đề.
2. Xác nhận hộp thoại thông báo.
3. Quan sát:
   - Huy hiệu trạng thái chuyển sang màu xanh lá cây `Đã giao`.
   - Nút **Save** tự động biến mất.
   - Tất cả các ô nhập liệu (Khách hàng, Mặt hàng, Số lượng, Đơn giá, Trạng thái) đều bị khóa xám không thể chỉnh sửa.
   - Thử gọi API sửa đơn hoặc cố tình đổi trạng thái $\rightarrow$ Hệ thống lập tức từ chối và báo lỗi.

### Luồng 3: Xem Báo cáo Doanh thu theo ngày (Daily Revenue)
1. Tại thanh tìm kiếm Desk (Ctrl + G), gõ **Daily Revenue** (hoặc truy cập qua URL: `/app/query-report/Daily%20Revenue`).
2. Màn hình báo cáo hiển thị:
   - **Thẻ chỉ số tóm tắt:** Tổng số đơn đã giao và Tổng doanh thu.
   - **Biểu đồ cột (Bar Chart):** Thể hiện trực quan doanh thu theo các ngày.
   - **Bảng dữ liệu chi tiết:** Cột `Ngày tạo đơn`, `Số lượng đơn đã giao`, `Tổng doanh thu (VND)` kèm dòng tổng cộng ở chân trang.
   - Các đơn hàng ở trạng thái `Mới` hoặc `Hủy` hoàn toàn không bị tính vào báo cáo.

---

## 7. Cấu trúc thư mục mã nguồn

```text
order_management/
├── README.md
├── license.txt
├── pyproject.toml
└── order_management/
    ├── hooks.py
    ├── modules.txt
    ├── order_management/
    │   ├── doctype/
    │   │   └── sales_order/
    │   │       ├── sales_order.json       # Định nghĩa Schema DocType
    │   │       ├── sales_order.py         # Controller xử lý backend & validation
    │   │       ├── sales_order.js         # Client script cho Form View
    │   │       ├── sales_order_list.js    # Cấu hình màu sắc trạng thái List View
    │   │       └── test_sales_order.py    # 9 bài unit test tự động
    │   └── report/
    │       └── daily_revenue/
    │           ├── daily_revenue.json     # Metadata của Script Report
    │           ├── daily_revenue.py       # SQL aggregation, chart & summary
    │           ├── daily_revenue.js       # Bộ lọc ngày từ ngày - đến ngày
    │           └── test_daily_revenue.py  # 3 bài unit test tự động cho báo cáo
```

---
*Ứng dụng được xây dựng tuân thủ đầy đủ Frappe Standard Coding Guidelines.*
