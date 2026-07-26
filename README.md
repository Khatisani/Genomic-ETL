# Genomic-ETL

Genomic-ETL is a small, end-to-end Python data pipeline built to ingest raw DNA sequencing files, apply quality control (QC) filtering, screen for high-risk pharmacogenomic biomarkers, and convert biological sequence data into machine-learning-ready tensors and clinical JSON database records.


## The Clinical Scenario: Compound-K 

​Compound-K is a hypothetical psychiatric drug developed for treatment resistant clinical depression. During Phase III clinical trials, researchers identified specific pharmacogenomic biomarkers—short DNA sequence motifs—strongly correlated with severe adverse drug reactions (ADRs), such as neurotoxicity and acute liver injury.

​These high-risk risk sequences were cataloged and stored in data/biomarkers.fasta.

When a patient is prescribed Compound-K, their whole genome or target gene panel is sequenced. (Note: Epigenetic modifications such as DNA methylation are outside the scope of this pipeline).

​The goal of this ETL pipeline is to automatically process patient sequencing files, filter out sequencing noise, flag patients carrying risk motifs, and format the data for downstream clinical databases and predictive ML models.

## Why We Need an ETL Pipeline

​DNA sequencers do not output neat, structured patient tables. Instead, they output massive, messy FASTQ files filled with raw text records.

Every sequencing read consists of a strict 4-line block:

​Header (@): Sequence identifier and machine metadata. ​
Nucleotide Sequence: The raw base calls (A, C, G, T, or N for unknown). ​
Separator (+): Marker line separating sequence from quality scores. 
​Phred Quality String: ASCII characters encoding the machine's confidence in each base call. 

### The Challenges:

​Sequencer Noise: Sequencers make mistakes. Low-quality base calls (low Phred scores) can look like false-positive risk mutations.
​Format Corruption: Corrupted headers or mismatched sequence/quality string lengths will break downstream analysis.
​Unusable Raw Format: Machine learning models cannot process ASCII quality strings like 3IIIIIIIFF9BG or raw text sequences directly—they require standardized numerical tensors.

## Pipeline Architecture

​This project breaks the data processing down into three modular stages: Extract, Transform, and Load.

```
  +-------------------+
  | Raw FASTQ File    |
  +---------+---------+
            |
            v
  +-------------------+
  | 1. EXTRACT        | --> File Validation & 4-Line Integrity Check
  +---------+---------+
            | (Staged .tmp)
            v
  +-------------------+
  | 2. TRANSFORM      | --> ASCII -> Phred+33 conversion, Q20 QC Filter,
  +---------+---------+     and FASTQ Motif Scanning against biomarkers.fasta
            | (Filtered .tmp)
            v
  +-------------------+
  | 3. LOAD           | --> One-Hot Base Encoding, Sequence Padding/Truncation,
  +---------+---------+     Tensor Compilation (.npy) & Clinical DB Export (.json)

```

## Project Structure

```text
Genomic-ETL/
├── data/
│   ├── biomarkers.fasta         # HYPOTHETICAL: Mock sequence data for prototype testing
│   ├── example.fastq            # HYPOTHETICAL: Local structure validation file
│   ├── multi_seq.fastq          # HYPOTHETICAL: Multi-record mock dataset
│   └── sample1.fastq            # REAL: Authentic data from Galaxy Project Repository
│ 
├── pipeline/
│   ├── extract.py               # Stage 1: Ingestion & Validation Engine
│   ├── transform.py             # Stage 2: Q20 QC & Biomarker Motif Scanner
│   └── load.py                  # Stage 3: Tensor Vectorization & JSON Exporter
│
├── tests/
│   ├── test_extract.py          # Extraction test suite
│   ├── test_transform.py        # Transformation test suite
│   └── test_load.py             # Load test suite
│
├── main.py                      # Master Pipeline Orchestrator
└── README.md                    # Project Documentation
```

## How to run the current pipeline

### Run the pipeline directly:

```bash
python3 main.py data/example.fastq 
```

### Run the pipeline sequentially from the root directory:
#### Stage 1: Validate and stage raw FASTQ data
```python3 pipeline.extract data/sample_patient.fastq```

#### Stage 2: Perform Quality Control and scan for Compound-K risk biomarkers
```python3 pipeline.transform outputs/extracted_stage.tmp```

#### Stage 3: Compile numerical tensors and export JSON assets
```python3 pipeline.load outputs/filtered_stage.tmp```


## Running tests

To run the test suite:

```bash
python3 -m unittest tests
```

## Data Origin
Hypothetical Data (biomarkers.fasta, example.fastq, multi_seq.fastq): Programmatically generated or manually structured mock files. They do not contain real biological samples; instead, they serve as stable local baselines to verify that our extraction logic catches structural edge cases and structural anomalies.

Real-World Benchmark Data (data/sample1.fastq): Obtained directly from the open-source Galaxy Project Test Data Repository. This contains authentic sequencer outputs with real biological base calls and instrument quality scores, serving as our true production benchmark.

## Future directions
1. Database integration (SQLite)
2. Handle data integrity in schemas
3. Replace simple print statements with logging to track pipeline steps
4. How to handle big files?

5. Should I automate so it runs as soon as a file is uploaded?

WTC-AC6ZHTH9
