# LeadPilot: find people who are publicly asking for what your client sells

> **Not legal advice.** The operator and each client are responsible for compliance with CAN-SPAM, CASL, GDPR/UK-GDPR and local laws.
> Have a lawyer review the terms, consent text and regional settings before enabling any non-US region.

Phase 1 delivers: scaffold, database + migrations, admin login (argon2, CSRF, lockout, optional TOTP),
client intake (form + JSON/YAML import), AI-generated ICP with edit and approve, cost tracking,
and the **AI assistant panel on the right side of every page**.

## What's in v0.2
**UI:** left navigation, dashboard (clients, pending approvals, spend vs budget, recent activity), costs page,
system status page, grouped intake form, readable ICP view with an "Edit JSON" tab, progress steps and activity feed on
each client, toasts, busy buttons on slow actions, search and status filter, branded login and error pages.
**AI panel (right side):** collapsible (Hide button, or Ctrl+K to open), remembers open/closed, instant message echo,
typing indicator, safe markdown rendering of replies, Copy button, per-client context.
**Backend:** request IDs + JSON access logs, security headers (HSTS when `COOKIE_SECURE=true`), HTML/JSON error handling,
`/healthz` and `/readyz`, pause/resume with required reason and audit trail, per-user AI chat rate limit,
reusable rate limiter, cost reporting queries, and a Redis-free limiter that Phase 3 will swap for Redis.

## What's in the AI upgrade
- **Streaming chat** with Stop (Esc), Regenerate, live safe-markdown, and partial replies saved if you stop.
- **Structured output:** ICP and email generation use forced tool-use with validated schemas (no fragile JSON parsing).
- **Email Studio** (client page, once the ICP is approved): paste verified facts about a prospect, get a 3-email sequence with
  3 subject variants each. Pipeline: one generation call, instant code lint (length, links, spam words, fake "Re:", invented
  numbers, unknown fact ids), one LLM self-check, at most one rewrite, otherwise flagged "needs review".
- **Efficiency:** pooled keep-alive HTTP client, prompt caching with cache-aware cost tracking, compact deterministic context,
  history character budget, grouped queries, no model call when the lint already fails.
- Prompts live in `prompts/` (`assistant_v2`, `icp_v2`, `draft_sequence_v1`, `selfcheck_v1`) and the version is logged.

## What's in v0.3 (AI upgrade)
- **Streaming chat** with Stop (Esc), Regenerate, live safe-markdown, partial replies saved if you stop.
- **Email Studio** (client page, needs an approved ICP): paste verified facts about a prospect and get a 3-email sequence
  with 3 subject variants each. Every email is grounded: it can only cite your facts; a deterministic lint rejects invented
  numbers, spam phrases, fake "Re:" subjects, extra links, and greetings; a separate AI reviewer scores accuracy, tone, spam
  safety and compliance; failures trigger one rewrite, then go to you flagged. Greeting, signature, postal address and the
  unsubscribe/promotional footer are added by code so they can never be forgotten.
- **Structured output** through forced tool-use (ICP and emails) instead of parsing free text.
- **Efficiency:** prompt caching, pooled keep-alive connection, one call writes the whole sequence, lint runs before the
  AI reviewer (no model spend on obviously bad drafts), compact deterministic chat context, history character budget.
- Drafts are not stored or sent yet: the approval queue (Phase 5 persistence) and compliance gate (Phase 6) come next.

## What is new in v0.4: Proof Lens
Every sentence in an Email Studio draft is labelled with the prospect fact, client proof, offer or call to action that backs it, and unbacked sentences are shown in red. A first email whose opening is not backed by a fact is flagged for review. It runs in code, so it costs no extra AI calls. Settings: `MIN_OVERLAP` and `MIN_SHARED` in `app/services/provenance.py`.

## v0.5: Unlimited use and your own model
In `.env`: `UNLIMITED_USE=true` removes the per-client cost caps and the in-app rate limits (spend is still recorded on the Costs page).
Claude is still paid per use by Anthropic, and Anthropic's own account limits still apply.
For truly free, unlimited use, run a model on your own computer: install Ollama (ollama.com), run `ollama pull llama3.1:8b`,
then set `LLM_PROVIDER=ollama` in `.env` and restart. Local models are less accurate than Claude, so review emails carefully.

