
import json
from getpass import getpass
from pathlib import Path

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk


# Configuration
ELASTICSEARCH_URL = "https://localhost:9200"
INDEX_NAME = "amazon-products-lab-v1"
CHUNK_SIZE = 500
REQUEST_TIMEOUT = 120
MAX_RETRIES = 3

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "amazon-products.ndjson"


def read_actions(file_path):
    """Read the Bulk NDJSON file incrementally."""

    with file_path.open("r", encoding="utf-8") as file:
        line_number = 0

        while True:
            action_line = file.readline()

            if not action_line:
                break

            line_number += 1

            source_line = file.readline()

            if not source_line:
                raise ValueError(
                    f"Missing document after action at line {line_number}."
                )

            line_number += 1

            try:
                action_data = json.loads(action_line)
                document = json.loads(source_line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON near line {line_number}: {exc}"
                ) from exc

            metadata = action_data.get("index")

            if not isinstance(metadata, dict):
                raise ValueError(
                    f"Expected an index action near line {line_number - 1}."
                )

            target_index = metadata.get("_index")
            document_id = metadata.get("_id")

            if target_index != INDEX_NAME:
                raise ValueError(
                    f"Unexpected target index: {target_index!r}"
                )

            if not document_id:
                raise ValueError(
                    f"Missing document ID near line {line_number}."
                )

            if not isinstance(document, dict):
                raise ValueError(
                    f"Expected a JSON object near line {line_number}."
                )

            yield {
                "_op_type": "index",
                "_index": INDEX_NAME,
                "_id": document_id,
                "_source": document,
            }


def main():
    if not DATA_FILE.is_file():
        print(f"ERROR: Dataset file not found: {DATA_FILE}")
        return

    file_size_mb = DATA_FILE.stat().st_size / (1024 * 1024)

    print(f"Dataset: {DATA_FILE.name}")
    print(f"File size: {file_size_mb:.2f} MB")
    print(f"Target index: {INDEX_NAME}")
    print(f"Batch size: {CHUNK_SIZE}")

    username = input("Elasticsearch username: ").strip()
    password = getpass("Elasticsearch password: ")

    client = Elasticsearch(
        ELASTICSEARCH_URL,
        basic_auth=(username, password),
        verify_certs=False,
        request_timeout=REQUEST_TIMEOUT,
        max_retries=MAX_RETRIES,
        retry_on_timeout=True,
    )

    try:
        if not client.ping():
            print("ERROR: Could not connect to Elasticsearch.")
            return

        print("Connected to Elasticsearch.")

        if not client.indices.exists(index=INDEX_NAME):
            print(f"ERROR: Index does not exist: {INDEX_NAME}")
            print("No index was created. Check the index name.")
            return

        print("Index exists. Validating the dataset before import...")

        # Validate the complete file before sending any documents.
        validated_count = sum(1 for _ in read_actions(DATA_FILE))
        print(f"Dataset validation passed: {validated_count:,} documents.")

        confirm = input(
            f"Import {validated_count:,} documents into "
            f"{INDEX_NAME}? Type YES to continue: "
        )

        if confirm != "YES":
            print("Import cancelled. No documents were sent.")
            return

        succeeded = 0
        failed = 0
        first_errors = []

        print("Import started. Please wait...")

        for ok, result in streaming_bulk(
            client,
            read_actions(DATA_FILE),
            chunk_size=CHUNK_SIZE,
            max_retries=MAX_RETRIES,
            initial_backoff=2,
            max_backoff=30,
            raise_on_error=False,
            raise_on_exception=False,
            request_timeout=REQUEST_TIMEOUT,
        ):
            if ok:
                succeeded += 1
            else:
                failed += 1

                if len(first_errors) < 5:
                    first_errors.append(result)

            processed = succeeded + failed

            if processed % 5000 == 0:
                print(
                    f"Processed: {processed:,} | "
                    f"Successful: {succeeded:,} | "
                    f"Failed: {failed:,}"
                )

        print("\nImport finished.")
        print(f"Successful operations: {succeeded:,}")
        print(f"Failed operations: {failed:,}")

        if first_errors:
            print("\nFirst errors:")
            for error in first_errors:
                print(json.dumps(error, ensure_ascii=False, indent=2))

        if failed == 0:
            print("All bulk operations succeeded.")

        print(
            "Note: successful index operations can replace existing "
            "documents with the same IDs."
        )

    except KeyboardInterrupt:
        print(
            "\nImport interrupted. Some documents may already have "
            "been indexed. You can safely rerun this script with the "
            "same IDs to retry the import."
        )

    except Exception as exc:
        print(f"\nERROR: {type(exc).__name__}: {exc}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
