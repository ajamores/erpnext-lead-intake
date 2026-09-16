"""Webhook intake for website enquiries.

    POST /api/method/lead_intake.api.intake_enquiry
    Authorization: token <api_key>:<api_secret>

Authenticated callers only — a website's own backend, or any system that
already holds a token. The browser never sees these credentials.

Two properties matter more than anything else here:

* **Idempotency.** Networks retry. A sender that posts the same
  `external_enquiry_id` twice gets the same Lead back and nothing new is
  created. The unique index on the field is what makes that safe under
  concurrency, not the lookup.
* **Nothing is invented.** A company name that doesn't match an existing
  Customer is recorded as text on the Lead, never used to create records.
"""

import frappe
from frappe import _
from frappe.utils import validate_email_address

MAX_LENGTHS = {
	"external_enquiry_id": 140,
	"contact_name": 140,
	"company_name": 140,
	"email": 140,
	"phone": 40,
	"message": 10000,
}

REQUIRED_FIELDS = ("external_enquiry_id", "contact_name", "email", "message")


def _error(message, status=400):
	"""Return a predictable JSON error instead of Frappe's default 417."""
	frappe.local.response["http_status_code"] = status
	return {"error": message}


def _clean(value, field):
	if value is None:
		return None
	value = str(value).strip()
	return value[: MAX_LENGTHS[field]]


@frappe.whitelist(methods=["POST"])
def intake_enquiry(
	external_enquiry_id=None,
	contact_name=None,
	email=None,
	message=None,
	company_name=None,
	phone=None,
):
	payload = {
		"external_enquiry_id": _clean(external_enquiry_id, "external_enquiry_id"),
		"contact_name": _clean(contact_name, "contact_name"),
		"email": _clean(email, "email"),
		"message": _clean(message, "message"),
		"company_name": _clean(company_name, "company_name"),
		"phone": _clean(phone, "phone"),
	}

	missing = [field for field in REQUIRED_FIELDS if not payload[field]]
	if missing:
		return _error(_("Missing required field(s): {0}").format(", ".join(missing)))

	if not validate_email_address(payload["email"]):
		return _error(_("Not a valid email address: {0}").format(payload["email"]))

	existing = frappe.db.get_value(
		"Lead", {"custom_external_enquiry_id": payload["external_enquiry_id"]}, "name"
	)
	if existing:
		return {"lead": existing, "duplicate": True}

	lead = frappe.new_doc("Lead")
	lead.update(
		{
			"lead_name": payload["contact_name"],
			"company_name": payload["company_name"],
			"email_id": payload["email"],
			"mobile_no": payload["phone"],
			"status": "Lead",
			"custom_external_enquiry_id": payload["external_enquiry_id"],
			"custom_enquiry_message": payload["message"],
		}
	)

	try:
		lead.insert()
	except frappe.DuplicateEntryError:
		# ERPNext's Lead refuses a second Lead with an email address already on
		# file. A returning enquirer is a normal event, not a server error, so
		# the caller gets a 409 naming the Lead that already holds the address
		# rather than a traceback. Attaching the new enquiry to that Lead as a
		# note would be the next step; see README, Known limitations.
		frappe.db.rollback()
		owner = frappe.db.get_value("Lead", {"email_id": payload["email"]}, "name")
		return _error(
			_("A Lead already exists for {0}: {1}").format(payload["email"], owner),
			status=409,
		)
	except frappe.UniqueValidationError:
		# Two identical enquiries arrived at once. The database settled it;
		# return whichever Lead won rather than failing the caller.
		frappe.db.rollback()
		existing = frappe.db.get_value(
			"Lead", {"custom_external_enquiry_id": payload["external_enquiry_id"]}, "name"
		)
		if existing:
			return {"lead": existing, "duplicate": True}
		raise

	return {"lead": lead.name, "duplicate": False}
