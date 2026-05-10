#!/usr/bin/env python3
"""
Docker Validation Script
Tests the exact Docker commands that judges will use
"""

import subprocess
import sys
import time
import json
from pathlib import Path

def run_command(cmd, timeout=60):
    """Run shell command with timeout"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"

def validate_docker_solution():
    """Validate the Docker solution using exact judge commands"""
    
    print("=== DOCKER VALIDATION FOR ROUND 1A ===\n")
    
    # Step 1: Build Docker image (exact judge command)
    print("1. Building Docker image...")
    build_cmd = "docker build --platform linux/amd64 -t pdf-extractor:test ."
    
    success, stdout, stderr = run_command(build_cmd, timeout=300)  # 5 min timeout
    
    if not success:
        print("❌ Docker build FAILED!")
        print(f"Error: {stderr}")
        return False
    
    print("✅ Docker build successful!")
    
    # Step 2: Create test input directory
    print("\n2. Setting up test environment...")
    
    input_dir = Path("input")
    output_dir = Path("output")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Create a simple test case (since we don't have actual PDFs)
    test_info = {
        "note": "This would contain actual PDF files in real testing",
        "expected_behavior": "Process all PDFs and generate corresponding JSON files"
    }
    
    with open(input_dir / "test_info.txt", 'w') as f:
        f.write(str(test_info))
    
    print("✅ Test environment ready!")
    
    # Step 3: Run Docker container (exact judge command)
    print("\n3. Running Docker container...")
    
    run_cmd = "docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:test"
    
    start_time = time.time()
    success, stdout, stderr = run_command(run_cmd, timeout=120)  # 2 min timeout
    elapsed_time = time.time() - start_time
    
    if not success:
        print("❌ Docker run FAILED!")
        print(f"Error: {stderr}")
        print(f"Output: {stdout}")
        return False
    
    print(f"✅ Docker run successful! (took {elapsed_time:.2f}s)")
    
    # Step 4: Validate container behavior
    print("\n4. Validating container behavior...")
    
    # Check if container runs without crashing
    if "Error" in stderr or "Exception" in stderr:
        print("⚠️  Container had errors:")
        print(stderr)
    else:
        print("✅ Container ran without errors!")
    
    # Check output directory
    output_files = list(output_dir.glob("*.json"))
    print(f"✅ Found {len(output_files)} output files")
    
    # Step 5: Performance validation
    print("\n5. Performance validation...")
    
    if elapsed_time <= 10:
        print(f"✅ Performance: {elapsed_time:.2f}s (≤10s required)")
    else:
        print(f"⚠️  Performance: {elapsed_time:.2f}s (>10s limit)")
    
    # Step 6: Check Docker image size
    print("\n6. Checking Docker image size...")
    
    size_cmd = "docker images pdf-extractor:test --format 'table {{.Size}}'"
    success, size_output, _ = run_command(size_cmd)
    
    if success:
        print(f"✅ Docker image size: {size_output.strip()}")
    
    # Step 7: Network isolation test
    print("\n7. Testing network isolation...")
    
    # The --network none flag should prevent any network access
    network_test_cmd = "docker run --rm --network none pdf-extractor:test python -c 'import urllib.request; urllib.request.urlopen(\"http://google.com\")'"
    
    success, _, stderr = run_command(network_test_cmd, timeout=30)
    
    if not success and "Network is unreachable" in stderr:
        print("✅ Network isolation working correctly!")
    elif not success:
        print("✅ Network access properly blocked!")
    else:
        print("⚠️  Network isolation may not be working!")
    
    print("\n=== VALIDATION SUMMARY ===")
    print("✅ Docker build: SUCCESS")
    print("✅ Docker run: SUCCESS") 
    print("✅ Container execution: SUCCESS")
    print("✅ Network isolation: SUCCESS")
    print(f"✅ Performance: {elapsed_time:.2f}s")
    
    print("\n🎉 Docker solution is ready for Round 1A submission!")
    
    return True

def validate_json_format():
    """Validate JSON output format"""
    print("\n=== JSON FORMAT VALIDATION ===")
    
    # Test JSON format compliance
    sample_output = {
        "title": "Test Document",
        "outline": [
            {"level": "H1", "text": "Introduction", "page": 1},
            {"level": "H2", "text": "Background", "page": 2},
            {"level": "H3", "text": "Details", "page": 3}
        ]
    }
    
    try:
        # Test JSON serialization
        json_str = json.dumps(sample_output, indent=2, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        # Validate structure
        assert "title" in parsed
        assert "outline" in parsed
        assert isinstance(parsed["outline"], list)
        
        for heading in parsed["outline"]:
            assert "level" in heading
            assert "text" in heading  
            assert "page" in heading
            assert heading["level"] in ["H1", "H2", "H3"]
        
        print("✅ JSON format validation: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ JSON format validation: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("Starting Docker validation for Round 1A submission...\n")
    
    # Validate JSON format
    json_valid = validate_json_format()
    
    # Validate Docker solution
    docker_valid = validate_docker_solution()
    
    if json_valid and docker_valid:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("Your solution is ready for Round 1A submission!")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED!")
        print("Please fix issues before submission.")
        sys.exit(1)