## v0.6: themes, logo, Ollama without a key
Light and dark themes (moon/sun button in the header, remembered per browser), a new logo (`app/static/logo.svg`), and the System page shows the AI provider. With `LLM_PROVIDER=ollama` no Anthropic key is needed.

## v0.8: Find leads (problem-first)
LeadPilot now looks for the **problem**, not the demographic. For a client, press **Find leads**:

1. It builds searches from the client's *Problems you solve* (plain customer wording) plus geography, urgency and
   frustration phrasing ("need help with...", "looking for a quote", "unhappy with my current provider...").
2. It searches the public web (Brave Search API if `BRAVE_API_KEY` is set, otherwise DuckDuckGo) and opens each page,
   respecting `robots.txt`. Sites behind a login (Facebook, LinkedIn, X) are never read.
3. The model judges each page, but **code checks its work**: the quoted evidence must appear word for word on the page,
   the post must be a first-hand request, still open, recent, in the service area, and a customer the client wants.
4. The score is plain arithmetic (problem 30, intent 25, recency 15, fit 15, area 10, reachable 5). Below 60 is dropped.
5. Only contact details that are printed on the page are shown. Emails are never guessed or looked up.
6. Pages a program cannot open (Reddit blocks most bots) can only be judged from the search snippet. Those leads are
   labelled **Check the page first** and capped at 69, so they can never outrank verified leads.
7. Nothing is ever sent. **Write a message** drafts a reply for a person to review and copy.

Track each lead (contacted, replied, won, not a fit) and download them as a spreadsheet. The AI now has its own page (**Ask AI**, second icon in the left bar, or Ctrl+K). Files: `app/leadfinder/`, `app/api/leads.py`,
`app/services/leads.py`, `prompts/lead_qualify_v1.md`, `prompts/lead_outreach_v1.md`, migration `0002`.

Search settings are in `.env.example` (`SEARCH_PROVIDER`, `BRAVE_API_KEY`, `LEADS_MAX_QUERIES`, `LEADS_MAX_PAGES`).
After upgrading from v0.7 run `make migrate`.

## v0.9: simple look, Ask AI page
The interface is now deliberately plain, in the style of Polify: a narrow icon-only bar on the left, white pages, one blue accent,
no shadows, and a Light / Dark choice at the top right. Home is one big **Ask AI** button and four plain rows.
**Ask AI** is a single chat page (streaming replies, Stop, Regenerate, Copy, Clear chat) that can be scoped to one client.
To re-brand, edit the tokens at the top of `app/static/app.css` and `app/static/logo.svg`.

## v0.7: design system
Warm neutral surfaces, one deep-green brand color, a single 6px radius, borders instead of shadows, Inter for the interface and Source Serif 4 for page titles. To re-brand, edit the tokens at the top of `app/static/app.css` (`--btn`, `--brand-text`, `--bg`, `--r`) and `app/static/logo.svg`.

## Quick start (any computer with Python 3.12+)

```bash
python start.py      # Windows: py start.py
```
The first run installs everything, asks for your keys, creates your login and opens the app. Next time, run the same command to start it.

## Manual setup (macOS / Linux; on Windows use WSL2)

```bash
cd leadpilot
python3 -m venv .venv && source .venv/bin/activate
make install          # installs dependencies
make init             # creates .env with a fresh SECRET_KEY
```
Open `.env` and set `ANTHROPIC_API_KEY=...` (needed for ICP generation and the AI panel).
Then:
```bash
make migrate          # creates the database tables
make admin            # create your admin login (add --totp via: python scripts/create_admin.py --totp)
make seed             # optional: demo client with an approved ICP (no API key needed)
make dev              # starts http://127.0.0.1:8000
```

## Test and lint
```bash
make test
make lint
```

## Docker (production-style)
```bash
cp .env.example .env && python scripts/gen_key.py --write-env
export POSTGRES_PASSWORD='choose-a-long-password'
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml exec app python scripts/create_admin.py
```
Put Caddy in front for HTTPS (`docker/Caddyfile`) and set `COOKIE_SECURE=true`.

## Using the AI panel
It sits on the right of every admin page. On a client page it knows that client's intake and approved ICP;
elsewhere it gives general help. It cannot take actions. Chat history is stored per admin and client; use **Clear** to delete it.
On small screens tap the **AI** button in the header.

## Security notes
Secrets come only from environment variables. Sessions are signed cookies; every POST needs a CSRF token.
Login locks the account after repeated failures. Never commit `.env`.
