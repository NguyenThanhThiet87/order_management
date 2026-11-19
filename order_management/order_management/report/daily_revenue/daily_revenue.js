// Copyright (c) 2026, ThanhThiet and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Revenue"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("Từ ngày"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("Đến ngày"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
