"""Custom fields this app adds to ERPNext's Lead.

Declared here rather than left as manual UI changes so that a fresh
`bench install-app lead_intake` reproduces them exactly. Run on install and
after every migrate; `create_custom_fields` updates in place, so it is safe
to run repeatedly.

The `custom_` prefix matches what Frappe generates for fields created through
Customize Form, and guarantees these can never collide with a field ERPNext
adds to Lead in a future version.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

SERVICE_INTEREST_OPTIONS = [
	"IT",
	"Strategy",
	"AI",
	"CRM",
	"ERP",
	"EDI",
	"VoIP",
	"Web",
	"Other",
]

TRIAGE_SOURCES = ["Claude", "Rules", "Manual"]

CUSTOM_FIELDS = {
	"Lead": [
		{
			"fieldname": "custom_external_enquiry_id",
			"label": "External Enquiry ID",
			"fieldtype": "Data",
			"insert_after": "qualification_status",
			"unique": 1,
			"read_only": 1,
			"no_copy": 1,
			"description": "Identifier from the sending system. Makes intake idempotent.",
		},
		{
			"fieldname": "custom_service_interest",
			"label": "Service Interest",
			"fieldtype": "Select",
			"insert_after": "custom_external_enquiry_id",
			"options": "\n".join([""] + SERVICE_INTEREST_OPTIONS),
			"in_list_view": 1,
			"translatable": 1,
		},
		{
			"fieldname": "custom_ai_summary",
			"label": "AI Summary",
			"fieldtype": "Small Text",
			"insert_after": "custom_service_interest",
			"description": "One sentence a salesperson can read in the list view.",
		},
		{
			"fieldname": "custom_triage_source",
			"label": "Triage Source",
			"fieldtype": "Select",
			"insert_after": "custom_ai_summary",
			"options": "\n".join([""] + TRIAGE_SOURCES),
			"read_only": 1,
			"in_standard_filter": 1,
			"description": "How the service interest and qualification status were set.",
		},
	]
}


def setup_custom_fields():
	create_custom_fields(CUSTOM_FIELDS)
