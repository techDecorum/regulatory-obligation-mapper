# Regulatory Obligation Mapper

An AI-assisted pipeline on Google Cloud that turns regulation text into individual,
traceable obligations, maps them to controls, and keeps a human reviewer in the loop.

## The problem
Compliance teams in banking and healthcare read regulations line by line and map each
requirement to internal controls by hand. It's slow, inconsistent, and hard to audit.
As a business systems analyst in banking, I've seen this work up close.

## How it works (planned architecture)
1. **Intake:** public regulation text is stored in Cloud Storage with its source and retrieval date.
2. **Decompose:** Gemini on Vertex AI splits the text into individual obligations.
3. **Review:** a human approves, corrects, or rejects each AI mapping in a Cloud Run app.
4. **Measure:** decisions are logged to BigQuery to track how accurate the AI is.

## Current status
- [x] **Module 1 – Foundation:** project setup, regulation intake, least-privilege service account
- [ ] Module 2 – Decompose obligations with Gemini
- [ ] Module 3 – Human-in-the-loop review app
- [ ] Module 4 – Accuracy measurement in BigQuery
- [ ] Module 5 – Security hardening
- [ ] Module 6 – AI agent upgrade and HIPAA variant

## Data
| Regulation | Scope | Source |
|---|---|---|
| Regulation P (GLBA privacy rule), 12 CFR Part 1016 | Subpart A, §§1016.4–1016.9 | [eCFR](https://www.ecfr.gov/current/title-12/chapter-X/part-1016) |

Only public regulation text is used. No real customer or bank data.

## Security design
- A dedicated service account (`mapper-pipeline-sa`) with **read-only access to one bucket**
  (`roles/storage.objectViewer`), following least privilege.
- Predefined roles instead of broad basic roles.
- No downloadable service account keys.

## Disclaimer
This is a learning and portfolio project. It is not legal or compliance advice.