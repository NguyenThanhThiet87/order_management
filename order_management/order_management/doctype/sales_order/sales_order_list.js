// Copyright (c) 2026, ThanhThiet and contributors
// For license information, please see license.txt

frappe.listview_settings["Sales Order"] = {
	add_fields: ["status", "customer", "amount"],
	get_indicator(doc) {
		if (doc.status === "Mới") {
			return [__("Mới"), "blue", "status,=,Mới"];
		} else if (doc.status === "Đã giao") {
			return [__("Đã giao"), "green", "status,=,Đã giao"];
		} else if (doc.status === "Hủy") {
			return [__("Hủy"), "red", "status,=,Hủy"];
		}
	}
};
