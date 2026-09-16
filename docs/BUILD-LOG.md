# Build log

Written as the work happens, not reconstructed afterwards. Kept in the repo as the work happens.

## 2026-09-15 — M0: development environment

| Who | What | Notes |
|---|---|---|
| Armand | Chose the problem, the stack and the scope | Website enquiry → ERPNext CRM Lead, AI triage, SQL report |
| Armand | Enabled Docker Desktop's WSL integration | Docker was installed on Windows but unreachable from WSL, so nothing could run |
| Claude Code | Found WSL had 7.4 GB of a 15.3 GB host, below the 6 GB Docker wants for this stack | Wrote `.wslconfig` asking for 10 GB and 8 GB swap |
| Armand | Ran `wsl --shutdown` and restarted | Came back with 9.7 GB total, 7.1 GB available, 12 CPUs |
| Claude Code | Checked frappe_docker's current docs instead of trusting the commands we had | Found three differences: v16 is now stable, the Procfile needs its redis lines removed, and CLI-only use needs `FRAPPE_BIND_ADDR` plus explicit port mappings |
| Claude Code | Cloned frappe_docker, copied `devcontainer-example` to `.devcontainer`, patched the `frappe` service | Added `FRAPPE_BIND_ADDR=0.0.0.0` and bound ports 8000-8005 and 9000-9005 to 127.0.0.1 only |
| Claude Code | Started the four containers | frappe, mariadb 11.8, redis-cache, redis-queue |
| Claude Code | Checked the container's runtimes before the long install | Default was Python 3.14.7 and Node 24. Assumed those were too new for Frappe and pinned Python 3.12.14 and Node 22.23.2 |
| Claude Code | `bench init --frappe-branch version-16` **failed** | The command still exited 0, so the failure only showed up when the next step reported `No module named 'frappe'`. The real error: `frappe==16.34.0 depends on Python>=3.14,<3.15` |
| Claude Code | Read `apps/frappe/pyproject.toml` and `package.json` instead of guessing again | v16 requires **Python >=3.14,<3.15** and **Node >=24**. The image's defaults were correct all along; the pin caused the failure |
| Claude Code | Wiped the bench and re-ran `bench init` with the container's default runtimes | Running |

## 2026-09-15 — M1: the app and its custom fields

| Who | What | Notes |
|---|---|---|
| Claude Code | `bench new-app lead_intake`, installed on the site | Took three attempts: `bench new-app` asks more questions than expected and aborts on EOF rather than taking defaults |
| Claude Code | Read `apps/erpnext/erpnext/crm/doctype/lead/lead.json` before designing any field | Lead already has `qualification_status` (Unqualified / In Process / Qualified), so we use ERPNext's field instead of inventing one |
| Armand | Created the Service Interest field by hand through Customize Form | Frappe named it `custom_service_interest`. Since v15, fields added this way get a `custom_` prefix so they can never collide with a field ERPNext adds to Lead later |
| Claude Code | Declared all four fields in `lead_intake/setup/custom_fields.py`, wired to `after_install` and `after_migrate` | Chose `create_custom_fields()` over exported fixtures: it updates in place, so installing and migrating repeatedly is idempotent. It also repositioned Armand's field into the Qualification tab |

## 2026-09-15 — M2: webhook intake

| Who | What | Notes |
|---|---|---|
| Claude Code | `lead_intake/api.py` — `intake_enquiry`, POST only, token auth | Validates required fields and the email address, caps every field length, and returns a plain JSON `{"error": ...}` with a 400 rather than Frappe's default 417 |
| Claude Code | Idempotency in two layers | A lookup on `custom_external_enquiry_id` handles the ordinary case; the unique index plus a `UniqueValidationError` catch handles two identical enquiries arriving at once. The lookup alone would not be safe under concurrency |
| Claude Code | `lead_intake/setup/integration_user.py` — a least-privilege role and user | The role can create and read Leads and nothing else. A token leaked from a website's backend then cannot reach customers, invoices or accounts |
| Armand | Tested all five cases against the running site | Valid enquiry 200, repeat 200 with `duplicate: true` and nothing created, missing fields 400 naming them, bad email 400, no credentials 403 |
