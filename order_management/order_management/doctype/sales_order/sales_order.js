// Copyright (c) 2026, ThanhThiet and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Order", {
	refresh(frm) {
		// 1. Nếu đơn hàng đã giao hoặc đã hủy: Khóa form và chặn sửa đổi trên UI
		if (!frm.is_new() && (frm.doc.status === "Đã giao" || frm.doc.status === "Hủy")) {
			frm.disable_save();
			frm.set_read_only();

			const indicator_color = frm.doc.status === "Đã giao" ? "green" : "red";
			frm.page.set_indicator(frm.doc.status, indicator_color);
			return;
		}

		// 2. Thêm nút thao tác nhanh trực tiếp trên thanh công cụ khi đơn ở trạng thái 'Mới'
		if (!frm.is_new() && frm.doc.status === "Mới") {
			frm.add_custom_button(__("Đã giao"), function () {
				frappe.confirm(
					__("Bạn có chắc chắn muốn chuyển đơn hàng sang trạng thái <b>Đã giao</b>?<br>Sau khi giao, đơn hàng sẽ bị khóa vĩnh viễn không thể chỉnh sửa."),
					function () {
						frm.set_value("status", "Đã giao");
						frm.save();
					}
				).addClass("btn-primary");
			}).addClass("btn-success");

			frm.add_custom_button(__("Hủy đơn"), function () {
				frappe.confirm(
					__("Bạn có chắc chắn muốn <b>Hủy</b> đơn hàng này?<br>Sau khi hủy, đơn hàng sẽ không thể chỉnh sửa lại."),
					function () {
						frm.set_value("status", "Hủy");
						frm.save();
					}
				);
			}).addClass("btn-danger");
		}
	},

	// 3. Tự động tính toán trước thành tiền khi người dùng gõ Số lượng hoặc Đơn giá
	quantity(frm) {
		calculate_amount(frm);
	},

	unit_price(frm) {
		calculate_amount(frm);
	}
});

function calculate_amount(frm) {
	const qty = flt(frm.doc.quantity) || 0;
	const price = flt(frm.doc.unit_price) || 0;
	frm.set_value("amount", qty * price);
}
