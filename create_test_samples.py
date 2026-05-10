#!/usr/bin/env python3
"""
Create Sample Test PDFs and Expected Outputs
For testing the PDF extraction solution
"""

import json
import os
from pathlib import Path

def create_test_samples():
    """Create sample test cases for development testing"""
    
    # Create test directories
    test_dir = Path("test_samples")
    test_dir.mkdir(exist_ok=True)
    
    input_dir = test_dir / "input"
    output_dir = test_dir / "output"
    expected_dir = test_dir / "expected"
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    expected_dir.mkdir(exist_ok=True)
    
    # Sample 1: Simple Academic Paper
    sample1_expected = {
        "title": "Understanding Artificial Intelligence",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1},
            {"level": "H2", "text": "What is AI?", "page": 2},
            {"level": "H3", "text": "History of AI", "page": 3},
            {"level": "H3", "text": "Types of AI", "page": 4},
            {"level": "H2", "text": "Machine Learning", "page": 5},
            {"level": "H3", "text": "Supervised Learning", "page": 6},
            {"level": "H3", "text": "Unsupervised Learning", "page": 7},
            {"level": "H1", "text": "Applications", "page": 8},
            {"level": "H2", "text": "Healthcare", "page": 9},
            {"level": "H2", "text": "Finance", "page": 10},
            {"level": "H1", "text": "Conclusion", "page": 11}
        ]
    }
    
    # Sample 2: Technical Documentation
    sample2_expected = {
        "title": "API Documentation Guide",
        "outline": [
            {"level": "H1", "text": "1. Getting Started", "page": 1},
            {"level": "H2", "text": "1.1 Installation", "page": 2},
            {"level": "H3", "text": "1.1.1 Prerequisites", "page": 2},
            {"level": "H3", "text": "1.1.2 Setup Process", "page": 3},
            {"level": "H2", "text": "1.2 Configuration", "page": 4},
            {"level": "H1", "text": "2. API Reference", "page": 5},
            {"level": "H2", "text": "2.1 Authentication", "page": 6},
            {"level": "H2", "text": "2.2 Endpoints", "page": 7},
            {"level": "H3", "text": "2.2.1 User Management", "page": 8},
            {"level": "H3", "text": "2.2.2 Data Operations", "page": 9},
            {"level": "H1", "text": "3. Examples", "page": 10}
        ]
    }
    
    # Sample 3: Complex Document
    sample3_expected = {
        "title": "Research Paper: Advanced Topics in Computer Science",
        "outline": [
            {"level": "H1", "text": "Abstract", "page": 1},
            {"level": "H1", "text": "Introduction", "page": 2},
            {"level": "H1", "text": "Literature Review", "page": 3},
            {"level": "H2", "text": "Previous Work", "page": 4},
            {"level": "H2", "text": "Research Gap", "page": 5},
            {"level": "H1", "text": "Methodology", "page": 6},
            {"level": "H2", "text": "Data Collection", "page": 7},
            {"level": "H2", "text": "Analysis Framework", "page": 8},
            {"level": "H3", "text": "Statistical Methods", "page": 9},
            {"level": "H3", "text": "Validation Techniques", "page": 10},
            {"level": "H1", "text": "Results", "page": 11},
            {"level": "H2", "text": "Quantitative Results", "page": 12},
            {"level": "H2", "text": "Qualitative Analysis", "page": 13},
            {"level": "H1", "text": "Discussion", "page": 14},
            {"level": "H1", "text": "Conclusion", "page": 15},
            {"level": "H1", "text": "References", "page": 16}
        ]
    }
    
    # Save expected outputs
    samples = [
        ("sample1.json", sample1_expected),
        ("sample2.json", sample2_expected),
        ("sample3.json", sample3_expected)
    ]
    
    for filename, expected in samples:
        with open(expected_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(expected, f, indent=2, ensure_ascii=False)
    
    # Create README for test samples
    readme_content = """# Test Samples for PDF Extractor

This directory contains sample test cases for validating the PDF extraction solution.

## Structure

- `input/` - Place test PDF files here
- `output/` - Generated JSON outputs will appear here
- `expected/` - Expected outputs for comparison

## Test Cases

1. **sample1.json** - Simple academic paper structure
2. **sample2.json** - Technical documentation with numbered sections
3. **sample3.json** - Complex research paper with multiple levels

## Usage

1. Place corresponding PDF files in `input/` directory
2. Run the extraction solution
3. Compare outputs in `output/` with expected results in `expected/`

## Validation

Use the test runner to automatically validate:

```bash
python test_solution.py
```

This will check:
- Output format compliance
- Performance constraints
- Edge case handling
- Multilingual support
"""
    
    with open(test_dir / "README.md", 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created test samples in {test_dir}/")
    print("📁 Directory structure:")
    print(f"   {input_dir}/ - Place test PDFs here")
    print(f"   {output_dir}/ - Generated outputs")
    print(f"   {expected_dir}/ - Expected results")
    
    return test_dir

if __name__ == "__main__":
    create_test_samples()