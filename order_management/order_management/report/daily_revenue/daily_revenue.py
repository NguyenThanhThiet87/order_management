# Copyright (c) 2026, ThanhThiet and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"fieldname": "order_date",
			"label": _("Ngày tạo đơn"),
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"fieldname": "total_orders",
			"label": _("Số lượng đơn đã giao"),
			"fieldtype": "Int",
			"width": 180,
		},
		{
			"fieldname": "total_revenue",
			"label": _("Tổng doanh thu (VND)"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 220,
		},
	]


def get_data(filters=None):
	conditions = ["status = 'Đã giao'"]
	values = {}

	if filters:
		if filters.get("from_date"):
			conditions.append("DATE(creation) >= %(from_date)s")
			values["from_date"] = filters.get("from_date")
		if filters.get("to_date"):
			conditions.append("DATE(creation) <= %(to_date)s")
			values["to_date"] = filters.get("to_date")

	where_clause = " AND ".join(conditions)

	sql = f"""
		SELECT
			DATE(creation) AS order_date,
			COUNT(name) AS total_orders,
			SUM(amount) AS total_revenue
		FROM `tabSales Order`
		WHERE {where_clause}
		GROUP BY DATE(creation)
		ORDER BY order_date DESC
	"""

	raw_data = frappe.db.sql(sql, values, as_dict=True)
	return raw_data


def get_chart_data(data):
	if not data:
		return None

	# Sắp xếp theo ngày tăng dần để vẽ biểu đồ theo trục thời gian
	sorted_data = list(reversed(data))
	labels = [str(d.get("order_date")) for d in sorted_data]
	values = [float(d.get("total_revenue") or 0.0) for d in sorted_data]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Tổng doanh thu"),
					"values": values,
				}
			],
		},
		"type": "bar",
		"colors": ["#28a745"],
	}


def get_report_summary(data):
	if not data:
		return None

	total_orders = sum(d.get("total_orders", 0) for d in data)
	total_revenue = sum(float(d.get("total_revenue") or 0.0) for d in data)

	return [
		{
			"value": total_orders,
			"label": _("Tổng số đơn đã giao"),
			"datatype": "Int",
		},
		{
			"value": total_revenue,
			"label": _("Tổng doanh thu"),
			"datatype": "Currency",
			"currency": "VND",
		},
	]
