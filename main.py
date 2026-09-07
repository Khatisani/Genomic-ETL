"""
Genomic-ETL Pipeline Orchestrator (`main.py`).

Coordinates execution across the three pipeline stages:
1. Extraction & Validation (pipeline/extract.py)
2. Transformation, QC & Biomarker Scanning (pipeline/transform.py)
3. Loading, Vectorization & SQL Ingestion (pipeline/load.py)
"""

import os
import subprocess
import sys
from pipeline.logger import get_logger

logger = get_logger("orchestrator")


def run_stage(command: list, stage_name: str) -> None:
    """
    Executes a pipeline stage subprocess and monitors exit codes.

    Args:
        command (list): Subprocess command and arguments list.
        stage_name (str): Identifier for logging context.

    Raises:
        SystemExit: If the subprocess returns a non-zero exit code.
    """
    logger.info(f"Starting {stage_name}...")
    proc = subprocess.run(command, capture_output=False)

    if proc.returncode != 0:
        logger.error(
            f"Pipeline aborted: {stage_name} failed with exit code {proc.returncode}."
        )
        sys.exit(proc.returncode)

    logger.info(f"{stage_name} completed successfully.")


def main():
    """
    CLI orchestrator entry point for end-to-end execution.
    """
    if len(sys.argv) != 2:
        logger.error("Invalid arguments provided.")
        print("Usage: python3 main.py <inputfile.fastq>")
        sys.exit(1)

    input_file = sys.argv[1]
    staging_file = "outputs/extracted_stage.tmp"
    filtered_file = "outputs/filtered_stage.tmp"

    os.makedirs("outputs", exist_ok=True)

    logger.info("Initializing Genomic-ETL Pipeline Engine")
    logger.info(f"Source target: {input_file}")

    # Stage 1: Extraction & Validation
    run_stage(
        ["python3", "pipeline/extract.py", input_file],
        "Stage 1 [Extraction & Validation]",
    )

    # Stage 2: Quality Transformation & Filtering
    run_stage(
        ["python3", "pipeline/transform.py", staging_file],
        "Stage 2 [QC & Motif Scanning]",
    )

    # Stage 3: Loading, Vectorization & SQL Ingestion
    run_stage(
        ["python3", "-m", "pipeline.load", filtered_file],
        "Stage 3 [Vectorization & SQL Loader]",
    )

    logger.info("Genomic-ETL Pipeline execution completed successfully.")


if __name__ == "__main__":
    main()