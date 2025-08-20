#!/usr/bin/env python3
"""Debug script to check PDF page counts and content"""

import pdfplumber
import os

def check_pdf_pages():
    """Check how many pages each PDF has and content distribution"""
    
    supplier_files = {
        'COA': 'attached_assets/SUPPLIER COA_1755699787621.pdf',
        'MSDS': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf', 
        'TDS': 'attached_assets/SUPPLIER TDS_1755699787623.pdf'
    }
    
    for doc_type, file_path in supplier_files.items():
        if os.path.exists(file_path):
            print(f"\n{doc_type} Document Analysis:")
            print("=" * 40)
            
            try:
                with pdfplumber.open(file_path) as pdf:
                    print(f"Total pages: {len(pdf.pages)}")
                    
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text:
                            text_length = len(text.strip())
                            print(f"Page {i+1}: {text_length} characters")
                            if text_length > 0:
                                # Show first 200 chars of each page
                                preview = text.strip()[:200].replace('\n', ' ')
                                print(f"  Preview: {preview}...")
                        else:
                            print(f"Page {i+1}: No text extracted (likely image-based)")
                            
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    check_pdf_pages()