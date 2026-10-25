"""Module 2: break a regulation into individual obligations with Gemini on Vertex AI."""
import json
import os
from datetime import datetime, timezone

from google import genai
from google.genai import types
from google.cloud import storage

PROJECT = "obligation-mapper"
LOCATION = os.environ.get("GEMINI_LOCATION", "global")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
BUCKET = "obligationbucket"
SOURCE = "regulations/reg-p-12cfr1016-subpart-a.txt"

PROMPT = """You are a compliance analyst at a U.S. bank.
Read the regulation text below and extract every individual obligation it places on a financial institution.

Rules:
- One obligation per item. Split compound requirements into separate items.
- Write each obligation as one plain sentence starting with "The institution must", "The institution must not", or "The institution may".
- Cite the exact section number (for example, 1016.4(a)).
- Copy a short supporting quote from the text, word for word.
- Only extract obligations that are in the text. Do not invent or infer obligations.
- Skip definitions, examples, and headings unless they create an obligation.

Return JSON: a list of objects with these fields:
obligation_id (OBL-001, OBL-002, ...), section, obligation, type ("must", "must_not", or "may"), source_quote.

Regulation text:
"""


def main():
    # 1. Read the regulation from Cloud Storage
    storage_client = storage.Client(project=PROJECT)
    bucket = storage_client.bucket(BUCKET)
    regulation_text = bucket.blob(SOURCE).download_as_text()
    print(f"Read {len(regulation_text):,} characters from gs://{BUCKET}/{SOURCE}")

    # 2. Ask Gemini to extract the obligations
    client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT + regulation_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            max_output_tokens=32768,
        ),
    )
    obligations = json.loads(response.text)
    print(f"Gemini extracted {len(obligations)} obligations using {MODEL}")

    # 3. Save the results to Cloud Storage, with provenance
    result = {
        "source": f"gs://{BUCKET}/{SOURCE}",
        "model": MODEL,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "obligations": obligations,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_name = f"obligations/reg-p-subpart-a-{stamp}.json"
    bucket.blob(out_name).upload_from_string(
        json.dumps(result, indent=2), content_type="application/json"
    )
    print(f"Saved to gs://{BUCKET}/{out_name}")

    # 4. Show the first three as a preview
    for item in obligations[:3]:
        print(f"\n{item['obligation_id']} ({item['section']}): {item['obligation']}")


if __name__ == "__main__":
    main()