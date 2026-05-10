"""
Heading Detector - Advanced heuristics for detecting document headings
"""

import logging
import re
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class HeadingDetector:
    """Detects headings using multiple heuristic approaches"""
    
    def __init__(self):
        self.heading_patterns = [
            # Numbered patterns
            r'^\d+\.?\s+',  # 1. or 1 
            r'^\d+\.\d+\.?\s+',  # 1.1. or 1.1
            r'^\d+\.\d+\.\d+\.?\s+',  # 1.1.1. or 1.1.1
            r'^[IVXLCDM]+\.?\s+',  # Roman numerals
            r'^[A-Z]\.?\s+',  # A. or A
            r'^[a-z]\)?\s+',  # a) or a
            # Bullet patterns
            r'^[•▪▫◦‣⁃]\s+',
            r'^[-*]\s+',
        ]
        
        self.exclude_patterns = [
            r'^\d+$',  # Page numbers
            r'^page\s+\d+',
            r'^fig\w*\s+\d+',
            r'^table\s+\d+',
            r'^appendix\s*[a-z]?$',
        ]
    
    def detect_headings(self, text_blocks):
        """
        Detect headings from text blocks using multiple heuristics
        
        Args:
            text_blocks: List of text blocks with formatting information
            
        Returns:
            List of heading dictionaries with level, text, and page
        """
        if not text_blocks:
            return []
        
        # Calculate document statistics
        stats = self._calculate_statistics(text_blocks)
        
        # Score all potential headings
        candidates = self._score_heading_candidates(text_blocks, stats)
        
        # Filter and rank candidates
        headings = self._select_headings(candidates, stats)
        
        # Assign hierarchy levels
        leveled_headings = self._assign_levels(headings)
        
        logger.info(f"Detected {len(leveled_headings)} headings")
        return leveled_headings
    
    def _calculate_statistics(self, text_blocks):
        """Calculate document-wide statistics for scoring"""
        stats = {}
        
        # Font size statistics
        sizes = [b["size"] for b in text_blocks]
        stats["avg_size"] = statistics.mean(sizes)
        stats["median_size"] = statistics.median(sizes)
        stats["max_size"] = max(sizes)
        stats["size_std"] = statistics.stdev(sizes) if len(sizes) > 1 else 0
        
        # Font statistics
        font_counter = Counter(b["font"] for b in text_blocks)
        stats["common_fonts"] = [font for font, count in font_counter.most_common(3)]
        
        # Position statistics per page
        page_stats = defaultdict(lambda: {"widths": [], "heights": []})
        for block in text_blocks:
            page_stats[block["page"]]["widths"].append(block["x1"] - block["x0"])
            page_stats[block["page"]]["heights"].append(block["y1"] - block["y0"])
        
        stats["page_stats"] = dict(page_stats)
        
        return stats
    
    def _score_heading_candidates(self, text_blocks, stats):
        """Score each text block as a potential heading"""
        candidates = []
        
        for i, block in enumerate(text_blocks):
            # Skip very short or very long text
            text_len = len(block["text"].strip())
            if text_len < 2 or text_len > 200:
                continue
            
            # Skip excluded patterns
            if self._matches_exclude_pattern(block["text"]):
                continue
            
            score = self._calculate_heading_score(block, text_blocks, stats, i)
            
            if score > 0:
                candidates.append({
                    "score": score,
                    "text": block["text"].strip(),
                    "page": block["page"],
                    "size": block["size"],
                    "is_bold": block["is_bold"],
                    "y0": block["y0"],
                    "original_block": block
                })
        
        return candidates
    
    def _calculate_heading_score(self, block, text_blocks, stats, index):
        """Calculate heading score using multiple heuristics"""
        score = 0
        text = block["text"].strip()
        
        # 1. Font size heuristic
        size_ratio = block["size"] / stats["avg_size"]
        if size_ratio >= 1.5:
            score += 3
        elif size_ratio >= 1.2:
            score += 2
        elif size_ratio >= 1.1:
            score += 1
        
        # 2. Bold text
        if block["is_bold"]:
            score += 2
        
        # 3. Numbered/structured pattern
        if self._has_heading_pattern(text):
            score += 3
        
        # 4. Position and spacing
        spacing_score = self._calculate_spacing_score(block, text_blocks, index)
        score += spacing_score
        
        # 5. Length heuristic (headings are usually not too long)
        if 5 <= len(text) <= 80:
            score += 1
        elif len(text) > 120:
            score -= 1
        
        # 6. Case pattern
        if text.istitle() or text.isupper():
            score += 1
        
        # 7. Standalone line (not part of paragraph)
        if self._is_standalone_line(block, text_blocks, index):
            score += 1
        
        # 8. Font consistency with other potential headings
        font_score = self._calculate_font_consistency_score(block, text_blocks)
        score += font_score
        
        return score
    
    def _has_heading_pattern(self, text):
        """Check if text matches common heading patterns"""
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _matches_exclude_pattern(self, text):
        """Check if text matches patterns to exclude"""
        text_lower = text.lower().strip()
        for pattern in self.exclude_patterns:
            if re.match(pattern, text_lower):
                return True
        return False
    
    def _calculate_spacing_score(self, block, text_blocks, index):
        """Calculate score based on vertical spacing around the text"""
        score = 0
        
        same_page_blocks = [b for b in text_blocks if b["page"] == block["page"]]
        
        # Find blocks before and after
        before_blocks = [b for b in same_page_blocks if b["y1"] < block["y0"]]
        after_blocks = [b for b in same_page_blocks if b["y0"] > block["y1"]]
        
        # Check spacing above
        if before_blocks:
            closest_above = max(before_blocks, key=lambda b: b["y1"])
            space_above = block["y0"] - closest_above["y1"]
            if space_above > 15:  # Significant space above
                score += 1
        
        # Check spacing below
        if after_blocks:
            closest_below = min(after_blocks, key=lambda b: b["y0"])
            space_below = closest_below["y0"] - block["y1"]
            if space_below > 10:  # Some space below
                score += 1
        
        return score
    
    def _is_standalone_line(self, block, text_blocks, index):
        """Check if block is a standalone line (not part of a paragraph)"""
        same_page_blocks = [b for b in text_blocks if b["page"] == block["page"]]
        
        # Find nearby blocks
        nearby_blocks = [
            b for b in same_page_blocks 
            if abs(b["y0"] - block["y0"]) < 5 and b != block
        ]
        
        # If no nearby blocks on same line, it's standalone
        return len(nearby_blocks) == 0
    
    def _calculate_font_consistency_score(self, block, text_blocks):
        """Score based on font consistency with other potential headings"""
        # Find other blocks with similar properties
        similar_blocks = [
            b for b in text_blocks
            if (b["font"] == block["font"] and 
                abs(b["size"] - block["size"]) < 1 and
                b["is_bold"] == block["is_bold"])
        ]
        
        # If there are other similar blocks, they might form a heading style
        if len(similar_blocks) >= 2:
            return 1
        
        return 0
    
    def _select_headings(self, candidates, stats):
        """Select final headings from candidates"""
        if not candidates:
            return []
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top candidates with minimum score threshold
        min_score = max(2, statistics.mean([c["score"] for c in candidates]) * 0.7)
        selected = [c for c in candidates if c["score"] >= min_score]
        
        # Limit to reasonable number
        selected = selected[:50]  # Max 50 headings
        
        # Sort by page and position
        selected.sort(key=lambda x: (x["page"], x["y0"]))
        
        return selected
    
    def _assign_levels(self, headings):
        """Assign H1, H2, H3 levels to headings"""
        if not headings:
            return []
        
        # Group headings by similar properties
        size_groups = self._group_by_size(headings)
        
        # Assign levels based on size groups and patterns
        leveled = []
        
        for heading in headings:
            level = self._determine_level(heading, size_groups, headings)
            
            leveled.append({
                "level": level,
                "text": heading["text"],
                "page": heading["page"]
            })
        
        return leveled
    
    def _group_by_size(self, headings):
        """Group headings by font size"""
        size_groups = {}
        
        for heading in headings:
            size = heading["size"]
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(heading)
        
        # Sort sizes in descending order
        sorted_sizes = sorted(size_groups.keys(), reverse=True)
        
        return {i: size_groups[size] for i, size in enumerate(sorted_sizes)}
    
    def _determine_level(self, heading, size_groups, all_headings):
        """Determine heading level (H1, H2, H3)"""
        # Find which size group this heading belongs to
        heading_size = heading["size"]
        
        # Map size groups to levels
        size_to_group = {}
        for group_idx, size in enumerate(sorted(set(h["size"] for h in all_headings), reverse=True)):
            size_to_group[size] = group_idx
        
        group_idx = size_to_group[heading_size]
        
        # Also consider numbering pattern
        text = heading["text"]
        
        # Check for numbered patterns to refine level
        if re.match(r'^\d+\.?\s+', text):  # 1. Main section
            level = "H1"
        elif re.match(r'^\d+\.\d+\.?\s+', text):  # 1.1 Subsection
            level = "H2"
        elif re.match(r'^\d+\.\d+\.\d+\.?\s+', text):  # 1.1.1 Sub-subsection
            level = "H3"
        else:
            # Use size-based mapping
            if group_idx == 0:
                level = "H1"
            elif group_idx == 1:
                level = "H2"
            else:
                level = "H3"
        
        return level