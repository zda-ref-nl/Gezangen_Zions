#!/usr/bin/env python3
"""
Gezangen Zions Processing Examples and Usage Guide

This script demonstrates various ways to use the hymn splitting tools.
"""

import os
import subprocess
import time

def run_command(cmd, description):
    """Run a command and show results."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        print(f"✅ Completed in {elapsed:.1f} seconds")
        
        if result.stdout:
            print("Output:")
            print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")  
            print(result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_file_stats(directory):
    """Show statistics about created files."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        return
        
    files = []
    total_size = 0
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.pdf'):
                filepath = os.path.join(root, filename)
                size = os.path.getsize(filepath)
                files.append((filename, size))
                total_size += size
    
    print(f"\n📊 File Statistics:")
    print(f"Total PDF files: {len(files)}")
    print(f"Total size: {total_size / (1024*1024):.1f} MB")
    print(f"Average size: {(total_size / len(files) / 1024):.0f} KB per file" if files else "No files")
    
    if files:
        print(f"\nSample files:")
        for filename, size in sorted(files)[:5]:
            print(f"  {filename}: {size//1024} KB")

def main():
    """Run usage examples."""
    print("🎵 Gezangen Zions Processing - Usage Examples")
    print("="*60)
    
    # Check if required files exist
    required_files = [
        "#Gezangen Zions.original.pdf",
        "gezangen-zions.json", 
        "complete_processor.py",
        "fast_hymn_splitter.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return 1
    
    print("✅ All required files present")
    
    # Example 1: Quick test with first 5 hymns
    success = run_command(
        "python3 fast_hymn_splitter.py --count 5 --output test_output", 
        "Quick test - First 5 hymns"
    )
    
    if success:
        show_file_stats("test_output")
    
    # Example 2: Process first 50 hymns with full processor
    success = run_command(
        "python3 complete_processor.py --max-hymns 50 --output demo_output",
        "Demo processing - First 50 hymns with topics and index"
    )
    
    if success:
        show_file_stats("demo_output")
        
        # Show additional files created
        additional_files = [
            "demo_output/index.html",
            "demo_output/hymn_index.csv"
        ]
        
        print("\n📋 Additional files created:")
        for file in additional_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  {file}: {size} bytes")
    
    # Example 3: Show how to process specific range
    print(f"\n{'='*60}")
    print("📚 Additional Usage Examples")
    print('='*60)
    
    examples = [
        ("python3 complete_processor.py", "Process ALL hymns (532 total)"),
        ("python3 complete_processor.py --max-hymns 100", "Process first 100 hymns"),
        ("python3 fast_hymn_splitter.py --start 25 --count 25", "Process hymns 25-50"),
        ("python3 complete_processor.py --output church_hymns --max-hymns 200", "Custom output directory"),
        ("python3 complete_processor.py --quiet", "Minimal output")
    ]
    
    for cmd, desc in examples:
        print(f"\n💡 {desc}:")
        print(f"   {cmd}")
    
    # Show expected output structure
    print(f"\n{'='*60}")
    print("📁 Expected Output Structure")
    print('='*60)
    
    structure = """
    output_directory/
    ├── 001_Hymn_Title.pdf              # Individual hymn PDFs
    ├── 002_Another_Hymn.pdf
    ├── ...
    ├── 532_Final_Hymn.pdf
    ├── index.html                      # Browse-able HTML index
    ├── hymn_index.csv                  # Spreadsheet-compatible index
    └── by_topic/                       # Organized by theological topics
        ├── Eere_en_Lofzangen/          # Praise and honor songs
        │   ├── 001_Hymn_Title.pdf
        │   └── ...
        ├── De_Heilige_Geest/           # Holy Spirit songs  
        ├── Jezus_Leven_op_Aarde/       # Jesus' life on earth
        └── ...
    """
    
    print(structure)
    
    # Performance estimates
    print(f"\n{'='*60}")
    print("⚡ Performance Estimates")  
    print('='*60)
    
    estimates = [
        ("First 10 hymns", "~10-15 seconds", "~1MB"),
        ("First 50 hymns", "~30-45 seconds", "~5MB"), 
        ("First 100 hymns", "~1-2 minutes", "~10MB"),
        ("All 532 hymns", "~5-10 minutes", "~50-75MB")
    ]
    
    for task, time_est, size_est in estimates:
        print(f"  {task:<15}: {time_est:<15} → {size_est}")
    
    print(f"\n✅ Usage examples completed!")
    print(f"💡 Tip: Start with --max-hymns 10 for testing, then process larger batches")
    
    return 0

if __name__ == "__main__":
    exit(main())