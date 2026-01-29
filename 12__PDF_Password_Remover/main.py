"""
PDF Password Remover Backend
Removes password protection from PDF files
"""

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os


async def execute(request: Request):
    """
    Remove password protection from PDF
    
    Expected form data:
    - file: Password-protected PDF file
    - password: Password to unlock the PDF
    """
    try:
        print("[PDF Password Remover] Processing request")
        
        # Get form data
        form = await request.form()
        pdf_file = form.get('file')
        password = form.get('password', '')
        
        if not pdf_file:
            print("[PDF Password Remover] Error: No file provided")
            return JSONResponse(
                {"error": "No PDF file provided"}, 
                status_code=400
            )
        
        if not password:
            print("[PDF Password Remover] Error: No password provided")
            return JSONResponse(
                {"error": "No password provided"}, 
                status_code=400
            )
        
        # Read the uploaded PDF
        pdf_content = await pdf_file.read()
        print(f"[PDF Password Remover] File received: {pdf_file.filename} ({len(pdf_content)} bytes)")
        
        # Save to temporary input file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            tmp_input.write(pdf_content)
            input_path = tmp_input.name
        
        try:
            # Try to read PDF
            reader = PdfReader(input_path)
            
            # Check if PDF is encrypted
            if not reader.is_encrypted:
                cleanup_files(input_path)
                print("[PDF Password Remover] PDF is not password-protected")
                return JSONResponse(
                    {"error": "This PDF is not password-protected"}, 
                    status_code=400
                )
            
            # Try to decrypt with provided password
            decrypt_result = reader.decrypt(password)
            
            if decrypt_result == 0:
                # Password is incorrect
                cleanup_files(input_path)
                print("[PDF Password Remover] Incorrect password")
                return JSONResponse(
                    {"error": "Incorrect password. Please try again."}, 
                    status_code=400
                )
            
            # Password is correct, now create unlocked version
            writer = PdfWriter()
            
            # Copy all pages to writer
            for page in reader.pages:
                writer.add_page(page)
            
            # Copy metadata if available
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            # Save to temporary output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                output_path = tmp_output.name
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"[PDF Password Remover] Success: Removed password from {pdf_file.filename}")
            
            # Get original filename
            original_filename = pdf_file.filename if pdf_file.filename else 'document.pdf'
            new_filename = original_filename.replace('.pdf', '_unlocked.pdf')
            if new_filename == original_filename:
                new_filename = 'unlocked.pdf'
            
            # Return the unlocked PDF
            return FileResponse(
                path=output_path,
                filename=new_filename,
                media_type='application/pdf',
                background=lambda: cleanup_files(input_path, output_path)
            )
            
        except Exception as e:
            # Cleanup on error
            cleanup_files(input_path, None)
            print(f"[PDF Password Remover] Error: {str(e)}")
            raise e
            
    except Exception as e:
        print(f"[PDF Password Remover] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Error processing PDF: {str(e)}"}, 
            status_code=500
        )


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as e:
                print(f"Error cleaning up file {path}: {e}")

