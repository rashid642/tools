"""
PDF Merger Backend
Merges multiple PDF files into a single PDF document
"""

from fastapi import Request
from fastapi.responses import FileResponse
from PyPDF2 import PdfMerger, PdfReader
import tempfile
import os


async def execute(request: Request):
    """
    Merge multiple PDF files into one
    
    Expected form data:
    - files: Multiple PDF files
    - order: Order indices for each file (matching file order)
    """
    try:
        # Get form data
        form = await request.form()
        
        # Get all uploaded files and orders
        files = []
        orders = []
        
        # Iterate through form data
        for key, value in form.multi_items():
            if key == 'files':
                files.append(value)
            elif key == 'order':
                orders.append(value)
        
        if not files:
            return {"error": "No PDF files provided"}, 400
        
        if len(files) < 2:
            return {"error": "At least 2 PDF files are required for merging"}, 400
        
        # Create list of file data with order
        file_data = []
        for i, file in enumerate(files):
            order = int(orders[i]) if i < len(orders) else i
            file_data.append({
                'file': file,
                'order': order,
                'filename': file.filename or f'file_{i}.pdf'
            })
        
        # Sort by order
        file_data.sort(key=lambda x: x['order'])
        
        # Create temporary files for each uploaded PDF
        temp_files = []
        merger = PdfMerger()
        
        try:
            # Process each file
            for data in file_data:
                file = data['file']
                
                # Read file content
                content = await file.read()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(content)
                    temp_path = tmp.name
                    temp_files.append(temp_path)
                
                # Validate PDF
                try:
                    reader = PdfReader(temp_path)
                    if len(reader.pages) == 0:
                        return {"error": f"PDF file '{data['filename']}' has no pages"}, 400
                    
                    # Add to merger
                    merger.append(temp_path)
                    print(f"Added: {data['filename']} ({len(reader.pages)} pages)")
                    
                except Exception as e:
                    return {"error": f"Error reading PDF '{data['filename']}': {str(e)}"}, 400
            
            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
                output_path = tmp_output.name
            
            # Write merged PDF
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            
            print(f"Successfully merged {len(file_data)} PDFs")
            
            # Return the merged PDF
            return FileResponse(
                path=output_path,
                filename='merged.pdf',
                media_type='application/pdf',
                background=lambda: cleanup_files(output_path, *temp_files)
            )
            
        except Exception as e:
            # Cleanup on error
            merger.close()
            cleanup_files(None, *temp_files)
            raise e
            
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500


def cleanup_files(*file_paths):
    """Clean up temporary files"""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as e:
                print(f"Error cleaning up file {path}: {e}")

