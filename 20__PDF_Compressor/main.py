"""
PDF Compressor Backend
Compresses PDF files by optimizing content streams and reducing image quality
"""

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import tempfile
import os
import io


async def execute(request: Request):
    """
    Compress a PDF file
    
    Expected form data:
    - file: PDF file to compress
    - quality: Compression quality (low, medium, high)
    """
    try:
        print("[PDF Compressor] Processing compression request")
        
        # Get form data
        form = await request.form()
        uploaded_file = form.get('file')
        quality = form.get('quality', 'medium')
        
        if not uploaded_file:
            print("[PDF Compressor] Error: No file provided")
            return JSONResponse(
                {"error": "No PDF file provided"},
                status_code=400
            )
        
        # Read uploaded file
        content = await uploaded_file.read()
        
        # Save to temporary input file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            tmp_input.write(content)
            input_path = tmp_input.name
        
        try:
            # Read the PDF
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            if len(reader.pages) == 0:
                cleanup_files(input_path)
                return JSONResponse(
                    {"error": "PDF file has no pages"},
                    status_code=400
                )
            
            # Compression settings based on quality
            compression_settings = {
                'low': {'image_quality': 30, 'scale': 0.5},
                'medium': {'image_quality': 60, 'scale': 0.7},
                'high': {'image_quality': 85, 'scale': 0.9}
            }
            
            settings = compression_settings.get(quality, compression_settings['medium'])
            print(f"[PDF Compressor] Using quality: {quality}, settings: {settings}")
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                print(f"[PDF Compressor] Processing page {page_num + 1}/{len(reader.pages)}")
                
                # Compress page content
                page.compress_content_streams()
                
                # Add to writer
                writer.add_page(page)
            
            # Apply additional compression
            for page in writer.pages:
                page.compress_content_streams()
            
            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                output_path = tmp_output.name
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Get file sizes
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            compression_ratio = ((input_size - output_size) / input_size * 100) if input_size > 0 else 0
            
            print(f"[PDF Compressor] Success: Compressed from {input_size} to {output_size} bytes ({compression_ratio:.1f}% reduction)")
            
            # Clean up input file
            cleanup_files(input_path)
            
            # Return the compressed PDF
            return FileResponse(
                path=output_path,
                filename='compressed.pdf',
                media_type='application/pdf',
                background=lambda: cleanup_files(output_path)
            )
            
        except Exception as e:
            cleanup_files(input_path)
            raise e
            
    except Exception as e:
        print(f"[PDF Compressor] Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Error: {str(e)}"},
            status_code=500
        )


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
                print(f"[PDF Compressor] Cleaned up: {path}")
            except Exception as e:
                print(f"[PDF Compressor] Error cleaning up file {path}: {e}")

