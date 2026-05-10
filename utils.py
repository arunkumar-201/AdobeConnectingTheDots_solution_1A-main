"""
Utility functions for PDF processing
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_filename(filename):
    """Clean filename for safe filesystem usage"""
    # Remove or replace problematic characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(cleaned) > 200:
        cleaned = cleaned[:200]
    return cleaned

def is_valid_pdf(file_path):
    """Check if file is a valid PDF"""
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        
        # Check file extension
        if path.suffix.lower() != '.pdf':
            return False
        
        # Check file size (not empty, not too large)
        size = path.stat().st_size
        if size == 0 or size > 100 * 1024 * 1024:  # 100MB limit
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating PDF {file_path}: {e}")
        return False

def normalize_text(text):
    """Normalize text for better processing"""
    if not text:
        return ""
    
    # Handle common unicode issues
    text = text.replace('\ufeff', '')  # Remove BOM
    text = text.replace('\u00a0', ' ')  # Non-breaking space to regular space
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def detect_language(text_blocks):
    """Simple language detection based on character patterns"""
    if not text_blocks:
        return "en"
    
    # Combine first 1000 characters from text blocks
    combined_text = ""
    for block in text_blocks[:50]:  # First 50 blocks
        combined_text += block.get("text", "") + " "
        if len(combined_text) > 1000:
            break
    
    # Simple heuristic language detection
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]', combined_text):
        return "ja"  # Japanese
    elif re.search(r'[\u4e00-\u9fff]', combined_text):
        return "zh"  # Chinese
    elif re.search(r'[\u0400-\u04ff]', combined_text):
        return "ru"  # Russian
    elif re.search(r'[\u0590-\u05ff]', combined_text):
        return "he"  # Hebrew
    elif re.search(r'[\u0600-\u06ff]', combined_text):
        return "ar"  # Arabic
    
    return "en"  # Default to English

def calculate_text_density(text_blocks, page_num):
    """Calculate text density for a specific page"""
    page_blocks = [b for b in text_blocks if b["page"] == page_num]
    
    if not page_blocks:
        return 0
    
    # Calculate total text area
    total_area = 0
    for block in page_blocks:
        width = block["x1"] - block["x0"]
        height = block["y1"] - block["y0"]
        total_area += width * height
    
    # Estimate page area (rough approximation)
    max_x = max(b["x1"] for b in page_blocks)
    max_y = max(b["y1"] for b in page_blocks)
    page_area = max_x * max_y
    
    if page_area == 0:
        return 0
    
    return total_area / page_area