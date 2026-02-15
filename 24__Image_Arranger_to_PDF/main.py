from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
from PIL import Image
import img2pdf

async def execute(request: Request):
    """
    Convert multiple images to a single PDF document.
    Images are processed in the order they are received.
    
    Expected form data:
    - images: Multiple image files (JPG, PNG, GIF, WebP, BMP)
    """
    temp_files = []
    output_file = None
    
    try:
        print("[Image Arranger to PDF] Processing conversion request")
        
        # Get uploaded files
        form = await request.form()
        images = form.getlist('images')
        
        if not images or len(images) == 0:
            return JSONResponse(
                {"error": "No images provided"},
                status_code=400
            )
        
        if len(images) > 50:
            return JSONResponse(
                {"error": "Maximum 50 images allowed per PDF"},
                status_code=400
            )
        
        print(f"[Image Arranger to PDF] Processing {len(images)} images")
        
        # List to store processed image bytes
        image_list = []
        
        for idx, image_file in enumerate(images):
            # Validate file type
            if not image_file.content_type or not image_file.content_type.startswith('image/'):
                return JSONResponse(
                    {"error": f"File {image_file.filename} is not a valid image"},
                    status_code=400
                )
            
            # Read image content
            image_content = await image_file.read()
            
            # Save to temporary file for processing
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.filename)[1])
            temp_input.write(image_content)
            temp_input.close()
            temp_files.append(temp_input.name)
            
            # Open image with PIL to validate and optionally convert
            try:
                img = Image.open(temp_input.name)
                
                # Convert RGBA to RGB (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save converted image to new temporary file
                temp_converted = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                img.save(temp_converted.name, format='JPEG', quality=95)
                temp_converted.close()
                temp_files.append(temp_converted.name)
                
                # Read converted image bytes for PDF
                with open(temp_converted.name, 'rb') as f:
                    image_list.append(f.read())
                
                print(f"[Image Arranger to PDF] Processed image {idx + 1}/{len(images)}: {image_file.filename}")
                
            except Exception as e:
                print(f"[Image Arranger to PDF] Error processing image {image_file.filename}: {e}")
                return JSONResponse(
                    {"error": f"Failed to process image {image_file.filename}: {str(e)}"},
                    status_code=400
                )
        
        # Convert images to PDF using img2pdf
        print(f"[Image Arranger to PDF] Creating PDF with {len(images)} pages")
        
        try:
            pdf_bytes = img2pdf.convert(image_list)
        except Exception as e:
            print(f"[Image Arranger to PDF] Error converting images to PDF: {e}")
            return JSONResponse(
                {"error": f"Failed to create PDF: {str(e)}"},
                status_code=500
            )
        
        # Save PDF to temporary file
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_file.write(pdf_bytes)
        output_file.close()
        
        output_size = os.path.getsize(output_file.name)
        print(f"[Image Arranger to PDF] Successfully created PDF with {len(images)} pages ({output_size} bytes)")
        
        # Generate output filename
        output_filename = f'images-arranged.pdf'
        
        # Return the PDF file
        return FileResponse(
            output_file.name,
            media_type='application/pdf',
            filename=output_filename,
            background=lambda: cleanup_files(output_file.name, *temp_files)
        )
        
    except Exception as e:
        print(f"[Image Arranger to PDF] Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up files on error
        cleanup_files(output_file.name if output_file else None, *temp_files)
        
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
                print(f"[Image Arranger to PDF] Cleaned up: {path}")
            except Exception as e:
                print(f"[Image Arranger to PDF] Error cleaning up file {path}: {e}")
