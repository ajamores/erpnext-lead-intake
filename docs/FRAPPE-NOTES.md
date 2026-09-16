# Frappe notes

Armand's answers, in his own words, written during the build. Claude Code formats and corrects, never rewords. Kept in the repo as the work happens.

## M0 — the development environment

### 1. What is Bench?

**Armand:** "Banch is basically the platform with all its plumbing installed and it's where like a central hub for the business will reside. So that's where we'll see the leads come in and that's where we will evaluate whether or not the lead is worth pursuing or not."

**Correction (Claude Code):** Bench is the *tool*, not the platform. It's a command-line program plus a folder layout that installs Frappe, fetches apps, creates sites, and runs the dev server and background workers. The central hub the business uses is ERPNext running on a site. Bench built it and manages it; it isn't the thing itself.

### 2. What are the four containers for?

**Armand:** "The four containers FRAP that's the plumbing, where your DB is the database. Redis I've never used Redis, but I believe it is used to throttle requests and to make sure networks don't get overloaded."

**Correction (Claude Code):** MariaDB is the database — correct. The `frappe` container is the machine that runs the framework and the app code; Frappe is the plumbing, the container is where it runs. Redis isn't about throttling: it's an in-memory store, and there are two of them because they do different jobs. `redis-cache` remembers expensive results so Frappe doesn't recompute them or re-ask the database. `redis-queue` holds the waiting list of background jobs — in M3 the job that calls Claude goes into that queue and a worker picks it up, which is how the webhook answers instantly instead of waiting on the API.

### 3. What is a site?

**Armand:** "A site is where we will be running the CRM."

**Addition (Claude Code):** Right. A site is one tenant: its own database, its own uploaded files, its own config, and its own list of installed apps. One bench can host many sites, which is how a provider runs `clienta.example.com` and `clientb.example.com` from a single installation. This one is `development.localhost`.
