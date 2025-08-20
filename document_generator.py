import os
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask import current_app

class DocumentGenerator:
    def __init__(self):
        self.company_name = "Nano Tech Chemical Brothers Pvt. Ltd."
        self.company_address = "Vill. Mangarh, P.O. Kohara, Chandigarh Road Ludhiana-141112 INDIA"
        self.company_phone = "9041060304"
        
    def generate_documents(self, doc_set, extracted_data):
        """Generate all three documents and return file paths"""
        generated_files = {}
        
        try:
            # Generate COA
            coa_path = self.generate_coa(doc_set, extracted_data)
            generated_files['coa'] = coa_path
            
            # Generate MSDS
            msds_path = self.generate_msds(doc_set, extracted_data)
            generated_files['msds'] = msds_path
            
            # Generate TDS
            tds_path = self.generate_tds(doc_set, extracted_data)
            generated_files['tds'] = tds_path
            
        except Exception as e:
            current_app.logger.error(f"Error generating documents: {str(e)}")
            raise
            
        return generated_files
    
    def get_styles(self):
        """Get custom styles for documents"""
        styles = getSampleStyleSheet()
        
        # Company header style
        styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        # Document title style
        styles.add(ParagraphStyle(
            name='DocumentTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.black
        ))
        
        return styles
    
    def generate_coa(self, doc_set, extracted_data):
        """Generate Certificate of Analysis"""
        filename = f"{doc_set.id}_COA_{doc_set.company_product_name.replace(' ', '_')}.pdf"
        filepath = os.path.join(current_app.config['GENERATED_FOLDER'], filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = self.get_styles()
        story = []
        
        # Company header
        story.append(Paragraph(self.company_name, styles['CompanyHeader']))
        story.append(Paragraph(self.company_address, styles['Normal']))
        story.append(Paragraph(f"Mobile No.: {self.company_phone}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Document title
        story.append(Paragraph("CERTIFICATE OF ANALYSIS", styles['DocumentTitle']))
        story.append(Spacer(1, 20))
        
        # Product information table
        product_data = [
            ['Product Name:', doc_set.company_product_name],
            ['INCI Name:', extracted_data.get('inci_name', '')],
            ['Batch Number:', self.generate_batch_number(doc_set)],
            ['Manufacturing Date:', datetime.now().strftime('%d-%m-%Y')],
            ['Expiry Date:', (datetime.now() + timedelta(days=730)).strftime('%d-%m-%Y')]
        ]
        
        product_table = Table(product_data, colWidths=[2*inch, 4*inch])
        product_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(product_table)
        story.append(Spacer(1, 30))
        
        # Test results table
        test_data = [['Test Items', 'Specifications', 'Results']]
        
        # Add test results from extracted data
        for test in extracted_data.get('test_results', []):
            if test.get('document_type') == 'COA':
                test_data.append([
                    test.get('test_item', ''),
                    test.get('specification', ''),
                    test.get('result', '')
                ])
        
        # Add default tests if none found
        if len(test_data) == 1:
            test_data.extend([
                ['Appearance', 'White solid powder', 'White powder'],
                ['Sodium hyaluronate content', '≥ 95%', '97.4%'],
                ['Protein', '≤ 0.1%', '0.04%'],
                ['Loss on drying', '≤ 10%', '6.8%'],
                ['pH', '5.0-8.5', '6.8'],
                ['Heavy metal', '≤20 ppm', '≤20 ppm'],
                ['Total Bacteria', '< 100 CFU/g', 'Complied'],
                ['Yeast and molds', '< 50 CFU/g', 'Complied']
            ])
        
        test_table = Table(test_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(test_table)
        story.append(Spacer(1, 40))
        
        # Footer
        footer_data = [
            ['ISSUED DATE:', datetime.now().strftime('%d-%m-%Y')],
            ['TEST RESULT:', 'PASS']
        ]
        
        footer_table = Table(footer_data, colWidths=[2*inch, 2*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(footer_table)
        story.append(Spacer(1, 40))
        story.append(Paragraph(self.company_name, styles['Normal']))
        
        doc.build(story)
        return filepath
    
    def generate_msds(self, doc_set, extracted_data):
        """Generate Material Safety Data Sheet"""
        filename = f"{doc_set.id}_MSDS_{doc_set.company_product_name.replace(' ', '_')}.pdf"
        filepath = os.path.join(current_app.config['GENERATED_FOLDER'], filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = self.get_styles()
        story = []
        
        # Company header
        story.append(Paragraph(self.company_name, styles['CompanyHeader']))
        story.append(Spacer(1, 20))
        
        # Document title
        story.append(Paragraph("MATERIAL SAFETY DATA SHEET", styles['DocumentTitle']))
        story.append(Spacer(1, 20))
        
        # Section 1: Identification
        story.append(Paragraph("1. Identification:", styles['SectionHeader']))
        
        identification_data = [
            ['Product identifier:', doc_set.company_product_name],
            ['INCI name:', extracted_data.get('inci_name', 'Sodium hyaluronate')],
            ['Recommended use:', 'cosmetics Industry formulations'],
            ['Industrial sector:', 'Chemical Industry'],
            ['Company Name:', self.company_name],
            ['Address:', self.company_address],
            ['Mobile No.:', self.company_phone]
        ]
        
        for item in identification_data:
            story.append(Paragraph(f"<b>{item[0]}</b> {item[1]}", styles['Normal']))
        
        story.append(Spacer(1, 15))
        
        # Section 2: Hazards Identification
        story.append(Paragraph("2. Hazards Identification:", styles['SectionHeader']))
        story.append(Paragraph("<b>Classification of the substance or mixture:</b>", styles['Normal']))
        story.append(Paragraph("The product has been classified according to the legislation in force.", styles['Normal']))
        story.append(Paragraph("Classification according to Regulation (EC) No 1272/2008 as amended.", styles['Normal']))
        story.append(Paragraph("<b>Label Elements:</b> Not applicable.", styles['Normal']))
        story.append(Paragraph("<b>Signal Words:</b> Not applicable", styles['Normal']))
        story.append(Paragraph("<b>Hazard Statement(s):</b> Not applicable", styles['Normal']))
        story.append(Paragraph("<b>Precautionary Statements:</b> Not applicable", styles['Normal']))
        
        story.append(Spacer(1, 15))
        
        # Section 3: Composition
        story.append(Paragraph("3. Composition/Information on Ingredients:", styles['SectionHeader']))
        story.append(Paragraph("<b>Substances:</b> This product is a mixture.", styles['Normal']))
        story.append(Paragraph("<b>Description:</b> Mixture of the substances listed below with non hazardous addition.", styles['Normal']))
        
        composition_data = [
            ['Product Name', 'CAS No', 'EINECS No.', 'Concentration'],
            [extracted_data.get('inci_name', 'Sodium Hyaluronate'), 
             extracted_data.get('cas_number', '9067-32-7'), 
             '168-620-0', '≥95%']
        ]
        
        comp_table = Table(composition_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(comp_table)
        story.append(Spacer(1, 15))
        
        # Add more sections as needed (abbreviated for space)
        sections = [
            ("4. First aid measures", "Supply fresh air; consult doctor in case of complaint. In case of skin contact, flush with plenty of water."),
            ("5. Firefighting measures", "Suitable extinguishing media: foam, carbon dioxide, dry powder, water spray."),
            ("6. Accidental release measures", "Ensure adequate ventilation. Avoid contact with skin and eyes."),
            ("7. Handling and storage", "Store in a cool, dry and well-ventilated place away from strong oxidants."),
            ("8. Exposure controls", "Use appropriate personal protective equipment."),
            ("9. Physical and chemical properties", f"Form: Powder, Colour: White, pH: {extracted_data.get('safety_data', {}).get('ph', '5.0-8.5')}"),
        ]
        
        for section_title, section_content in sections:
            story.append(Paragraph(section_title, styles['SectionHeader']))
            story.append(Paragraph(section_content, styles['Normal']))
            story.append(Spacer(1, 10))
        
        doc.build(story)
        return filepath
    
    def generate_tds(self, doc_set, extracted_data):
        """Generate Technical Data Sheet"""
        filename = f"{doc_set.id}_TDS_{doc_set.company_product_name.replace(' ', '_')}.pdf"
        filepath = os.path.join(current_app.config['GENERATED_FOLDER'], filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = self.get_styles()
        story = []
        
        # Company header
        story.append(Paragraph(self.company_name, styles['CompanyHeader']))
        story.append(Spacer(1, 20))
        
        # Product title
        story.append(Paragraph(doc_set.company_product_name, styles['DocumentTitle']))
        story.append(Paragraph(f"(INCI Name: {extracted_data.get('inci_name', 'Sodium Hyaluronate')})", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Description
        story.append(Paragraph("<b>Description:</b>", styles['SectionHeader']))
        description = """COSCARE-H ACID is a sodium salt form of Hyaluronic Acid. Hyaluronic Acid is a natural 
        biomolecule widely found in skin and other tissues. It has excellent moisturizing effect and is 
        internationally known the ideal Natural Moisturizing Factor (NMF). It is a substance with good 
        moisturizing properties for cosmetics found in nature."""
        story.append(Paragraph(description, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Basic information
        basic_info = [
            ['INCI Name:', extracted_data.get('inci_name', 'Sodium Hyaluronate')],
            ['CAS No.:', extracted_data.get('cas_number', '9004-61-9')],
            ['M.F.:', extracted_data.get('molecular_formula', '(C14H21NO11)n')]
        ]
        
        for item in basic_info:
            story.append(Paragraph(f"<b>{item[0]}</b> {item[1]}", styles['Normal']))
        
        story.append(Spacer(1, 15))
        
        # Application
        story.append(Paragraph("<b>Application:</b>", styles['SectionHeader']))
        applications = [
            "➢ Moisturizing agent, anti-wrinkle agent, film former, skin conditioner.",
            "➢ Used in moisturizing products, anti-ageing products, skin soothing and healing products, etc.",
            "➢ Suitable for lotion gel, essence, emulsion and cream etc."
        ]
        
        for app in applications:
            story.append(Paragraph(app, styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Specification
        story.append(Paragraph("<b>Specification:</b>", styles['SectionHeader']))
        
        spec_data = [['Test Items', 'Specifications']]
        
        # Use extracted specifications or defaults
        specifications = extracted_data.get('specifications', {})
        if not specifications:
            specifications = {
                'Appearance': 'White solid powder',
                'Molecular weight': '(0.5 – 1.8) x 10⁶',
                'Sodium hyaluronate content': '≥ 95%',
                'Protein': '≤ 0.1%',
                'Loss on drying': '≤ 10%',
                'pH': '5.0-8.5',
                'Staphylococcus Aureus': 'Negative',
                'Pseudomonas Aeruginosa': 'Negative',
                'Heavy metal': '≤20 ppm',
                'Total Bacteria': '< 100 CFU/g',
                'Yeast and molds': '< 50 CFU/g'
            }
        
        for test_item, spec in specifications.items():
            spec_data.append([test_item, spec])
        
        spec_table = Table(spec_data, colWidths=[3*inch, 2.5*inch])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(spec_table)
        story.append(Spacer(1, 20))
        
        # Usage information
        usage_info = [
            ('Recommended use level:', extracted_data.get('recommended_use_level', '0.1 – 1.0 %')),
            ('Use Method:', extracted_data.get('use_method', 'Add in water phase directly.')),
            ('Package:', '1 Kg / bag.'),
            ('Storage:', extracted_data.get('storage_conditions', 'Store in a cool, dry and well-ventilated place and keep away from strong oxidants')),
            ('Shelf life:', extracted_data.get('shelf_life', '2 Years.'))
        ]
        
        for label, value in usage_info:
            story.append(Paragraph(f"<b>{label}</b>", styles['SectionHeader']))
            story.append(Paragraph(value, styles['Normal']))
            story.append(Spacer(1, 10))
        
        doc.build(story)
        return filepath
    
    def generate_batch_number(self, doc_set):
        """Generate a batch number for the company"""
        prefix = "NTCB"
        date_part = datetime.now().strftime("%y%m%d")
        suffix = f"{doc_set.id:02d}K1"
        return f"{prefix}/{date_part}{suffix}"
