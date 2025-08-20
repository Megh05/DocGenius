#!/usr/bin/env python3
"""Simple test to verify enhanced PDF extraction"""

from pdf_processor import PDFProcessor

def test_basic_extraction():
    """Test basic extraction functionality"""
    print("Testing Enhanced PDF Processor...")
    
    processor = PDFProcessor()
    
    # Test with all three files
    files = {
        'TDS': 'attached_assets/SUPPLIER TDS_1755699787623.pdf',
        'MSDS': 'attached_assets/SUPPLIER MSDS_1755699787622.pdf',
        'COA': 'attached_assets/SUPPLIER COA_1755699787621.pdf'
    }
    
    for doc_type, file_path in files.items():
        print(f"\n{doc_type} Extraction:")
        print("-" * 40)
        
        try:
            if doc_type == 'TDS':
                data = processor.extract_tds_data(file_path)
            elif doc_type == 'MSDS':
                data = processor.extract_msds_data(file_path)
            elif doc_type == 'COA':
                data = processor.extract_coa_data(file_path)
            
            # Display key information
            key_fields = ['product_name', 'cas_number', 'inci_name', 'molecular_formula', 'supplier_name']
            for field in key_fields:
                value = data.get(field, 'Not found')
                if value and value != 'Not found':
                    print(f"  {field}: {value}")
            
            if data.get('test_results'):
                print(f"  Test results: {len(data['test_results'])} found")
                for i, test in enumerate(data['test_results'][:3]):
                    print(f"    {i+1}. {test.get('test_item', 'N/A')}: {test.get('result', 'N/A')}")
        
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_basic_extraction()