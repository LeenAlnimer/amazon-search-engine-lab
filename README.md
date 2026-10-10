# Amazon Search Engine Lab

A hands-on learning project focused on **Elasticsearch, Kibana, and search relevance** using real-world Amazon product metadata.

The goal is to understand how search engines index data, analyze queries, rank results, and improve the search experience through practical experiments.

## Project Overview

This repository documents a step-by-step journey from dataset inspection and preparation to Elasticsearch indexing, search implementation, and relevance evaluation.

The project uses Amazon product metadata from the **Amazon Reviews'23** dataset, specifically the `raw_meta_All_Beauty` subset provided by McAuley Lab.

Rather than treating Elasticsearch as a black box, the project focuses on understanding how its core features work and how different search configurations affect results.

## Goals

- Understand Elasticsearch indexes, documents, mappings, and field types.
- Explore text analysis and full-text search.
- Compare exact matching with analyzed text search.
- Experiment with partial-word matching, autocomplete, and fuzzy search.
- Understand relevance scoring and ranking using `_score`.
- Evaluate search behavior using realistic product queries.
- Use Kibana Dev Tools to inspect mappings, execute queries, and analyze responses.
- Document experiments, findings, and improvements incrementally.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Dataset inspection, preparation, and import automation |
| PyArrow | Reading the source Parquet dataset |
| Elasticsearch 9.5.5 | Document storage, indexing, and search |
| Kibana 9.5.5 | Query execution, mapping inspection, and result analysis |
| Docker Desktop | Running the local Elasticsearch environment |
| Git and GitHub | Version control and project documentation |

## Dataset

**Source:** [Amazon Reviews'23 — All Beauty Metadata](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_All_Beauty)

The selected dataset is distributed in Parquet format.

### Dataset preparation

The source dataset contains product metadata such as:

- Product identifier (`parent_asin`)
- Product title
- Description
- Features
- Main category
- Price
- Average rating
- Rating count
- Store

The original dataset contains **112,590 rows**. During preparation, 12 rows with missing product identifiers or empty titles were skipped, leaving **112,578 product documents** for indexing.

The prepared documents use `parent_asin` as their Elasticsearch document ID.

### Data preparation decisions

- Empty or whitespace-only titles are excluded.
- Descriptions and features are cleaned and combined into text fields.
- Missing prices are represented as `null`.
- Available prices are converted to numeric values.
- The selected fields are retained for the initial search experiments.
- The original Parquet dataset and generated NDJSON file are kept locally and excluded from Git tracking.

**Note:** The dataset's price currency has not been independently verified.

## Current Elasticsearch Setup

The current lab index is:

`amazon-products-lab-v1`

The index was created with an explicit mapping to control how the selected fields are indexed.

Key mapping decisions include:

- `parent_asin`: `keyword`
- `title`: `text` with a `keyword` subfield
- `description`: `text`
- `features`: `text`
- `main_category`: `keyword`
- `price`: `float`
- `average_rating`: `float`
- `rating_number`: `integer`
- `store`: `keyword`

The mapping uses `dynamic: false`, so fields not explicitly mapped are retained in `_source` but are not dynamically indexed.

A separate `amazon-mapping-test` index was used for initial mapping and multi-field experiments.

## Project Structure

```text
amazon-search-lab/
├── .gitignore
├── inspect_dataset.py
├── prepare_dataset.py
├── import_to_elasticsearch.py
└── README.md
```

### Script responsibilities

**`inspect_dataset.py`**

Inspects the source dataset, including its schema, sample records, missing values, price values, and data quality.

**`prepare_dataset.py`**

Reads the Parquet dataset, cleans selected fields, and generates `amazon-products.ndjson` in Elasticsearch Bulk API format.

**`import_to_elasticsearch.py`**

Connects to the local Elasticsearch instance, validates the prepared dataset, and imports documents in batches using the Elasticsearch Python client and `streaming_bulk`.

### Local files

The following generated or source data files are intentionally excluded from Git:

- The original Parquet dataset
- `amazon-products.ndjson`

These files are kept locally to avoid committing large data files to the repository.

## Work Completed

- Selected the Amazon Reviews'23 All Beauty metadata subset.
- Inspected the dataset schema and data quality.
- Examined missing values, product identifiers, prices, and titles.
- Created an explicit Elasticsearch index mapping.
- Tested basic mapping and multi-field behavior in a separate test index.
- Prepared 112,578 valid product documents in NDJSON format.
- Imported 112,578 documents into `amazon-products-lab-v1`.
- Verified that the bulk import completed with 112,578 successful operations and zero failed operations.
- Added the initial Python scripts and `.gitignore` to GitHub.

## Planned Search Experiments

The following experiments are planned and will be documented as they are implemented.

### 1. Baseline Search

- Retrieve products using basic queries.
- Understand the difference between `match` and `term`.
- Compare `text` and `keyword` field behavior.

### 2. Search Relevance

- Examine how Elasticsearch calculates `_score`.
- Compare the ranking of results for different queries.
- Investigate why some products appear above others.

### 3. Partial-Word Matching

- Test searches where the user enters only part of a product title.
- Explore prefix matching and autocomplete approaches.
- Observe the effect of text analysis on matching.

### 4. Fuzzy Search

- Test misspelled search terms.
- Explore fuzzy matching and edit distance.
- Compare recall and result quality.

### 5. Search Analysis and Evaluation

- Build a collection of representative search queries.
- Compare query behavior and ranked results.
- Record observations, limitations, and improvements.

Additional experiments may be added as the project develops.

## Running the Project

This is a local learning environment. The following steps assume that Python and a compatible Elasticsearch environment are already installed and running.

### 1. Download the dataset

Download the `raw_meta_All_Beauty` Parquet file from the dataset source linked above.

Place it in your local Downloads folder, using the filename expected by `prepare_dataset.py` and `inspect_dataset.py`:

`full-00000-of-00001.parquet`

### 2. Inspect the dataset

Run the inspection script using your Python installation:

```powershell
python inspect_dataset.py
```

Adjust the command to match your local Python installation if necessary.

### 3. Prepare the dataset

```powershell
python prepare_dataset.py
```

This generates the local `amazon-products.ndjson` file.

### 4. Import into Elasticsearch

Ensure Elasticsearch is running and that your local connection settings and credentials are configured appropriately in `import_to_elasticsearch.py`.

Then run:

```powershell
python import_to_elasticsearch.py
```

The script validates the dataset and asks for confirmation before importing the documents.

**Important:** Review the connection settings and authentication requirements before running the import script. Bulk indexing can replace existing documents that have the same IDs in the target index.

## Data and Security Notes

- Dataset files are not committed to this repository.
- Do not commit passwords, API keys, access tokens, or other secrets.
- The current import script uses a local Elasticsearch HTTPS endpoint. Review its certificate-verification configuration before using it outside a local learning environment.
- This repository is an educational lab, not a production-ready search service.

## Documentation Approach

Experiments will be added incrementally, including:

- The question being investigated
- The Elasticsearch query or mapping used
- The observed results
- An explanation of the behavior
- Conclusions and possible improvements

The repository will evolve alongside the learning process, with completed experiments distinguished from planned work.

## License and Dataset Attribution

The Amazon metadata dataset is provided by McAuley Lab. Refer to the [original dataset page](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/tree/main/raw_meta_All_Beauty) for its terms, licensing, and attribution requirements.

The dataset is separate from the code in this repository.
