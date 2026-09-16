"""Creates the least-privilege user that the webhook authenticates as.

Run once per site:

    bench --site <site> execute lead_intake.setup.integration_user.create_integration_user

The role it creates can create and read Leads and nothing else. A token that
leaks from a website's backend should not be able to read customers, invoices
or anything in Accounts, which is exactly what would happen if an integration
ran as Administrator.

The API secret is shown once, at creation. Frappe stores it hashed and cannot
show it again; re-running rotates it.
"""

import frappe

ROLE = "Lead Intake Integration"
USER_EMAIL = "lead-intake@integration.local"


def _ensure_role():
	if not frappe.db.exists("Role", ROLE):
		role = frappe.new_doc("Role")
		role.role_name = ROLE
		role.desk_access = 0
		role.insert(ignore_permissions=True)

	from frappe.permissions import add_permission, update_permission_property

	add_permission("Lead", ROLE, 0)
	for permission in ("read", "create"):
		update_permission_property("Lead", ROLE, 0, permission, 1)
	for permission in ("write", "delete", "submit", "cancel", "amend", "report", "export", "share"):
		update_permission_property("Lead", ROLE, 0, permission, 0)


def _ensure_user():
	if frappe.db.exists("User", USER_EMAIL):
		return frappe.get_doc("User", USER_EMAIL)

	user = frappe.new_doc("User")
	user.update(
		{
			"email": USER_EMAIL,
			"first_name": "Lead Intake",
			"last_name": "Integration",
			"user_type": "System User",
			"send_welcome_email": 0,
			"enabled": 1,
		}
	)
	user.insert(ignore_permissions=True)
	return user


def create_integration_user():
	_ensure_role()
	user = _ensure_user()

	user.add_roles(ROLE)

	api_secret = frappe.generate_hash(length=15)
	user.api_key = user.api_key or frappe.generate_hash(length=15)
	user.api_secret = api_secret
	user.save(ignore_permissions=True)
	frappe.db.commit()

	print(f"LEAD_INTAKE_TOKEN={user.api_key}:{api_secret}")
	return {"api_key": user.api_key}
