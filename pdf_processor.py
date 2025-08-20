import pdfplumber
import re
import logging
from typing import Dict, List, Any
import tempfile
import os

# Optional imports for OCR functionality
try:
    import pytesseract
    from pdf2image import convert_from_path
    import numpy as np
    # Try importing cv2 with fallback
    try:
        import cv2
        CV2_AVAILABLE = True
    except ImportError:
        CV2_AVAILABLE = False
        print("OpenCV not available, using basic image processing")
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"OCR dependencies not available: {e}")
    print("PDF text extraction will use pdfplumber only")

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
        """Extract text from PDF file using multiple methods"""
        text = ""
        total_pages = 0
        pages_with_text = 0
        
        try:
            # First try pdfplumber (for text-based PDFs)
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                self.logger.info(f"Processing {total_pages} pages from {file_path}")
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 10:
                        text += f"\n--- PAGE {i+1} ---\n" + page_text + "\n"
                        pages_with_text += 1
                    else:
                        self.logger.debug(f"Page {i+1} has minimal or no text")
            
            self.logger.info(f"Extracted text from {pages_with_text}/{total_pages} pages")
            
            # If very few pages had text or total text is minimal, try OCR
            if (pages_with_text < total_pages * 0.5 or len(text.strip()) < 200) and OCR_AVAILABLE:
                self.logger.info(f"Limited text extraction ({pages_with_text}/{total_pages} pages), attempting OCR for {file_path}")
                ocr_text = self.extract_text_with_ocr(file_path)
                if len(ocr_text.strip()) > len(text.strip()):
                    self.logger.info("OCR provided better results, using OCR text")
                    text = ocr_text
                else:
                    self.logger.info("Original extraction was better, keeping original text")
                    
        except Exception as e:
            self.logger.error(f"Error extracting text from {file_path}: {str(e)}")
            # Try OCR as fallback
            if OCR_AVAILABLE:
                try:
                    self.logger.info("Attempting OCR as fallback")
                    text = self.extract_text_with_ocr(file_path)
                except Exception as ocr_error:
                    self.logger.error(f"OCR fallback failed: {str(ocr_error)}")
                    raise e
            else:
                raise e
        
        return text
    
    def extract_text_with_ocr(self, file_path: str) -> str:
        """Extract text using OCR from PDF"""
        if not OCR_AVAILABLE:
            raise Exception("OCR dependencies not available")
            
        text = ""
        try:
            # Convert PDF pages to images
            images = convert_from_path(file_path, dpi=300)
            
            for i, image in enumerate(images):
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                if CV2_AVAILABLE:
                    # Preprocess image for better OCR using OpenCV
                    if len(img_array.shape) == 3:
                        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    else:
                        gray = img_array
                    
                    # Apply image processing to improve OCR accuracy
                    gray = cv2.medianBlur(gray, 3)
                    
                    # Use Tesseract to extract text
                    page_text = pytesseract.image_to_string(gray, lang='eng+chi_sim')
                else:
                    # Use Tesseract directly on the image without OpenCV preprocessing
                    page_text = pytesseract.image_to_string(image, lang='eng+chi_sim')
                
                text += f"\n--- PAGE {i+1} (OCR) ---\n" + page_text
                
        except Exception as e:
            self.logger.error(f"OCR extraction failed for {file_path}: {str(e)}")
            raise
            
        return text
    
    def extract_coa_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Certificate of Analysis"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract product name - enhanced patterns
        product_patterns = [
            r'Product\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Product\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Chemical\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Trade\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'产品名称\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in product_patterns:
            product_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if product_match:
                product_name = product_match.group(1).strip()
                if len(product_name) > 2:  # Basic validation
                    data['product_name'] = product_name
                    break
        
        # Extract INCI name - enhanced patterns
        inci_patterns = [
            r'INCI\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'INCI\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'国际化妆品原料命名\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese INCI
        ]
        
        for pattern in inci_patterns:
            inci_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if inci_match:
                data['inci_name'] = inci_match.group(1).strip()
                break
        
        # Extract batch/lot number - enhanced patterns
        batch_patterns = [
            r'Batch\s+(?:No\.?|Number)\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'Lot\s+(?:No\.?|Number)\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'批号\s*[:\-]?\s*([A-Z0-9\-]+)',  # Chinese
            r'Batch\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'Lot\s*[:\-]?\s*([A-Z0-9\-]+)',
        ]
        
        for pattern in batch_patterns:
            batch_match = re.search(pattern, text, re.IGNORECASE)
            if batch_match:
                data['batch_number'] = batch_match.group(1).strip()
                break
        
        # Extract dates - enhanced patterns
        date_patterns = [
            r'Manufacturing\s+Date\s*[:\-]?\s*([0-9\-\/\.]+)',
            r'Mfg\.?\s+Date\s*[:\-]?\s*([0-9\-\/\.]+)',
            r'生产日期\s*[:\-]?\s*([0-9\-\/\.]+)',  # Chinese
            r'Expiry\s+Date\s*[:\-]?\s*([0-9\-\/\.]+)',
            r'Exp\.?\s+Date\s*[:\-]?\s*([0-9\-\/\.]+)',
            r'有效期\s*[:\-]?\s*([0-9\-\/\.]+)',  # Chinese
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match and ('Manufacturing' in pattern or 'Mfg' in pattern or '生产' in pattern):
                data['manufacturing_date'] = date_match.group(1).strip()
            elif date_match and ('Expiry' in pattern or 'Exp' in pattern or '有效' in pattern):
                data['expiry_date'] = date_match.group(1).strip()
        
        # Extract test results - enhanced table detection
        test_results = []
        lines = text.split('\n')
        
        # Look for table headers in multiple languages
        table_header_patterns = [
            r'Test\s+Items?.*Specification.*Result',
            r'Item.*Specification.*Result',
            r'Parameter.*Specification.*Result',
            r'Property.*Value',
            r'检测项目.*规格.*结果',  # Chinese
        ]
        
        for i, line in enumerate(lines):
            line_clean = re.sub(r'\s+', ' ', line.strip())
            for header_pattern in table_header_patterns:
                if re.search(header_pattern, line_clean, re.IGNORECASE):
                    # Found table header, extract data rows
                    for j in range(i+1, min(i+30, len(lines))):
                        test_line = lines[j].strip()
                        if not test_line or len(test_line) < 5:
                            continue
                        if any(x in test_line.lower() for x in ['issued', 'page', 'date', 'signature', 'approved', 'tel:', 'email:', 'address']):
                            continue
                            
                        # Try different parsing methods
                        parts = None
                        
                        # Method 1: Tab or multiple spaces
                        if '\t' in test_line:
                            parts = test_line.split('\t')
                        elif re.search(r'\s{3,}', test_line):
                            parts = re.split(r'\s{3,}', test_line)
                        else:
                            # Method 2: Smart splitting on whitespace
                            parts = re.split(r'\s{2,}', test_line)
                        
                        if parts and len(parts) >= 2:
                            test_item = parts[0].strip()
                            if len(parts) >= 3:
                                specification = parts[1].strip()
                                result = parts[2].strip()
                            else:
                                specification = ''
                                result = parts[1].strip()
                            
                            if test_item and result:
                                test_results.append({
                                    'test_item': test_item,
                                    'specification': specification,
                                    'result': result,
                                    'document_type': 'COA'
                                })
                    break
        
        data['test_results'] = test_results
        return data
    
    def extract_msds_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Material Safety Data Sheet"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract product name from MSDS as well - enhanced
        product_patterns = [
            r'Product\s*name\s*(.+?)(?:\n|CAS)',  # Stop at CAS or newline
            r'Product\s+(?:name|identifier)\s*[:\-]?\s*(.+?)(?:\n|CAS)',
            r'Productname\s*(.+?)(?:\n|CAS)',  # No space version
            r'Chemical\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in product_patterns:
            product_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if product_match:
                product_name = product_match.group(1).strip()
                # Clean up common artifacts
                product_name = re.sub(r'\s+', ' ', product_name)
                if len(product_name) > 2 and 'section' not in product_name.lower() and 'identifier' not in product_name.lower():
                    data['product_name'] = product_name
                    break
        
        # Extract CAS number - enhanced
        cas_patterns = [
            r'CAS\s*(?:No\.?|Number)?\s*[:\-]?\s*(\d{2,7}-\d{2}-\d)',
            r'CAS-No\.\s*(\d{2,7}-\d{2}-\d)',
            r'CAS编号\s*[:\-]?\s*(\d{2,7}-\d{2}-\d)',  # Chinese
        ]
        
        for pattern in cas_patterns:
            cas_match = re.search(pattern, text, re.IGNORECASE)
            if cas_match:
                data['cas_number'] = cas_match.group(1).strip()
                break
        
        # Extract molecular formula - enhanced
        formula_patterns = [
            r'Molecular\s+formula\s*[:\-]?\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',
            r'Formula\s*[:\-]?\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',
            r'M\.F\.\s*[:\-]?\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',
            r'分子式\s*[:\-]?\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',  # Chinese
        ]
        
        for pattern in formula_patterns:
            formula_match = re.search(pattern, text, re.IGNORECASE)
            if formula_match:
                formula = formula_match.group(1).strip()
                if len(formula) > 1:
                    data['molecular_formula'] = formula
                    break
        
        # Extract supplier/manufacturer name - enhanced
        supplier_patterns = [
            r'Manufacturer\s*[:\-]?\s*(.+?)(?:\n|Address)',
            r'Company\s+Name\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Supplier\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'制造商\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in supplier_patterns:
            supplier_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if supplier_match:
                supplier_name = supplier_match.group(1).strip()
                if len(supplier_name) > 3:
                    data['supplier_name'] = supplier_name
                    break
        
        # Extract INCI name if available in MSDS - enhanced
        inci_patterns = [
            r'INCI\s*(?:Name)?\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Synonyms\s*[:\-]?\s*(.+?)(?:\n|Formula)',  # Sometimes INCI is in synonyms
        ]
        
        for pattern in inci_patterns:
            inci_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if inci_match:
                inci_name = inci_match.group(1).strip()
                # Filter out obvious non-INCI content
                if (len(inci_name) > 2 and not any(x in inci_name.lower() for x in 
                    ['poly', 'according', 'required', 'disposal', 'none'])):
                    data['inci_name'] = inci_name
                    break
        
        # Extract safety data
        safety_data = {}
        
        # pH value - enhanced
        ph_patterns = [
            r'pH\s*(?:value)?\s*[:\-]?\s*([\d\.\-\~\s]+)',
            r'pH值\s*[:\-]?\s*([\d\.\-\~\s]+)',  # Chinese
        ]
        
        for pattern in ph_patterns:
            ph_match = re.search(pattern, text, re.IGNORECASE)
            if ph_match:
                safety_data['ph'] = ph_match.group(1).strip()
                break
        
        # Physical properties
        physical_props = {}
        
        # Appearance - enhanced
        appearance_patterns = [
            r'Appearance\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Physical\s+state\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'外观\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in appearance_patterns:
            appearance_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if appearance_match:
                appearance = appearance_match.group(1).strip()
                if len(appearance) > 2:
                    physical_props['appearance'] = appearance
                    break
        
        # Solubility - enhanced
        solubility_patterns = [
            r'Solubility\s*(?:in\s+water)?\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Water\s+solubility\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'溶解性\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in solubility_patterns:
            solubility_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if solubility_match:
                physical_props['solubility'] = solubility_match.group(1).strip()
                break
        
        data['safety_data'] = safety_data
        data['physical_properties'] = physical_props
        
        return data
    
    def extract_tds_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Technical Data Sheet"""
        text = self.extract_text_from_pdf(file_path)
        data = {}
        
        # Extract product information from TDS
        product_patterns = [
            r'Product\s*name\s*(.+?)(?:\n|$)',
            r'TDS\s+of\s+(.+?)(?:\n|$)',
            r'产品名称\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in product_patterns:
            product_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if product_match:
                product_name = product_match.group(1).strip()
                if len(product_name) > 2:
                    data['product_name'] = product_name
                    break
        
        # Extract INCI from TDS
        inci_patterns = [
            r'INCI\s*(.+?)(?:\n|$)',
            r'INCI\s+Name\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in inci_patterns:
            inci_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if inci_match:
                data['inci_name'] = inci_match.group(1).strip()
                break
        
        # Extract CAS from TDS
        cas_patterns = [
            r'CAS\s*(\d{2,7}-\d{2}-\d)',
        ]
        
        for pattern in cas_patterns:
            cas_match = re.search(pattern, text, re.IGNORECASE)
            if cas_match:
                data['cas_number'] = cas_match.group(1).strip()
                break
        
        # Extract molecular formula from TDS - enhanced
        formula_patterns = [
            r'Molecularformula\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',
            r'Molecular\s+formula\s*[（(]?([A-Z0-9\(\)]+n?)[）)]?',
            r'Formula\s*[（(]?\s*([A-Z0-9H\(\)]{3,}n?)\s*[）)]?',  # More flexible pattern
            r'[（(]\s*([C][H0-9N\(\)O]+n?)\s*[）)]',  # Pattern in parentheses starting with C
        ]
        
        for pattern in formula_patterns:
            formula_match = re.search(pattern, text, re.IGNORECASE)
            if formula_match:
                formula = formula_match.group(1).strip()
                # Validate it looks like a molecular formula
                if len(formula) > 2 and any(c.isdigit() for c in formula):
                    data['molecular_formula'] = formula
                    break
        
        # Extract appearance from TDS
        appearance_patterns = [
            r'Appearance\s*(.+?)(?:\n|$)',
            r'Physical\s+form\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in appearance_patterns:
            appearance_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if appearance_match:
                appearance = appearance_match.group(1).strip()
                if len(appearance) > 3:
                    if 'physical_properties' not in data:
                        data['physical_properties'] = {}
                    data['physical_properties']['appearance'] = appearance
                    break
        
        # Extract specifications table - enhanced
        specifications = {}
        test_results = []
        lines = text.split('\n')
        
        # Look for specification tables with multiple patterns
        spec_patterns = [
            r'Specification',
            r'Test\s+Items?',
            r'Parameter',
            r'Property',
            r'Analysis',
        ]
        
        for i, line in enumerate(lines):
            line_clean = re.sub(r'\s+', ' ', line.strip())
            
            # Check if this line contains specification headers
            is_spec_header = any(re.search(pattern, line_clean, re.IGNORECASE) for pattern in spec_patterns)
            
            if is_spec_header and len(line_clean) > 10:
                # Found specification section, extract data
                for j in range(i+1, min(i+50, len(lines))):
                    spec_line = lines[j].strip()
                    if not spec_line or len(spec_line) < 3:
                        continue
                    
                    # Skip obvious non-data lines
                    skip_keywords = ['recommended', 'use', 'package', 'storage', 'shelf', 'product', 'tel:', 'email:', 'address', 'website', 'web:', 'add:']
                    if any(keyword in spec_line.lower() for keyword in skip_keywords):
                        continue
                    
                    # Try to parse the specification line
                    parts = None
                    
                    # Check for various delimiters
                    if '≥' in spec_line or '≤' in spec_line or '±' in spec_line:
                        # Likely a specification with value
                        if re.search(r'\s{2,}', spec_line):
                            parts = re.split(r'\s{2,}', spec_line)
                        elif '\t' in spec_line:
                            parts = spec_line.split('\t')
                        else:
                            # Try to split on the symbol
                            for symbol in ['≥', '≤', '±']:
                                if symbol in spec_line:
                                    before, after = spec_line.split(symbol, 1)
                                    parts = [before.strip(), symbol + after.strip()]
                                    break
                    
                    elif re.search(r'\s{2,}', spec_line):
                        parts = re.split(r'\s{2,}', spec_line)
                    elif '\t' in spec_line:
                        parts = spec_line.split('\t')
                    else:
                        # Single item, might be parameter name only
                        parts = [spec_line]
                    
                    if parts and len(parts) >= 1:
                        param = parts[0].strip()
                        value = parts[1].strip() if len(parts) > 1 else ''
                        
                        if param and len(param) > 1:
                            if value:
                                specifications[param] = value
                                # Also add as test result for COA generation
                                test_results.append({
                                    'test_item': param,
                                    'specification': value,
                                    'result': value,  # For TDS, result often equals specification
                                    'document_type': 'TDS'
                                })
                            else:
                                specifications[param] = 'As specified'
                break
        
        data['specifications'] = specifications
        data['test_results'] = test_results
        
        # Extract usage information - enhanced
        usage_patterns = [
            r'Recommended\s+use\s+level\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'Use\s+level\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'推荐用量\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in usage_patterns:
            use_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if use_match:
                data['recommended_use_level'] = use_match.group(1).strip()
                break
        
        # Extract usage description
        usage_desc_patterns = [
            r'Product\s+Usage\s*(.+?)(?:\n\n|Package)',
            r'Application\s*[:\-]?\s*(.+?)(?:\n\n|Package)',
            r'Usage\s*[:\-]?\s*(.+?)(?:\n\n|Package)',
        ]
        
        for pattern in usage_desc_patterns:
            usage_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if usage_match:
                data['product_usage'] = usage_match.group(1).strip()
                break
        
        # Extract storage conditions - enhanced
        storage_patterns = [
            r'Storage\s+Conditions\s*(.+?)(?:\n\n|Shelf)',
            r'Storage\s*[:\-]?\s*(.+?)(?:\n\n|Shelf)',
            r'存储条件\s*[:\-]?\s*(.+?)(?:\n\n|$)',  # Chinese
        ]
        
        for pattern in storage_patterns:
            storage_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if storage_match:
                data['storage_conditions'] = storage_match.group(1).strip()
                break
        
        # Extract shelf life - enhanced
        shelf_patterns = [
            r'Shelf\s+life\s*(.+?)(?:\n|$)',
            r'Shelf\s*life\s*[:\-]?\s*(.+?)(?:\n|$)',
            r'有效期\s*[:\-]?\s*(.+?)(?:\n|$)',  # Chinese
        ]
        
        for pattern in shelf_patterns:
            shelf_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if shelf_match:
                data['shelf_life'] = shelf_match.group(1).strip()
                break
        
        return data
