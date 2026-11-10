import json, uuid, re
from decimal import Decimal

SRC_FILE = "parsed_10k.json"
DST_FILE = "parsed_10k.jsonld"

def clean_number(s: str):
    """Convert '$10,000,000' or '40%' into plain number string."""
    if not s or not isinstance(s, str):
        return None
    # Remove $, commas, and % but keep digits, dot, minus
    cleaned = re.sub(r"[^\d\.\-]", "", s)
    return str(Decimal(cleaned)) if cleaned else None

def enrich_numbers(d: dict):
    """Recursively add *_value fields with typed decimal numbers."""
    for key, val in list(d.items()):
        if isinstance(val, str):
            num = clean_number(val)
            if num:
                d[f"{key}_value"] = {
                    "@value": num,
                    "@type": "http://www.w3.org/2001/XMLSchema#decimal"
                }
        elif isinstance(val, dict):
            enrich_numbers(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    enrich_numbers(item)

def convert_file(path_in, path_out):
    data = json.load(open(path_in, encoding="utf-8"))

    # Build JSON-LD wrapper
    jsonld = {
        "@context": {"ex": "http://example.org/tenk/"},
        "@id": f"ex:report-{uuid.uuid4()}",
    }

    # Merge original JSON content
    for k, v in data.items():
        jsonld[k] = v

    # Enrich numeric values
    enrich_numbers(jsonld)

    # Save result
    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(jsonld, f, indent=2, ensure_ascii=False)

    print(f"✅ Done converting → {path_out}")

# Run conversion
convert_file(SRC_FILE, DST_FILE)
