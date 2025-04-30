import re
import time
import base64
import json
import requests


def extract_id(numerade_url: str) -> str:
    """
    Pulls the trailing numeric ID off a Numerade question URL.
    E.g. ".../81652/" -> "81652"
    """
    m = re.search(r'/(\d+)/?$', numerade_url)
    return m.group(1) if m else "unknown"


def xor_b64(text: str, key: str = "console.log(fuckoff);") -> str:
    """
    Mirrors the JS TextEncoder→XOR→btoa flow.
    """
    tb = text.encode("utf-8")
    kb = key.encode("utf-8")
    xored = bytearray(tb[i] ^ kb[i % len(kb)] for i in range(len(tb)))
    return base64.b64encode(xored).decode("utf-8")


def fetch_numerade_html(numerade_url: str, email: str) -> str:
    """
    Builds the JSON payload and POSTs it to Numerade’s service,
    returning the raw HTML snippet in the `data` field.
    """
    payload_token = xor_b64(f"{email}::{numerade_url}")
    resp = requests.post(
        "https://connect.freeportforall.in/service/numerade",
        json={"numerade": payload_token},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    resp.raise_for_status()
    body = resp.json()
    return body.get("data", "")


def main():
    # ─── Configuration ────────────────────────────────────────
    EMAIL        = "hacata4742@oziere.com"
    QUESTION_URL = (
        "https://www.numerade.com/ask/question/"
        "25-if-x2y-y225-what-is-the-value-of-at-the-point43-a-b-c-d-e-81652/"
    )
    # ──────────────────────────────────────────────────────────

    qid = extract_id(QUESTION_URL)
    try:
        snippet = fetch_numerade_html(QUESTION_URL, EMAIL)
        if not snippet:
            print("⚠️  No HTML returned in `data` field.")
            return

        out_file = f"numerade_{qid}.html"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(snippet)
        print(f"✅  Transcript saved to {out_file}")

    except requests.RequestException as e:
        print(f"❌  HTTP error: {e}")
    except Exception as e:
        print(f"❌  Unexpected error: {e}")


if __name__ == "__main__":
    main()