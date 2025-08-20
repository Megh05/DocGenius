#!/usr/bin/env python3
"""Test OCR extraction directly"""

import logging
logging.basicConfig(level=logging.INFO)

from pdf_processor import PDFProcessor

def test_ocr_extraction():
    """Test OCR extraction on the supplier files"""
    processor = PDFProcessor()
    
    # Test files
    files = {
        'MSDS': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf',
        'TDS': 'attached_assets/SUPPLIER TDS_1755699787623.pdf',
        'COA': 'attached_assets/SUPPLIER COA_1755699787621.pdf'
    }
    
    for doc_type, file_path in files.items():
        print(f"\n{doc_type} OCR Test:")
        print("=" * 50)
        
        try:
            # Test direct OCR extraction
            ocr_text = processor.extract_text_with_ocr(file_path)
            print(f"OCR text length: {len(ocr_text)} characters")
            
            # Count pages in OCR output
            page_count = ocr_text.count("--- PAGE")
            print(f"Pages detected in OCR: {page_count}")
            
            # Show first 500 characters
            preview = ocr_text[:500].replace('\n', ' ')
            print(f"Preview: {preview}...")
            
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_ocr_extraction()