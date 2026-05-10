"""
PDF Processor - Core logic for extracting document structure
"""

import logging
import fitz  # PyMuPDF
from pathlib import Path
from title_extractor import TitleExtractor
from heading_detector import HeadingDetector
from output_formatter import OutputFormatter

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Main PDF processing class that orchestrates extraction"""
    
    def __init__(self):
        self.title_extractor = TitleExtractor()
        self.heading_detector = HeadingDetector()
        self.output_formatter = OutputFormatter()
    
    def process_pdf(self, pdf_path):
        """
        Process a PDF file and extract title and hierarchical outline
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            dict: Structured output with title and outline
        """
        try:
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            
            # Limit to 50 pages as specified
            page_count = min(len(doc), 50)
            logger.info(f"Processing {page_count} pages")
            
            # Extract all text blocks with formatting information
            text_blocks = self._extract_text_blocks(doc, page_count)
            
            # Extract title
            title = self.title_extractor.extract_title(doc, text_blocks)
            
            # Detect headings
            headings = self.heading_detector.detect_headings(text_blocks)
            
            # Format output
            result = self.output_formatter.format_output(title, headings)
            
            doc.close()
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    def _extract_text_blocks(self, doc, page_count):
        """Extract text blocks with formatting information from all pages"""
        text_blocks = []
        
        for page_num in range(page_count):
            page = doc[page_num]
            
            # Get text blocks with formatting
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        if not span["text"].strip():
                            continue
                            
                        text_block = {
                            "text": span["text"].strip(),
                            "page": page_num + 1,
                            "bbox": span["bbox"],  # (x0, y0, x1, y1)
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],  # Bold, italic, etc.
                            "x0": span["bbox"][0],
                            "y0": span["bbox"][1],
                            "x1": span["bbox"][2],
                            "y1": span["bbox"][3],
                            "width": span["bbox"][2] - span["bbox"][0],
                            "height": span["bbox"][3] - span["bbox"][1]
                        }
                        
                        # Calculate additional properties
                        text_block["is_bold"] = bool(span["flags"] & 2**4)
                        text_block["is_italic"] = bool(span["flags"] & 2**1)
                        text_block["line_height"] = text_block["height"]
                        
                        text_blocks.append(text_block)
        
        logger.info(f"Extracted {len(text_blocks)} text blocks")
        return text_blocks