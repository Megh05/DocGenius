#!/usr/bin/env python3
"""Test current extraction to see what's being extracted"""

from pdf_processor import PDFProcessor
import json

def test_current_extraction():
    """Test what's currently being extracted from each document"""
    processor = PDFProcessor()
    
    # Test files that should be in uploads folder
    files = {
        'TDS': 'attached_assets/SUPPLIER TDS_1755699787623.pdf',
        'MSDS': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf', 
        'COA': 'attached_assets/SUPPLIER COA_1755699787621.pdf'
    }
    
    print("=== CURRENT EXTRACTION TEST ===\n")
    
    for doc_type, file_path in files.items():
        print(f"{doc_type} Document:")
        print("-" * 30)
        
        try:
            if doc_type == 'TDS':
                data = processor.extract_tds_data(file_path)
            elif doc_type == 'MSDS':
                data = processor.extract_msds_data(file_path) 
            elif doc_type == 'COA':
                data = processor.extract_coa_data(file_path)
            
            # Show all extracted data
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"  {key}: {len(value)} items")
                    for i, item in enumerate(value[:3]):
                        print(f"    {i+1}. {item}")
                elif value:
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"  ERROR: {e}")
            
        print()

if __name__ == "__main__":
    test_current_extraction()