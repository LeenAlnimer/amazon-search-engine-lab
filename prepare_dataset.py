
from pathlib import Path
import json
import pyarrow.parquet as pq

dataset_path = Path.home() / "Downloads" / "full-00000-of-00001.parquet"
output_path = Path(__file__).parent / "amazon-products.ndjson"

table = pq.read_table(dataset_path)

def clean_text_list(values):
    if not values:
        return None

    cleaned = [
        value.strip()
        for value in values
        if isinstance(value, str) and value.strip()
    ]

    return " ".join(cleaned) if cleaned else None

def clean_price(value):
    if value is None or str(value).strip().lower() in ("", "none"):
        return None

    return float(value)

written = 0
skipped = 0

with output_path.open("w", encoding="utf-8") as file:
    for row in table.to_pylist():
        product_id = row.get("parent_asin")
        title = row.get("title")

        if not product_id or not isinstance(title, str) or not title.strip():
            skipped += 1
            continue

        product = {
            "parent_asin": product_id,
            "title": title.strip(),
            "description": clean_text_list(row.get("description")),
            "features": clean_text_list(row.get("features")),
            "main_category": row.get("main_category"),
            "price": clean_price(row.get("price")),
            "average_rating": row.get("average_rating"),
            "rating_number": row.get("rating_number"),
            "store": row.get("store") or None,
        }

        action = {
            "index": {
                "_index": "amazon-products-lab-v1",
                "_id": product_id,
            }
        }

        file.write(json.dumps(action, ensure_ascii=False) + "\n")
        file.write(json.dumps(product, ensure_ascii=False) + "\n")
        written += 1

print("Products prepared:", written)
print("Products skipped:", skipped)
print("Output file:", output_path)
