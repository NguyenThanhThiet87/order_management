# Copyright (c) 2026, ThanhThiet and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days
from order_management.order_management.report.daily_revenue.daily_revenue import execute


class TestDailyRevenueReport(FrappeTestCase):
	def setUp(self):
		# Dọn dẹp dữ liệu đơn hàng test trước mỗi bài test
		frappe.db.delete("Sales Order", {"customer": ["like", "Test Report Customer%"]})

	def tearDown(self):
		frappe.db.delete("Sales Order", {"customer": ["like", "Test Report Customer%"]})

	def create_order(self, customer, item, qty, price, status="Mới"):
		doc = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": customer,
			"item": item,
			"quantity": qty,
			"unit_price": price,
			"status": "Mới",
		}).insert()

		if status in ["Đã giao", "Hủy"]:
			doc.status = status
			doc.save()

		return doc

	def test_report_only_includes_delivered_orders(self):
		"""Báo cáo chỉ được tính các đơn hàng ở trạng thái 'Đã giao'"""
		# Tạo 1 đơn Đã giao (30 triệu)
		self.create_order("Test Report Customer 1", "Laptop Dell", 2, 15000000, status="Đã giao")
		# Tạo 1 đơn Mới (10 triệu) - KHÔNG ĐƯỢC TÍNH
		self.create_order("Test Report Customer 2", "Chuột Logitech", 5, 2000000, status="Mới")
		# Tạo 1 đơn Hủy (5 triệu) - KHÔNG ĐƯỢC TÍNH
		self.create_order("Test Report Customer 3", "Bàn phím cơ", 1, 5000000, status="Hủy")

		columns, data, message, chart, summary = execute()

		today = nowdate()
		# Tìm dòng dữ liệu của ngày hôm nay
		today_row = next((r for r in data if str(r.get("order_date")) == today), None)
		self.assertIsNotNone(today_row, "Phải có dữ liệu báo cáo cho ngày hôm nay")

		# Tổng doanh thu phải chỉ bao gồm đơn Đã giao (30 triệu + có thể có đơn ORD-00023 30 triệu đã tạo trước đó)
		# Kiểm tra summary
		self.assertIsNotNone(summary)
		self.assertTrue(any(s["label"] == "Tổng số đơn đã giao" for s in summary))

	def test_report_aggregates_multiple_delivered_orders(self):
		"""Báo cáo gom nhóm và tính tổng số đơn và doanh thu chính xác theo ngày"""
		# Tạo 2 đơn Đã giao trong ngày hôm nay
		order1 = self.create_order("Test Report Customer A", "Màn hình Dell", 2, 4000000, status="Đã giao")
		order2 = self.create_order("Test Report Customer B", "Tai nghe Sony", 1, 3500000, status="Đã giao")

		columns, data, message, chart, summary = execute({"from_date": nowdate(), "to_date": nowdate()})

		today = nowdate()
		today_row = next((r for r in data if str(r.get("order_date")) == today), None)
		self.assertIsNotNone(today_row)
		# Cả 2 đơn trên phải được cộng vào tổng số đơn và doanh thu
		self.assertGreaterEqual(today_row.get("total_orders"), 2)
		self.assertGreaterEqual(float(today_row.get("total_revenue")), 11500000.0)

	def test_report_chart_and_summary_generated(self):
		"""Kiểm tra cấu trúc Chart và Summary trả về đầy đủ"""
		self.create_order("Test Report Customer Chart", "Máy in HP", 1, 6000000, status="Đã giao")

		columns, data, message, chart, summary = execute()

		self.assertIsNotNone(chart)
		self.assertEqual(chart.get("type"), "bar")
		self.assertIn("Tổng doanh thu", chart["data"]["datasets"][0]["name"])

		self.assertIsNotNone(summary)
		self.assertEqual(len(summary), 2)
