import os
import json
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_file, current_app
from werkzeug.utils import secure_filename
from app import app, db
from models import DocumentSet, TestResult
from pdf_processor import PDFProcessor
from document_generator import DocumentGenerator

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    recent_documents = DocumentSet.query.order_by(DocumentSet.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_documents=recent_documents)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if files are present
        if 'supplier_coa' not in request.files or 'supplier_msds' not in request.files or 'supplier_tds' not in request.files:
            flash('Please upload all three required documents (COA, MSDS, TDS)', 'error')
            return redirect(request.url)
        
        files = {
            'coa': request.files['supplier_coa'],
            'msds': request.files['supplier_msds'],
            'tds': request.files['supplier_tds']
        }
        
        # Check if all files are selected and valid
        for doc_type, file in files.items():
            if file.filename == '':
                flash(f'Please select a {doc_type.upper()} file', 'error')
                return redirect(request.url)
            
            if not allowed_file(file.filename):
                flash(f'{doc_type.upper()} file must be a PDF', 'error')
                return redirect(request.url)
        
        # Get form data
        company_product_name = request.form.get('company_product_name', '').strip()
        if not company_product_name:
            flash('Please provide a company product name', 'error')
            return redirect(request.url)
        
        try:
            # Create document set record
            doc_set = DocumentSet(
                original_product_name="",  # Will be extracted from PDFs
                company_product_name=company_product_name,
                supplier_name="",  # Will be extracted from PDFs
            )
            db.session.add(doc_set)
            db.session.flush()  # Get the ID
            
            # Save uploaded files
            saved_files = {}
            for doc_type, file in files.items():
                filename = secure_filename(f"{doc_set.id}_{doc_type}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_files[doc_type] = filepath
                
                # Update document set with file paths
                if doc_type == 'coa':
                    doc_set.supplier_coa_path = filepath
                elif doc_type == 'msds':
                    doc_set.supplier_msds_path = filepath
                elif doc_type == 'tds':
                    doc_set.supplier_tds_path = filepath
            
            # Process PDFs and extract data
            processor = PDFProcessor()
            extracted_data = processor.process_documents(saved_files)
            
            # Update document set with extracted data
            doc_set.original_product_name = extracted_data.get('product_name', '')
            doc_set.supplier_name = extracted_data.get('supplier_name', '')
            doc_set.cas_number = extracted_data.get('cas_number', '')
            doc_set.inci_name = extracted_data.get('inci_name', '')
            doc_set.molecular_formula = extracted_data.get('molecular_formula', '')
            doc_set.batch_number = extracted_data.get('batch_number', '')
            
            # Parse dates if available
            if extracted_data.get('manufacturing_date'):
                try:
                    doc_set.manufacturing_date = datetime.strptime(extracted_data['manufacturing_date'], '%d-%m-%Y').date()
                except:
                    pass
            
            if extracted_data.get('expiry_date'):
                try:
                    doc_set.expiry_date = datetime.strptime(extracted_data['expiry_date'], '%d-%m-%Y').date()
                except:
                    pass
            
            doc_set.extracted_data = json.dumps(extracted_data)
            
            # Save test results
            for test in extracted_data.get('test_results', []):
                test_result = TestResult(
                    document_set_id=doc_set.id,
                    test_item=test.get('test_item', ''),
                    specification=test.get('specification', ''),
                    result=test.get('result', ''),
                    document_type=test.get('document_type', 'COA')
                )
                db.session.add(test_result)
            
            # Generate new documents
            generator = DocumentGenerator()
            generated_files = generator.generate_documents(doc_set, extracted_data)
            
            # Update document set with generated file paths
            doc_set.generated_coa_path = generated_files.get('coa')
            doc_set.generated_msds_path = generated_files.get('msds')
            doc_set.generated_tds_path = generated_files.get('tds')
            
            db.session.commit()
            
            flash('Documents processed successfully!', 'success')
            return redirect(url_for('results', doc_set_id=doc_set.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing documents: {str(e)}")
            flash(f'Error processing documents: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/results/<int:doc_set_id>')
def results(doc_set_id):
    doc_set = DocumentSet.query.get_or_404(doc_set_id)
    extracted_data = json.loads(doc_set.extracted_data) if doc_set.extracted_data else {}
    return render_template('results.html', doc_set=doc_set, extracted_data=extracted_data)

@app.route('/download/<int:doc_set_id>/<doc_type>')
def download(doc_set_id, doc_type):
    doc_set = DocumentSet.query.get_or_404(doc_set_id)
    
    file_path = None
    if doc_type == 'coa':
        file_path = doc_set.generated_coa_path
    elif doc_type == 'msds':
        file_path = doc_set.generated_msds_path
    elif doc_type == 'tds':
        file_path = doc_set.generated_tds_path
    
    if not file_path or not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect(url_for('results', doc_set_id=doc_set_id))
    
    filename = f"NTCB_{doc_type.upper()}_{doc_set.company_product_name.replace(' ', '_')}.pdf"
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload'))
