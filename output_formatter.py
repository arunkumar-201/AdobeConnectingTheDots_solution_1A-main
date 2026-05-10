"""
Output Formatter - Formats extracted data into required JSON structure
"""

import logging

logger = logging.getLogger(__name__)

class OutputFormatter:
    """Formats extraction results into the required JSON structure"""
    
    def format_output(self, title, headings):
        """
        Format title and headings into required JSON structure
        
        Args:
            title: Extracted document title
            headings: List of detected headings with level, text, and page
            
        Returns:
            dict: Formatted output matching specification
        """
        # Clean and validate title
        if not title or not isinstance(title, str):
            title = "Document Title"
        
        title = title.strip()
        if not title:
            title = "Document Title"
        
        # Clean and validate headings
        clean_headings = []
        seen_headings = set()
        
        for heading in headings:
            # Validate heading structure
            if not isinstance(heading, dict):
                continue
                
            level = heading.get("level", "H1")
            text = heading.get("text", "").strip()
            page = heading.get("page", 1)
            
            # Skip empty or invalid headings
            if not text or len(text) < 2:
                continue
            
            # Normalize level
            if level not in ["H1", "H2", "H3"]:
                level = "H1"
            
            # Ensure page is integer
            try:
                page = int(page)
                if page < 1:
                    page = 1
            except (ValueError, TypeError):
                page = 1
            
            # Remove duplicates (same text on same page)
            heading_key = (text.lower(), page)
            if heading_key in seen_headings:
                continue
            seen_headings.add(heading_key)
            
            # Clean text
            text = self._clean_text(text)
            
            clean_headings.append({
                "level": level,
                "text": text,
                "page": page
            })
        
        # Sort headings by page, then by level priority
        level_priority = {"H1": 1, "H2": 2, "H3": 3}
        clean_headings.sort(key=lambda h: (h["page"], level_priority.get(h["level"], 1)))
        
        result = {
            "title": title,
            "outline": clean_headings
        }
        
        logger.info(f"Formatted output: title='{title}', {len(clean_headings)} headings")
        return result
    
    def _clean_text(self, text):
        """Clean and normalize heading text"""
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common artifacts
        text = re.sub(r'^[•▪▫◦‣⁃\-*]\s*', '', text)  # Remove bullets
        text = text.strip('.,;:')  # Remove trailing punctuation
        
        # Limit length
        if len(text) > 150:
            text = text[:147] + "..."
        
        return text