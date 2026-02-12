"""
PDF Compressor Backend
Compresses PDF files using Ghostscript for optimal compression
"""

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import subprocess


async def execute(request: Request):
    """
    Compress a PDF file using Ghostscript
    
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
            # Quality settings for Ghostscript
            # Using PDFSETTINGS for different compression levels
            quality_settings = {
                'low': '/screen',      # Lowest quality, smallest size (72 dpi)
                'medium': '/ebook',    # Medium quality (150 dpi)
                'high': '/printer'     # High quality (300 dpi)
            }
            
            pdf_setting = quality_settings.get(quality, '/ebook')
            print(f"[PDF Compressor] Using quality: {quality} (Ghostscript setting: {pdf_setting})")
            
            # Create output file path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                output_path = tmp_output.name
            
            # Ghostscript compression command
            # Using optimal settings for compression while preserving content
            gs_command = [
                'gs',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={pdf_setting}',
                '-dNOPAUSE',
                '-dQUIET',
                '-dBATCH',
                '-dDetectDuplicateImages=true',
                '-dCompressFonts=true',
                '-dCompressPages=true',
                '-dDownsampleColorImages=true',
                '-dDownsampleGrayImages=true',
                '-dDownsampleMonoImages=true',
                f'-sOutputFile={output_path}',
                input_path
            ]
            
            print(f"[PDF Compressor] Running Ghostscript compression...")
            
            # Run Ghostscript
            result = subprocess.run(
                gs_command,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"[PDF Compressor] Ghostscript error: {result.stderr}")
                cleanup_files(input_path, output_path)
                return JSONResponse(
                    {"error": "Failed to compress PDF. Please try again."},
                    status_code=500
                )
            
            # Check if output file was created and has content
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                cleanup_files(input_path, output_path)
                return JSONResponse(
                    {"error": "Compression failed. Output file is empty."},
                    status_code=500
                )
            
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
            
        except subprocess.TimeoutExpired:
            cleanup_files(input_path, output_path if 'output_path' in locals() else None)
            return JSONResponse(
                {"error": "Compression timed out. File may be too large."},
                status_code=500
            )
        except FileNotFoundError:
            cleanup_files(input_path)
            return JSONResponse(
                {"error": "Ghostscript not installed on server. Please contact administrator."},
                status_code=500
            )
        except Exception as e:
            cleanup_files(input_path, output_path if 'output_path' in locals() else None)
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

