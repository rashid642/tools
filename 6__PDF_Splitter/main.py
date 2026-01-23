"""
PDF Splitter Backend
Splits PDF files into multiple documents by page ranges
"""

from fastapi import Request
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os
import json
import zipfile


async def execute(request: Request):
    """
    Split PDF into multiple files based on page ranges
    
    Expected form data:
    - file: PDF file
    - splits: JSON array of split configurations
      [
        {"name": "chapter-1", "pages": [1, 2, 3]},
        {"name": "chapter-2", "pages": [4, 5, 6]}
      ]
    """
    try:
        # Get form data
        form = await request.form()
        pdf_file = form.get('file')
        splits_json = form.get('splits', '[]')
        
        if not pdf_file:
            return {"error": "No PDF file provided"}, 400
        
        # Parse splits configuration
        try:
            splits = json.loads(splits_json)
        except json.JSONDecodeError:
            return {"error": "Invalid splits configuration"}, 400
        
        if not splits or not isinstance(splits, list):
            return {"error": "No splits provided"}, 400
        
        # Read the uploaded PDF
        pdf_content = await pdf_file.read()
        
        # Save to temporary input file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            tmp_input.write(pdf_content)
            input_path = tmp_input.name
        
        temp_files = [input_path]
        
        try:
            # Read PDF
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            # Validate all splits
            for split in splits:
                if not isinstance(split, dict):
                    return {"error": "Invalid split format"}, 400
                
                if 'pages' not in split or not isinstance(split['pages'], list):
                    return {"error": "Each split must have a 'pages' array"}, 400
                
                # Validate page numbers
                for page_num in split['pages']:
                    if not isinstance(page_num, int) or page_num < 1 or page_num > total_pages:
                        return {
                            "error": f"Invalid page number {page_num}. PDF has {total_pages} pages."
                        }, 400
            
            # Create split PDFs
            split_files = []
            
            for i, split in enumerate(splits):
                name = split.get('name', f'split-{i+1}')
                pages = split['pages']
                
                if not pages:
                    continue
                
                # Create writer for this split
                writer = PdfWriter()
                
                # Add specified pages (pages are 1-indexed from frontend)
                for page_num in sorted(pages):
                    writer.add_page(reader.pages[page_num - 1])
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_split:
                    split_path = tmp_split.name
                
                with open(split_path, 'wb') as output_file:
                    writer.write(output_file)
                
                # Sanitize filename
                safe_name = sanitize_filename(name)
                split_files.append((split_path, f'{safe_name}.pdf'))
                temp_files.append(split_path)
            
            if not split_files:
                return {"error": "No valid splits created"}, 400
            
            # Create ZIP file with all splits
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
                zip_path = tmp_zip.name
            
            temp_files.append(zip_path)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for split_path, filename in split_files:
                    zipf.write(split_path, filename)
            
            # Get original filename for ZIP
            original_filename = pdf_file.filename
            if original_filename:
                zip_filename = original_filename.replace('.pdf', '-splits.zip')
            else:
                zip_filename = 'pdf-splits.zip'
            
            # Return the ZIP file
            return FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type='application/zip',
                background=lambda: cleanup_files(*temp_files)
            )
            
        except Exception as e:
            # Cleanup on error
            cleanup_files(*temp_files)
            raise e
            
    except Exception as e:
        print(f"Error splitting PDF: {e}")
        return {"error": str(e)}, 500


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters
    """
    # Replace spaces with hyphens
    name = name.strip().replace(' ', '-')
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    
    # Remove leading/trailing dots and hyphens
    name = name.strip('.-')
    
    # If name is empty after sanitization, use default
    if not name:
        name = 'split'
    
    return name


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as e:
                print(f"Error cleaning up file {path}: {e}")

