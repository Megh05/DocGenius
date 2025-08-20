# Chemical Document Automation System

## Overview

This is a Flask-based web application that automates the processing of chemical supplier documents (COA, MSDS, TDS) and generates company-branded versions. The system extracts data from uploaded PDF documents and produces standardized, branded documents for Nano Tech Chemical Brothers Pvt. Ltd., reducing manual processing time from 4-5 hours to just minutes.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 2025)

### Enhanced PDF Processing System
- **Date**: August 20, 2025
- **Issue**: Original PDF extraction was not capturing all pages from multi-page documents (MSDS had 6 pages, only reading 1)
- **Solution**: Enhanced PDF processor with multi-page support and OCR capabilities
- **Key Improvements**:
  - Multi-page text extraction with page-by-page processing
  - OCR fallback for image-based PDFs (like COA documents)
  - Enhanced pattern matching for Chinese supplier documents
  - Better extraction of product names, CAS numbers, INCI names, molecular formulas
  - Multi-language support (English and Chinese patterns)
  - Improved table detection for test results and specifications
- **Dependencies Added**: pytesseract, pdf2image, opencv-python, tesseract (system), poppler-utils (system)
- **Status**: ✅ COMPLETE - OCR system fully operational
- **Results**: Successfully extracting comprehensive data from all document types:
  - MSDS: 6 pages, 11,102+ characters extracted 
  - TDS: 1 page, 1,938+ characters extracted
  - COA: 1 page, 1,289+ characters extracted
- **Data Quality**: Product names, INCI names, CAS numbers, supplier info, molecular formulas all extracting accurately

### Mistral AI Integration
- **Date**: August 20, 2025
- **Feature**: Added Mistral AI for enhanced OCR and field validation
- **Implementation**:
  - Settings panel with gear icon in navigation for API key management
  - MistralService class for OCR enhancement and field validation
  - Integrated Pixtral-12B model for advanced document image analysis
  - Mistral-Large for intelligent field validation and error correction
  - Session-based settings storage with API key security
- **Key Features**:
  - Enhanced OCR using Mistral vision model (Pixtral-12B)
  - Intelligent field validation and automatic error correction
  - API connection testing with real-time feedback
  - User-configurable OCR and validation toggles
  - Secure API key handling with masked input fields
- **Dependencies Added**: requests library for Mistral API communication
- **Status**: ✅ COMPLETE - Mistral integration functional
- **Benefits**: Improved accuracy for chemical document processing, automatic error detection and correction

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap with custom CSS for upload interfaces and styling
- **JavaScript**: Vanilla JavaScript for file upload handling, drag-and-drop functionality
- **Responsive Design**: Mobile-friendly interface with card-based layouts

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite by default, configurable via DATABASE_URL environment variable
- **Document Processing**: Custom PDF processor using pdfplumber for text extraction
- **Document Generation**: ReportLab for creating branded PDF documents
- **File Handling**: Werkzeug for secure file uploads with 16MB size limit

### Data Storage Architecture
- **Primary Database**: SQLAlchemy with declarative base model
- **Document Storage**: File system with separate directories for uploads and generated files
- **Data Models**: 
  - DocumentSet: Main entity storing product information and file paths
  - TestResult: Related entity for storing extracted test data
- **JSON Storage**: Extracted data stored as JSON text in database for flexibility

### Document Processing Pipeline
- **Upload Phase**: Multi-file upload with validation (COA, MSDS, TDS)
- **Extraction Phase**: PDF text extraction and data parsing using regex patterns
- **Generation Phase**: Automated creation of company-branded documents
- **Storage Phase**: Generated documents saved with structured naming convention

### Authentication and Security
- **Session Management**: Flask sessions with configurable secret key
- **File Security**: Secure filename handling and file type validation
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **Werkzeug**: WSGI utilities and security helpers

### Document Processing Libraries
- **pdfplumber**: PDF text extraction and parsing
- **ReportLab**: PDF generation for branded documents
- **ReportLab Components**: platypus, lib.pagesizes, lib.styles for document formatting

### Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via CDN
- **Font Awesome 6**: Icon library for interface elements
- **Custom CSS/JS**: Application-specific styling and upload functionality

### Development and Deployment
- **Python Standard Library**: os, json, datetime, logging for core functionality
- **Environment Variables**: Configuration via DATABASE_URL and SESSION_SECRET
- **File System**: Local storage for uploaded and generated documents

### Database Configuration
- **Connection Pooling**: Configured with pool_recycle and pool_pre_ping
- **Migration Support**: SQLAlchemy create_all for initial schema creation
- **Development Default**: SQLite with configurable production database support