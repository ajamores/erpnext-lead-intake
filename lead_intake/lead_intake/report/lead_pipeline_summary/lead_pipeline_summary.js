// Filters for the Lead Pipeline Summary report.
// Defaults to the last 30 days so the report opens with something in it.

frappe.query_reports["Lead Pipeline Summary"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "status",
			label: __("Lead Status"),
			fieldtype: "Select",
			options: [
				"",
				"Lead",
				"Open",
				"Replied",
				"Opportunity",
				"Quotation",
				"Lost Quotation",
				"Interested",
				"Converted",
				"Do Not Contact",
			],
		},
		{
			fieldname: "triage_source",
			label: __("Triaged By"),
			fieldtype: "Select",
			options: ["", "Claude", "Rules", "Manual"],
		},
	],
};
