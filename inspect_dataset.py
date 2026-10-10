
from pathlib import Path
import pyarrow.parquet as pq

dataset_path = Path.home() / "Downloads" / "full-00000-of-00001.parquet"
table = pq.read_table(dataset_path, columns=["price"])

prices = table.column("price").to_pylist()

valid_prices = []
missing_count = 0
invalid_prices = []

for value in prices:
    if value is None or str(value).strip().lower() in ("", "none"):
        missing_count += 1
        continue

    try:
        valid_prices.append(float(value))
    except (ValueError, TypeError):
        invalid_prices.append(value)

print("Total products:", len(prices))
print("Valid numeric prices:", len(valid_prices))
print("Missing prices:", missing_count)
print("Invalid prices:", len(invalid_prices))

if valid_prices:
    print("Minimum price:", min(valid_prices))
    print("Maximum price:", max(valid_prices))

print("Invalid examples:", invalid_prices[:10])
