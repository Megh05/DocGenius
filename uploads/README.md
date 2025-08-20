# Uploads Directory

This directory stores the uploaded supplier documents (COA, MSDS, TDS) temporarily during processing.

## Structure
- Files are named with the pattern: `{document_set_id}_{document_type}_{original_filename}`
- Supported file types: PDF only
- Maximum file size: 16MB per document

## Cleanup
Files in this directory can be cleaned up periodically as they are only needed during processing.
