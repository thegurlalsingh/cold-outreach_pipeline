# Assignment - Cold Outreach Pipeline

A fully automated B2B cold outreach pipeline. One domain in — lookalike
companies sourced, decision-makers found, emails resolved, outreach sent.
Zero manual steps after the input.

```
stripe.com  →  Ocean.io  →  Prospeo  →  Prospeo  →  Brevo
   (seed)       (lookalikes)  (contacts)    (emails)        (sent)
```

---

## Pipeline Overview

| Stage | Tool | Input | Output |
|-------|------|-------|--------|
| 1 | Ocean.io | Seed domain | Lookalike company domains |
| 2 | Prospeo | Company domains | C-Suite / VP contacts + LinkedIn URLs |
| 3 | Prospeo | LinkedIn URLs | Verified work email addresses |
| 4 | Brevo | Enriched contacts | Personalized cold emails sent |

---

## Project Structure

```
.
├── main.py                   # Orchestrates all 4 stages end to end
├── requirements.txt          # Python dependencies
├── .env                      # API keys and sender info (never commit this)
└── stages/
    ├── ocean.py              # Stage 1 — Ocean.io lookalike discovery
    ├── prospeo.py            # Stage 2 & 3 — Prospeo search + enrich
    └── brevo.py              # Stage 4 — Brevo email sending
```

---

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your `.env`

Create a `.env` file in the project root:

```env
OCEAN_API_KEY=your_ocean_api_key
PROSPEO_API_KEY=your_prospeo_api_key
BREVO_API_KEY=your_brevo_api_key
SENDER_EMAIL=you@yourdomain.com
SENDER_NAME=Your Name
```

> **Note:** Your sender domain must be verified in Brevo before emails can be sent.

### 3. Accounts required

| Service | Signup | Purpose |
|---------|--------|---------|
| [Ocean.io](https://ocean.io) | Company email required | Lookalike company discovery |
| [Prospeo](https://app.prospeo.io) | Free tier available | Contact search + email enrichment |
| [Brevo](https://app.brevo.com) | Free tier available | Transactional email sending |

---

## Running the Pipeline

### Full pipeline (all 4 stages)

```bash
python main.py stripe.com
```

Replace `stripe.com` with your seed domain — a company you already know is
a strong customer fit.

### Run stages individually

```bash
export $(grep -v '^#' .env | xargs)

python stages/ocean.py stripe.com

python stages/prospeo.py search ocean_stage1_output.json

python stages/prospeo.py enrich prospeo_stage2_output.json

python stages/brevo.py prospeo_stage3_output.json
```

---

## Output Files

Each stage saves a JSON file that feeds into the next:

| File | Contents |
|------|----------|
| `ocean_stage1_output.json` | List of lookalike company domains |
| `prospeo_stage2_output.json` | Decision-makers per domain (name, title, LinkedIn URL) |
| `prospeo_stage3_output.json` | Enriched contacts with verified work emails |

---

## Resilience

- **Rate limits** — auto-retries with sleep on `429` responses
- **Missing data** — contacts without LinkedIn URLs or emails are skipped gracefully, pipeline continues
- **Partial failures** — one failed domain or contact does not stop the run
- **Safety checkpoint** — summary shown before emails fire, requires explicit `yes` to proceed

---

## Edge Cases Handled

| Scenario | Behaviour |
|----------|-----------|
| Domain returns no contacts | Skipped, next domain processed |
| Contact has no LinkedIn URL | Skipped with log message |
| Email resolution fails | Contact excluded from mailing list |
| Brevo rate limit hit | Auto-waits 60 seconds, retries once |
| Invalid or placeholder email | Filtered out before sending |
| No verified emails found | Pipeline exits cleanly before Stage 4 |
