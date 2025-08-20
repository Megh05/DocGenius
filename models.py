from app import db
from datetime import datetime

class DocumentSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_product_name = db.Column(db.String(200), nullable=False)
    company_product_name = db.Column(db.String(200), nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50))
    inci_name = db.Column(db.String(200))
    molecular_formula = db.Column(db.String(100))
    batch_number = db.Column(db.String(100))
    manufacturing_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # File paths
    supplier_coa_path = db.Column(db.String(500))
    supplier_msds_path = db.Column(db.String(500))
    supplier_tds_path = db.Column(db.String(500))
    
    generated_coa_path = db.Column(db.String(500))
    generated_msds_path = db.Column(db.String(500))
    generated_tds_path = db.Column(db.String(500))
    
    # Extracted data (JSON field)
    extracted_data = db.Column(db.Text)  # Will store JSON string
    
    def __repr__(self):
        return f'<DocumentSet {self.company_product_name}>'

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_set_id = db.Column(db.Integer, db.ForeignKey('document_set.id'), nullable=False)
    test_item = db.Column(db.String(200), nullable=False)
    specification = db.Column(db.String(200))
    result = db.Column(db.String(200))
    document_type = db.Column(db.String(10))  # COA, MSDS, TDS
    
    document_set = db.relationship('DocumentSet', backref=db.backref('test_results', lazy=True))
