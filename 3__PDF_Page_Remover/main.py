"""
PDF Page Remover Backend
Removes specified pages from PDF files
"""

from fastapi import Request
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os


async def execute(request: Request):
    """
    Remove specified pages from PDF and return modified file
    
    Expected form data:
    - file: PDF file
    - pages: Comma-separated page numbers (e.g., "1, 3, 5-7")
    """
    try:
        # Get form data
        form = await request.form()
        pdf_file = form.get('file')
        pages_to_remove = form.get('pages', '')
        
        if not pdf_file:
            return {"error": "No PDF file provided"}, 400
        
        if not pages_to_remove:
            return {"error": "No page numbers provided"}, 400
        
        # Parse page numbers
        pages_set = parse_page_numbers(pages_to_remove)
        if not pages_set:
            return {"error": "Invalid page numbers format"}, 400
        
        # Read the uploaded PDF
        pdf_content = await pdf_file.read()
        
        # Save to temporary input file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            tmp_input.write(pdf_content)
            input_path = tmp_input.name
        
        try:
            # Read PDF
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            # Validate page numbers
            max_page = max(pages_set) if pages_set else 0
            if max_page > total_pages:
                return {
                    "error": f"Page {max_page} doesn't exist. PDF has only {total_pages} pages."
                }, 400
            
            if len(pages_set) >= total_pages:
                return {"error": "Cannot remove all pages from PDF"}, 400
            
            # Create writer and add pages (excluding the ones to remove)
            writer = PdfWriter()
            pages_kept = 0
            
            for page_num in range(1, total_pages + 1):
                if page_num not in pages_set:
                    writer.add_page(reader.pages[page_num - 1])
                    pages_kept += 1
            
            # Save to temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                output_path = tmp_output.name
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Get original filename
            original_filename = pdf_file.filename
            if original_filename:
                new_filename = original_filename.replace('.pdf', '_modified.pdf')
            else:
                new_filename = 'modified.pdf'
            
            # Return the modified PDF
            return FileResponse(
                path=output_path,
                filename=new_filename,
                media_type='application/pdf',
                background=lambda: cleanup_files(input_path, output_path)
            )
            
        except Exception as e:
            # Cleanup on error
            cleanup_files(input_path, None)
            raise e
            
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return {"error": str(e)}, 500


def parse_page_numbers(pages_str: str) -> set:
    """
    Parse page numbers from string format like "1, 3, 5-7"
    Returns set of page numbers to remove
    """
    pages = set()
    parts = pages_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        if '-' in part:
            # Handle range like "3-5"
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start >= 1 and end >= start:
                    pages.update(range(start, end + 1))
            except (ValueError, IndexError):
                continue
        else:
            # Handle single page like "3"
            try:
                page = int(part.strip())
                if page >= 1:
                    pages.add(page)
            except ValueError:
                continue
    
    return pages


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as e:
                print(f"Error cleaning up file {path}: {e}")

