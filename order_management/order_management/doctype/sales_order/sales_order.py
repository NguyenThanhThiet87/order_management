# Copyright (c) 2026, ThanhThiet and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint


class SalesOrder(Document):
	def validate(self):
		self.validate_quantities_and_prices()
		self.calculate_amount()
		self.validate_status_lifecycle()

	def before_save(self):
		self.prevent_modification_on_closed_orders()

	def on_trash(self):
		if self.status in ["Đã giao", "Hủy"]:
			frappe.throw(
				_("Không được phép xóa đơn hàng đã ở trạng thái '{0}'.").format(self.status),
				frappe.ValidationError,
			)

	def validate_quantities_and_prices(self):
		"""
		Quy tắc nghiệp vụ đề bài:
		- Số lượng (Quantity) phải > 0
		- Đơn giá (Unit Price) phải > 0
		"""
		qty = cint(self.quantity)
		if qty <= 0:
			frappe.throw(
				_("Số lượng (Quantity) phải lớn hơn 0. Giá trị hiện tại: {0}").format(self.quantity),
				frappe.ValidationError,
			)

		price = flt(self.unit_price)
		if price <= 0:
			frappe.throw(
				_("Đơn giá (Unit Price) phải lớn hơn 0. Giá trị hiện tại: {0}").format(self.unit_price),
				frappe.ValidationError,
			)

	def calculate_amount(self):
		"""
		Quy tắc nghiệp vụ đề bài:
		- Thành tiền = Số lượng × Đơn giá
		- Luôn tính toán lại ở server, không tin cậy giá trị do client gửi lên
		"""
		self.amount = flt(cint(self.quantity) * flt(self.unit_price), self.precision("amount") or 2)

	def validate_status_lifecycle(self):
		"""
		Quy tắc trạng thái đề bài:
		- Đơn mới tạo luôn khởi đầu ở trạng thái 'Mới'
		- Từ 'Mới' chỉ được phép chuyển sang 'Đã giao' hoặc 'Hủy'
		"""
		if self.is_new():
			if self.status != "Mới":
				self.status = "Mới"
		else:
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.status == "Mới":
				if self.status not in ["Mới", "Đã giao", "Hủy"]:
					frappe.throw(
						_("Trạng thái không hợp lệ! Từ 'Mới' chỉ có thể chuyển sang 'Đã giao' hoặc 'Hủy'."),
						frappe.ValidationError,
					)

	def prevent_modification_on_closed_orders(self):
		"""
		Quy tắc nghiệp vụ cốt lõi:
		- Đơn hàng 'Đã giao' hoặc 'Hủy' thì KHÔNG sửa, KHÔNG đổi trạng thái được nữa.
		- Kiểm tra ở backend server, chặn cả người dùng thao tác trên Desk lẫn gọi REST API.
		"""
		if self.is_new():
			return

		old_doc = self.get_doc_before_save()
		old_status = old_doc.status if old_doc else frappe.db.get_value("Sales Order", self.name, "status")

		if old_status in ["Đã giao", "Hủy"]:
			frappe.throw(
				_("Đơn hàng {0} đã ở trạng thái '{1}', không được phép chỉnh sửa hoặc đổi trạng thái.").format(
					self.name, old_status
				),
				frappe.ValidationError,
			)
