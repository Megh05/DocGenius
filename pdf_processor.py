import pdfplumber
import re
import logging
from typing import Dict, List, Any

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_documents(self, file_paths: Dict[str, str]) -> Dict[str, Any]:
        """Process all three document types and extract relevant data"""
        extracted_data = {
            'product_name': '',
            'supplier_name': '',
            'cas_number': '',
            'inci_name': '',
            'molecular_formula': '',
            'batch_number': '',
            'manufacturing_date': '',
            'expiry_date': '',
            'test_results': [],
            'specifications': {},
            'safety_data': {},
            'physical_properties': {}
        }
        
        try:
            # Process COA
            if 'coa' in file_paths:
                coa_data = self.extract_coa_data(file_paths['coa'])
                extracted_data.update(coa_data)
            
            # Process MSDS
            if 'msds' in file_paths:
                msds_data = self.extract_msds_data(file_paths['msds'])
                extracted_data.update(msds_data)
            
            # Process TDS
            if 'tds' in file_paths:
                tds_data = self.extract_tds_data(file_paths['tds'])
                extracted_data.update(tds_data)
                
        except Exception as e:
            self.logger.error(f"Error processing documents: {str(e)}")
            raise
        
        return extracted_data
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
        return text
    
    def extract_coa_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Certificate of Analysis"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract product name
        product_match = re.search(r'Product Name:\s*(.+)', text, re.IGNORECASE)
        if product_match:
            data['product_name'] = product_match.group(1).strip()
        
        # Extract INCI name
        inci_match = re.search(r'INCI Name:\s*(.+)', text, re.IGNORECASE)
        if inci_match:
            data['inci_name'] = inci_match.group(1).strip()
        
        # Extract batch number
        batch_match = re.search(r'Batch Number:\s*(.+)', text, re.IGNORECASE)
        if batch_match:
            data['batch_number'] = batch_match.group(1).strip()
        
        # Extract manufacturing date
        mfg_match = re.search(r'Manufacturing Date:\s*(.+)', text, re.IGNORECASE)
        if mfg_match:
            data['manufacturing_date'] = mfg_match.group(1).strip()
        
        # Extract expiry date
        exp_match = re.search(r'Expiry Date:\s*(.+)', text, re.IGNORECASE)
        if exp_match:
            data['expiry_date'] = exp_match.group(1).strip()
        
        # Extract test results
        test_results = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Test Items' in line and 'Specifications' in line and 'Results' in line:
                # Found header, extract subsequent test data
                for j in range(i+1, min(i+20, len(lines))):
                    test_line = lines[j].strip()
                    if test_line and not test_line.startswith('ISSUED DATE'):
                        parts = re.split(r'\s{2,}', test_line)
                        if len(parts) >= 3:
                            test_results.append({
                                'test_item': parts[0].strip(),
                                'specification': parts[1].strip(),
                                'result': parts[2].strip(),
                                'document_type': 'COA'
                            })
        
        data['test_results'] = test_results
        return data
    
    def extract_msds_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Material Safety Data Sheet"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract CAS number
        cas_match = re.search(r'CAS\s*No\.?\s*[:\-]?\s*(\d{2,7}-\d{2}-\d)', text, re.IGNORECASE)
        if cas_match:
            data['cas_number'] = cas_match.group(1).strip()
        
        # Extract molecular formula
        formula_patterns = [
            r'Molecular formula\s*[:\-]?\s*([A-Z0-9\(\)]+n?)',
            r'M\.F\.\s*[:\-]?\s*([A-Z0-9\(\)]+n?)',
            r'Formula\s*[:\-]?\s*([A-Z0-9\(\)]+n?)'
        ]
        
        for pattern in formula_patterns:
            formula_match = re.search(pattern, text, re.IGNORECASE)
            if formula_match:
                data['molecular_formula'] = formula_match.group(1).strip()
                break
        
        # Extract supplier name
        supplier_patterns = [
            r'Company Name:\s*(.+)',
            r'Manufacturer:\s*(.+)',
            r'Supplier:\s*(.+)'
        ]
        
        for pattern in supplier_patterns:
            supplier_match = re.search(pattern, text, re.IGNORECASE)
            if supplier_match:
                data['supplier_name'] = supplier_match.group(1).strip()
                break
        
        # Extract safety data
        safety_data = {}
        
        # pH value
        ph_match = re.search(r'pH\s*value?\s*[:\-]?\s*([\d\.\-\s]+)', text, re.IGNORECASE)
        if ph_match:
            safety_data['ph'] = ph_match.group(1).strip()
        
        # Physical properties
        physical_props = {}
        
        # Appearance
        appearance_match = re.search(r'Appearance\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
        if appearance_match:
            physical_props['appearance'] = appearance_match.group(1).strip()
        
        # Solubility
        solubility_match = re.search(r'Solubility\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
        if solubility_match:
            physical_props['solubility'] = solubility_match.group(1).strip()
        
        data['safety_data'] = safety_data
        data['physical_properties'] = physical_props
        
        return data
    
    def extract_tds_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Technical Data Sheet"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract specifications
        specifications = {}
        
        # Look for specification table
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Specifications' in line or 'Test Items' in line:
                # Extract specifications data
                for j in range(i+1, min(i+30, len(lines))):
                    spec_line = lines[j].strip()
                    if spec_line and not any(x in spec_line.lower() for x in ['recommended', 'use', 'package', 'storage']):
                        parts = re.split(r'\s{2,}', spec_line)
                        if len(parts) >= 2:
                            specifications[parts[0].strip()] = parts[1].strip()
        
        data['specifications'] = specifications
        
        # Extract recommended use level
        use_level_match = re.search(r'Recommended use level:\s*(.+)', text, re.IGNORECASE)
        if use_level_match:
            data['recommended_use_level'] = use_level_match.group(1).strip()
        
        # Extract use method
        use_method_match = re.search(r'Use Method:\s*(.+)', text, re.IGNORECASE)
        if use_method_match:
            data['use_method'] = use_method_match.group(1).strip()
        
        # Extract storage conditions
        storage_match = re.search(r'Storage:\s*(.+)', text, re.IGNORECASE)
        if storage_match:
            data['storage_conditions'] = storage_match.group(1).strip()
        
        # Extract shelf life
        shelf_life_match = re.search(r'Shelf life:\s*(.+)', text, re.IGNORECASE)
        if shelf_life_match:
            data['shelf_life'] = shelf_life_match.group(1).strip()
        
        return data
