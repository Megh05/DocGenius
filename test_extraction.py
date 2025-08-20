#!/usr/bin/env python3
"""Test script to analyze PDF extraction capabilities"""

import pdfplumber
import re
import os
from pdf_processor import PDFProcessor

def analyze_supplier_pdfs():
    """Analyze the supplier PDFs to understand their structure"""
    
    supplier_files = {
        'coa': 'attached_assets/SUPPLIER COA_1755699787621.pdf',
        'msds': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf', 
        'tds': 'attached_assets/SUPPLIER TDS_1755699787623.pdf'
    }
    
    processor = PDFProcessor()
    
    for doc_type, file_path in supplier_files.items():
        if os.path.exists(file_path):
            print(f"\n{'='*50}")
            print(f"ANALYZING {doc_type.upper()} DOCUMENT")
            print(f"{'='*50}")
            
            try:
                # Extract raw text
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- PAGE {page_num + 1} ---\n"
                            text += page_text
                
                # Print first 2000 characters to analyze structure
                print("RAW TEXT (first 2000 chars):")
                print(text[:2000])
                print("\n" + "="*30)
                
                # Try to extract key information
                print("KEY INFORMATION EXTRACTION:")
                
                # Product name patterns
                product_patterns = [
                    r'Product[:\s]*(.+?)(?:\n|$)',
                    r'Name[:\s]*(.+?)(?:\n|$)', 
                    r'Product Name[:\s]*(.+?)(?:\n|$)',
                    r'Chemical Name[:\s]*(.+?)(?:\n|$)',
                    r'Trade Name[:\s]*(.+?)(?:\n|$)',
                ]
                
                for pattern in product_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        print(f"Product Name Candidates: {matches[:3]}")
                        break
                
                # CAS number
                cas_match = re.search(r'CAS\s*(?:No\.?|Number)?\s*[:\-]?\s*(\d{2,7}-\d{2}-\d)', text, re.IGNORECASE)
                if cas_match:
                    print(f"CAS Number: {cas_match.group(1)}")
                
                # Molecular formula
                formula_patterns = [
                    r'Molecular\s+formula\s*[:\-]?\s*([A-Z0-9\(\)]+)',
                    r'M\.F\.\s*[:\-]?\s*([A-Z0-9\(\)]+)',
                    r'Formula\s*[:\-]?\s*([A-Z0-9\(\)]+)'
                ]
                
                for pattern in formula_patterns:
                    formula_match = re.search(pattern, text, re.IGNORECASE)
                    if formula_match:
                        print(f"Molecular Formula: {formula_match.group(1)}")
                        break
                
                # Batch/Lot number
                batch_patterns = [
                    r'Batch\s*(?:No\.?|Number)?\s*[:\-]?\s*([A-Z0-9\-]+)',
                    r'Lot\s*(?:No\.?|Number)?\s*[:\-]?\s*([A-Z0-9\-]+)'
                ]
                
                for pattern in batch_patterns:
                    batch_match = re.search(pattern, text, re.IGNORECASE)
                    if batch_match:
                        print(f"Batch/Lot Number: {batch_match.group(1)}")
                        break
                
                # Look for table-like structures
                lines = text.split('\n')
                table_candidates = []
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['test', 'specification', 'result', 'property', 'value']):
                        table_candidates.append((i, line.strip()))
                
                if table_candidates:
                    print(f"\nPOTENTIAL TABLE HEADERS:")
                    for line_num, line in table_candidates[:5]:
                        print(f"Line {line_num}: {line}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

def test_enhanced_extraction():
    """Test the enhanced PDF processor"""
    
    supplier_files = {
        'coa': 'attached_assets/SUPPLIER COA_1755699787621.pdf',
        'msds': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf', 
        'tds': 'attached_assets/SUPPLIER TDS_1755699787623.pdf'
    }
    
    processor = PDFProcessor()
    
    print("TESTING ENHANCED EXTRACTION SYSTEM")
    print("="*60)
    
    try:
        # Test the full process_documents method
        extracted_data = processor.process_documents(supplier_files)
        
        print("\nFULL EXTRACTION RESULTS:")
        print("-" * 40)
        
        # Display key information
        key_fields = ['product_name', 'supplier_name', 'cas_number', 'inci_name', 
                     'molecular_formula', 'batch_number', 'manufacturing_date', 'expiry_date']
        
        for field in key_fields:
            value = extracted_data.get(field, 'Not found')
            print(f"{field.replace('_', ' ').title()}: {value}")
        
        print(f"\nTest Results Found: {len(extracted_data.get('test_results', []))}")
        for i, test in enumerate(extracted_data.get('test_results', [])[:5]):  # Show first 5
            print(f"  {i+1}. {test.get('test_item', 'N/A')} -> {test.get('result', 'N/A')} ({test.get('document_type', 'N/A')})")
        
        print(f"\nSpecifications Found: {len(extracted_data.get('specifications', {}))}")
        for i, (key, value) in enumerate(list(extracted_data.get('specifications', {}).items())[:5]):  # Show first 5
            print(f"  {i+1}. {key}: {value}")
        
        print(f"\nPhysical Properties: {extracted_data.get('physical_properties', {})}")
        print(f"Safety Data: {extracted_data.get('safety_data', {})}")
        
        return extracted_data
        
    except Exception as e:
        print(f"Error in enhanced extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # analyze_supplier_pdfs()
    test_enhanced_extraction()