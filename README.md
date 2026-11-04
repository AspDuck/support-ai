# Support AI | Intelligence Studio

An interactive, mobile-friendly support-operations portfolio prototype built with **Streamlit + SQLite**. It demonstrates two AI-adjacent support workflows with explainable, deterministic logic: natural-language data insights and support ticket triage / response drafting.

> **Fictional data only.** All 10,000 records are generated synthetically. No real client data, protected health information, or personal identifiers are included. This prototype is not for clinical or emergency use.

## Features

- **Operations dashboard:** monthly volume, top needs, regions, referrals, response times, urgent share, and follow-up rate.
- **Interactive filters:** region, support need, channel, priority, and date range.
- **Ask the data:** familiar natural-language prompts grounded in filtered records, using fixed analytic functions rather than arbitrary model-generated SQL.
- **Ticket triage:** explainable category/priority/routing suggestions, including safety keyword escalation and human-reviewed drafts.
- **CSV export:** download filtered synthetic records.
- **No OpenAI API key required.** Runs as a standalone demo.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

On first launch, `generate_data.py` creates `support_demo.sqlite3` with 10,000 reproducible fictional interactions. The database is intentionally not stored in Git because it is derived data.

## Deploy on Streamlit Community Cloud

1. Put these files at the root of your GitHub repository (`app.py`, `insights.py`, `triage.py`, `generate_data.py`, `requirements.txt`, `.gitignore`).
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create a new app, select your repository, branch `main`, and entry file `app.py`.
4. Deploy and share the generated public URL.

## Limitations and safeguards

The phrase-to-insight classifier supports a defined set of analytical question families. It is **not** a general language model, and it does not generate SQL. Ticket triage is a demonstration classifier based on keywords and must be reviewed by a qualified human. Never rely on the demo to provide crisis response; in Canada, call/text 988 for suicide crisis support or contact local emergency services in immediate danger.

## Project structure

- `app.py`: Streamlit UI
- `generate_data.py`: reproducible synthetic SQLite dataset generator
- `insights.py`: question-to-aggregation reasoning
- `triage.py`: ticket classification and response drafting
- `requirements.txt`: minimal dependencies
- `.gitignore`: derived database / local files
