"""Keyword triage. The fallback whenever Claude can't be trusted or reached.

This path runs when there is no API key, when the API errors or times out, and
crucially when Claude answers with something outside the allowed values. It is
deliberately dull: no model, no network, no failure modes. A Lead always ends
up classified by something.

Order matters. The first matching rule wins, so the rules are listed from most
specific to least.
"""

import re

# (service_interest, qualification_status, keywords)
RULES = [
	(
		"IT",
		"Qualified",
		["ransomware", "breach", "hacked", "malware", "phishing", "locked out", "outage", "down"],
	),
	(
		"IT",
		"In Process",
		["cybersecurity", "security", "firewall", "antivirus", "penetration test", "compliance"],
	),
	(
		"IT",
		"In Process",
		["microsoft 365", "office 365", "m365", "sharepoint", "azure", "cloud", "migration"],
	),
	("IT", "In Process", ["backup", "disaster recovery", "restore", "ransomware insurance"]),
	("IT", "In Process", ["network", "wifi", "wi-fi", "switch", "router", "vpn", "cabling"]),
	("VoIP", "In Process", ["voip", "phone system", "phones", "pbx", "sip", "telephony"]),
	("CRM", "In Process", ["crm", "salesforce", "hubspot", "zoho", "pipeline", "lead management"]),
	("ERP", "In Process", ["erp", "erpnext", "odoo", "netsuite", "inventory", "accounting system"]),
	("EDI", "In Process", ["edi", "850", "810", "trading partner", "purchase order feed"]),
	(
		"Web",
		"In Process",
		["website", "web site", "wordpress", "landing page", "seo", "web app", "ecommerce"],
	),
	("AI", "In Process", ["ai ", "copilot", "chatbot", "automation", "machine learning", "llm"]),
	("Strategy", "In Process", ["vcio", "roadmap", "it strategy", "budget", "consulting"]),
	("IT", "In Process", ["helpdesk", "help desk", "support", "managed services", "it support"]),
]

FALLBACK = ("Other", "Unqualified")


def classify(subject_and_message: str):
	"""Return (service_interest, qualification_status, summary)."""
	haystack = f" {(subject_and_message or '').lower()} "

	for service, qualification, keywords in RULES:
		if any(keyword in haystack for keyword in keywords):
			return service, qualification, _summarise(subject_and_message)

	return FALLBACK[0], FALLBACK[1], _summarise(subject_and_message)


def _summarise(message: str, limit: int = 200) -> str:
	"""First sentence of the enquiry, trimmed. No model involved."""
	text = re.sub(r"\s+", " ", (message or "").strip())
	if not text:
		return ""

	first_sentence = re.split(r"(?<=[.!?])\s", text)[0]
	if len(first_sentence) > limit:
		return first_sentence[: limit - 1].rstrip() + "…"
	return first_sentence
