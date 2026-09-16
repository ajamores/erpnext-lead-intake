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
