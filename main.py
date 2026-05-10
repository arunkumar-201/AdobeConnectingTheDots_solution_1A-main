#!/usr/bin/env python3
"""
PDF Document Structure Extractor
Main entry point for processing PDFs and extracting hierarchical outlines
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/extraction.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to process all PDFs in input directory"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    processor = PDFProcessor()
    total_start_time = time.time()
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            start_time = time.time()
            
            # Process PDF
            result = processor.process_pdf(pdf_file)
            
            # Generate output filename
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            # Save result
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            elapsed = time.time() - start_time
            logger.info(f"Completed {pdf_file.name} in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            # Create error output
            error_result = {
                "title": "Error: Could not extract title",
                "outline": [],
                "error": str(e)
            }
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    total_elapsed = time.time() - total_start_time
    logger.info(f"Processed {len(pdf_files)} files in {total_elapsed:.2f}s")

if __name__ == "__main__":
    main()