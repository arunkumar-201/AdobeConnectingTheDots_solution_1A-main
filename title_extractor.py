"""
Title Extractor - Logic for identifying document titles
"""

import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

class TitleExtractor:
    """Extracts document title using multiple strategies"""
    
    def extract_title(self, doc, text_blocks):
        """
        Extract document title using multiple heuristics
        
        Args:
            doc: PyMuPDF document object
            text_blocks: List of text blocks with formatting info
            
        Returns:
            str: Extracted title
        """
        # Strategy 1: Try document metadata
        title = self._extract_from_metadata(doc)
        if title and len(title.strip()) > 0:
            logger.info(f"Title extracted from metadata: {title}")
            return title.strip()
        
        # Strategy 2: Find title from first page content
        title = self._extract_from_content(text_blocks)
        if title:
            logger.info(f"Title extracted from content: {title}")
            return title
        
        # Strategy 3: Fallback to filename
        title = "Document Title"
        logger.info(f"Using fallback title: {title}")
        return title
    
    def _extract_from_metadata(self, doc):
        """Extract title from PDF metadata"""
        try:
            metadata = doc.metadata
            title = metadata.get("title", "").strip()
            if title and len(title) > 2:
                return title
        except Exception as e:
            logger.debug(f"Could not extract metadata title: {e}")
        return None
    
    def _extract_from_content(self, text_blocks):
        """Extract title from document content using heuristics"""
        if not text_blocks:
            return None
        
        # Filter first page blocks
        first_page_blocks = [b for b in text_blocks if b["page"] == 1]
        if not first_page_blocks:
            return None
        
        # Find potential titles using multiple criteria
        candidates = []
        
        # Get font size statistics
        font_sizes = [b["size"] for b in first_page_blocks]
        if not font_sizes:
            return None
            
        avg_size = sum(font_sizes) / len(font_sizes)
        max_size = max(font_sizes)
        
        # Look for large, bold, centered text in upper part of first page
        page_height = max(b["y1"] for b in first_page_blocks)
        upper_threshold = page_height * 0.3  # Upper 30% of page
        
        for block in first_page_blocks:
            # Skip very small text or common patterns
            if (len(block["text"]) < 3 or 
                len(block["text"]) > 200 or
                self._is_common_pattern(block["text"])):
                continue
            
            score = 0
            
            # Large font size
            if block["size"] >= max_size * 0.8:
                score += 3
            elif block["size"] >= avg_size * 1.5:
                score += 2
            
            # Bold text
            if block["is_bold"]:
                score += 2
            
            # Position in upper part of page
            if block["y0"] <= upper_threshold:
                score += 2
            
            # Centered text (approximately)
            page_width = max(b["x1"] for b in first_page_blocks)
            center = page_width / 2
            text_center = (block["x0"] + block["x1"]) / 2
            if abs(text_center - center) < page_width * 0.2:
                score += 1
            
            # Avoid very long lines (likely paragraphs)
            if len(block["text"]) > 100:
                score -= 1
            
            # Prefer title case or all caps
            if (block["text"].istitle() or 
                (block["text"].isupper() and len(block["text"]) > 5)):
                score += 1
            
            if score > 0:
                candidates.append((score, block["text"], block["y0"]))
        
        if candidates:
            # Sort by score (descending) and position (ascending)
            candidates.sort(key=lambda x: (-x[0], x[2]))
            title = candidates[0][1].strip()
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            title = title.strip('"\'')
            
            if len(title) >= 3:
                return title
        
        return None
    
    def _is_common_pattern(self, text):
        """Check if text matches common non-title patterns"""
        patterns = [
            r'^\d+$',  # Just numbers
            r'^page\s+\d+',  # Page numbers
            r'^chapter\s+\d+',  # Chapter numbers
            r'^fig\w*\s+\d+',  # Figure references
            r'^table\s+\d+',  # Table references
            r'^\w{1,3}\s*$',  # Very short text
            r'^[^\w]*$',  # Only punctuation
        ]
        
        text_lower = text.lower().strip()
        for pattern in patterns:
            if re.match(pattern, text_lower):
                return True
        
        return False