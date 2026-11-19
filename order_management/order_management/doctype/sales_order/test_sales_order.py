# Copyright (c) 2026, ThanhThiet and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestSalesOrder(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("Sales Order", {"customer": ["in", ["Khách hàng Test", "Khách hàng Test Lỗi"]]})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.delete("Sales Order", {"customer": ["in", ["Khách hàng Test", "Khách hàng Test Lỗi"]]})
		frappe.db.commit()

	def create_order(self, customer="Khách hàng Test", item="Laptop Dell", qty=2, unit_price=15000000, status="Mới", **kwargs):
		doc = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": customer,
			"item": item,
			"quantity": qty,
			"unit_price": unit_price,
			"status": status,
			**kwargs
		})
		doc.insert()
		return doc

	def test_01_create_valid_order_and_server_amount_calculation(self):
		"""1. Tạo đơn hợp lệ: Thành tiền phải do server tự tính = Số lượng * Đơn giá"""
		doc = self.create_order(qty=3, unit_price=10000000)
		self.assertEqual(doc.status, "Mới")
		self.assertEqual(doc.amount, 30000000.0)

	def test_02_server_recalculates_amount_if_client_tampers(self):
		"""2. Kiểm tra nếu client gửi sai amount lên, server phải tính lại đè lên"""
		doc = self.create_order(qty=2, unit_price=5000000, amount=99999999)
		self.assertEqual(doc.amount, 10000000.0, "Server phải tự tính lại Amount, không tin client")

	def test_03_reject_zero_or_negative_quantity(self):
		"""3. Chặn số lượng <= 0"""
		with self.assertRaises(frappe.ValidationError):
			self.create_order(customer="Khách hàng Test Lỗi", qty=0, unit_price=5000000)

		with self.assertRaises(frappe.ValidationError):
			self.create_order(customer="Khách hàng Test Lỗi", qty=-3, unit_price=5000000)

	def test_04_reject_zero_or_negative_unit_price(self):
		"""4. Chặn đơn giá <= 0"""
		with self.assertRaises(frappe.ValidationError):
			self.create_order(customer="Khách hàng Test Lỗi", qty=1, unit_price=0)

		with self.assertRaises(frappe.ValidationError):
			self.create_order(customer="Khách hàng Test Lỗi", qty=1, unit_price=-100000)

	def test_05_status_transition_from_moi_to_da_giao(self):
		"""5. Chuyển trạng thái từ 'Mới' sang 'Đã giao' thành công"""
		doc = self.create_order()
		doc.status = "Đã giao"
		doc.save()
		self.assertEqual(doc.status, "Đã giao")

	def test_06_status_transition_from_moi_to_huy(self):
		"""6. Chuyển trạng thái từ 'Mới' sang 'Hủy' thành công"""
		doc = self.create_order()
		doc.status = "Hủy"
		doc.save()
		self.assertEqual(doc.status, "Hủy")

	def test_07_disallow_edit_when_da_giao(self):
		"""7. Đơn đã giao thì KHÔNG sửa, KHÔNG đổi trạng thái được nữa"""
		doc = self.create_order()
		doc.status = "Đã giao"
		doc.save()

		# Thử đổi trạng thái sang 'Mới' hoặc 'Hủy'
		doc.status = "Mới"
		with self.assertRaises(frappe.ValidationError):
			doc.save()

		# Thử sửa số lượng hoặc đơn giá
		doc.reload()
		doc.quantity = 10
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_08_disallow_edit_when_huy(self):
		"""8. Đơn đã hủy thì KHÔNG sửa, KHÔNG đổi trạng thái được nữa"""
		doc = self.create_order()
		doc.status = "Hủy"
		doc.save()

		# Thử sửa lại thành 'Mới'
		doc.status = "Mới"
		with self.assertRaises(frappe.ValidationError):
			doc.save()

		# Thử đổi mặt hàng
		doc.reload()
		doc.item = "Bàn phím cơ"
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_09_disallow_delete_when_completed_or_cancelled(self):
		"""9. Không được xóa đơn hàng đã giao hoặc đã hủy"""
		doc = self.create_order()
		doc.status = "Đã giao"
		doc.save()

		with self.assertRaises(frappe.ValidationError):
			doc.delete()
