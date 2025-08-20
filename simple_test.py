#!/usr/bin/env python3
"""Simple test to verify enhanced PDF extraction"""

from pdf_processor import PDFProcessor

def test_basic_extraction():
    """Test basic extraction functionality"""
    print("Testing Enhanced PDF Processor...")
    
    processor = PDFProcessor()
    
    # Test with the TDS file which we know has readable text
    tds_file = 'attached_assets/SUPPLIER TDS_1755699787623.pdf'
    
    try:
        print("Extracting from TDS...")
        tds_data = processor.extract_tds_data(tds_file)
        
        print("\nTDS Extraction Results:")
        print("-" * 30)
        for key, value in tds_data.items():
            if isinstance(value, dict) and len(value) > 0:
                print(f"{key}: {len(value)} items")
                for sub_key, sub_value in list(value.items())[:3]:  # Show first 3
                    print(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list) and len(value) > 0:
                print(f"{key}: {len(value)} items")
                for item in value[:3]:  # Show first 3
                    print(f"  {item}")
            else:
                print(f"{key}: {value}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_extraction()