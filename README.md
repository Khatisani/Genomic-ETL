# Genomic-ETL

Genomic-ETL is a small ETL-style pipeline for processing genomic FASTQ data. The current focus is on building a reliable first stage that validates FASTQ files, checks basic structure, and stages raw records for downstream transformation and machine learning workflows.

The project is still evolving, but it already includes a working validation and extraction flow, a prototype transformation module, and unit tests for the ingestion logic.

## What the project does

At the moment, the pipeline supports:

- validating that a file exists and uses a FASTQ-compatible extension
- checking basic FASTQ structure such as header, separator, and quality line format
- extracting raw records into a staging file for later processing
- testing the extraction and validation behavior with unit tests

## Current project structure

```text
Genomic-ETL/
├── data/
│   └── example.fastq
├── pipeline/
│   ├── __init__.py
│   ├── extract.py
│   └── transform_clean.py
├── tests/
│   └── test_extract.py
├── main.py
└── README.md
```

## Current implementation status

The repository currently has:

- Stage 1: Extraction and validation implemented in pipeline/extract.py
- Stage 2: A transformation prototype implemented in pipeline/transform_clean.py
- Stage 3: Loading and final output generation are still pending

The main entry point in main.py is a draft orchestrator. It is intended to coordinate the pipeline stages, but the full end-to-end workflow is not yet fully connected.

## How to run the current pipeline

Run the extraction workflow directly:

```bash
python3 -m pipeline.extract data/example.fastq
```

This will validate the file and create a staged output at data/extracted_stage.tmp.

You can also try the draft orchestrator:

```bash
python3 main.py data/example.fastq data/output.npy
```

> Note: The current version of the orchestrator runs the extraction stage as part of its flow, but the final .npy output generation is still a work in progress.

## Running tests

To run the test suite:

```bash
python3 -m unittest tests/test_extract.py
```

## Future direction

Planned development includes:

- integrating the transformation logic into the main pipeline flow
- generating a final numerical feature matrix from FASTQ sequences
- adding a proper loading stage for model-ready outputs
- expanding test coverage for transformation and orchestration
