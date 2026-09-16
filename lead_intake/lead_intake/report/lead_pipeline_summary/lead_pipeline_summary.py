"""Lead Pipeline Summary — what came in, what it was about, and who judged it.

One aggregate query, grouped by service. Every filter value is bound as a
parameter; nothing from the user is formatted into the SQL string.

The last column is the one worth explaining in a demo: it shows what share of
each row was classified by Claude rather than by the keyword fallback, so
anyone reading the report can see how much of it the model actually touched.
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

UNCLASSIFIED = "(Unclassified)"


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	return [
		{
			"label": _("Service"),
			"fieldname": "service",
			"fieldtype": "Data",
			"width": 160,
		},
		{"label": _("Total"), "fieldname": "total", "fieldtype": "Int", "width": 80},
		{"label": _("Qualified"), "fieldname": "qualified", "fieldtype": "Int", "width": 100},
		{"label": _("In Process"), "fieldname": "in_process", "fieldtype": "Int", "width": 100},
		{"label": _("Unqualified"), "fieldname": "unqualified", "fieldtype": "Int", "width": 110},
		{
			"label": _("Became Opportunity"),
			"fieldname": "opportunities",
			"fieldtype": "Int",
			"width": 160,
		},
		{
			"label": _("% Triaged by Claude"),
			"fieldname": "pct_claude",
			"fieldtype": "Percent",
			"width": 160,
		},
	]


def get_data(filters):
	conditions = ["l.docstatus < 2", "DATE(l.creation) BETWEEN %(from_date)s AND %(to_date)s"]
	values = {
		"from_date": getdate(filters.from_date or add_days(nowdate(), -30)),
		"to_date": getdate(filters.to_date or nowdate()),
		"unclassified": UNCLASSIFIED,
	}

	if filters.status:
		conditions.append("l.status = %(status)s")
		values["status"] = filters.status

	if filters.triage_source:
		conditions.append("l.custom_triage_source = %(triage_source)s")
		values["triage_source"] = filters.triage_source

	return frappe.db.sql(
		f"""
		SELECT
			COALESCE(NULLIF(l.custom_service_interest, ''), %(unclassified)s) AS service,
			COUNT(*) AS total,
			SUM(CASE WHEN l.qualification_status = 'Qualified' THEN 1 ELSE 0 END) AS qualified,
			SUM(CASE WHEN l.qualification_status = 'In Process' THEN 1 ELSE 0 END) AS in_process,
			SUM(CASE WHEN l.qualification_status = 'Unqualified' THEN 1 ELSE 0 END) AS unqualified,
			SUM(CASE WHEN l.status IN ('Opportunity', 'Converted') THEN 1 ELSE 0 END) AS opportunities,
			ROUND(
				100.0 * SUM(CASE WHEN l.custom_triage_source = 'Claude' THEN 1 ELSE 0 END)
				/ COUNT(*),
				0
			) AS pct_claude
		FROM `tabLead` l
		WHERE {" AND ".join(conditions)}
		GROUP BY service
		ORDER BY total DESC, service ASC
		""",
		values,
		as_dict=True,
	)
