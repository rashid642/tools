from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import subprocess

async def execute(request: Request):
    """
    Convert document files (DOC, DOCX, PPT, PPTX, XLS, XLSX) to PDF
    
    Expected form data:
    - file: Document file to convert
    """
    input_file = None
    output_file = None
    
    try:
        print("[Document to PDF] Processing conversion request")
        
        # Get uploaded file
        form = await request.form()
        file = form.get('file')
        
        if not file:
            return JSONResponse(
                {"error": "No file provided"},
                status_code=400
            )
        
        # Get file extension
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Validate file type
        valid_extensions = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']
        if file_extension not in valid_extensions:
            return JSONResponse(
                {"error": f"Unsupported file type. Supported: {', '.join(valid_extensions)}"},
                status_code=400
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_input:
            content = await file.read()
            temp_input.write(content)
            input_file = temp_input.name
        
        print(f"[Document to PDF] Input file saved: {filename} ({len(content)} bytes)")
        
        # Create output file path
        output_file = tempfile.mktemp(suffix='.pdf')
        
        # Convert using LibreOffice (headless mode)
        # LibreOffice must be installed on the server
        print(f"[Document to PDF] Starting conversion with LibreOffice")
        
        try:
            # Try different LibreOffice commands (varies by system)
            libreoffice_commands = [
                'libreoffice',
                'soffice',
                '/usr/bin/libreoffice',
                '/usr/bin/soffice'
            ]
            
            conversion_successful = False
            for cmd in libreoffice_commands:
                process = None
                try:
                    # Run LibreOffice in headless mode to convert to PDF
                    # Using Popen for better process control
                    process = subprocess.Popen(
                        [
                            cmd,
                            '--headless',
                            '--convert-to', 'pdf',
                            '--outdir', os.path.dirname(output_file),
                            input_file
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Wait for completion with timeout
                    stdout, stderr = process.communicate(timeout=60)
                    result = type('obj', (object,), {
                        'returncode': process.returncode,
                        'stdout': stdout,
                        'stderr': stderr
                    })
                    
                    if result.returncode == 0:
                        conversion_successful = True
                        # LibreOffice creates the output file with the same name but .pdf extension
                        expected_output = os.path.join(
                            os.path.dirname(output_file),
                            os.path.splitext(os.path.basename(input_file))[0] + '.pdf'
                        )
                        if os.path.exists(expected_output):
                            # Rename to our desired output file
                            os.rename(expected_output, output_file)
                        break
                except subprocess.TimeoutExpired:
                    # CRITICAL: Kill the process to prevent zombies
                    if process:
                        try:
                            process.kill()
                            process.wait(timeout=5)  # Wait for kill to complete
                            print(f"[Document to PDF] Killed timed-out {cmd} process")
                        except:
                            pass
                    continue
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"[Document to PDF] Error with {cmd}: {e}")
                    # Kill process if still running
                    if process and process.poll() is None:
                        try:
                            process.kill()
                            process.wait(timeout=5)
                        except:
                            pass
                    continue
            
            if not conversion_successful:
                return JSONResponse(
                    {"error": "LibreOffice conversion failed. Please ensure LibreOffice is installed on the server."},
                    status_code=500
                )
        
        except subprocess.TimeoutExpired:
            # This should not be reached due to inner handling, but just in case
            print("[Document to PDF] Global timeout handler reached")
            return JSONResponse(
                {"error": "Conversion timeout. File may be too large or complex."},
                status_code=500
            )
        
        # Verify output file was created
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            return JSONResponse(
                {"error": "PDF generation failed. Output file is empty or missing."},
                status_code=500
            )
        
        output_size = os.path.getsize(output_file)
        print(f"[Document to PDF] Conversion successful: {filename} -> PDF ({output_size} bytes)")
        
        # Generate output filename
        output_filename = os.path.splitext(filename)[0] + '.pdf'
        
        # Return the PDF file
        return FileResponse(
            output_file,
            media_type='application/pdf',
            filename=output_filename,
            background=lambda: cleanup_files(input_file, output_file)
        )
        
    except Exception as e:
        print(f"[Document to PDF] Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up files on error
        cleanup_files(input_file, output_file)
        
        return JSONResponse(
            {"error": f"Conversion error: {str(e)}"},
            status_code=500
        )


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
                print(f"[Document to PDF] Cleaned up: {path}")
            except Exception as e:
                print(f"[Document to PDF] Error cleaning up file {path}: {e}")

