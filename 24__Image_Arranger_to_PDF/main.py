"""
Image Arranger to PDF Converter
Accepts multiple images, maintains their order, and combines them into a single PDF.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import io
from PIL import Image
import img2pdf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Arranger to PDF")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tool": "Image Arranger to PDF",
        "version": "1.0.0"
    }

@app.post("/convert")
async def convert_images_to_pdf(images: List[UploadFile] = File(...)):
    """
    Convert multiple images to a single PDF document.
    Images are processed in the order they are received.
    """
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    if len(images) > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 images allowed per PDF")
    
    logger.info(f"Processing {len(images)} images")
    
    try:
        # List to store processed image bytes
        image_list = []
        
        for idx, image_file in enumerate(images):
            # Validate file type
            if not image_file.content_type or not image_file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {image_file.filename} is not a valid image"
                )
            
            # Read image content
            image_content = await image_file.read()
            
            # Open image with PIL to validate and optionally convert
            try:
                img = Image.open(io.BytesIO(image_content))
                
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
                
                # Save converted image to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=95)
                img_byte_arr.seek(0)
                image_list.append(img_byte_arr.getvalue())
                
                logger.info(f"Processed image {idx + 1}/{len(images)}: {image_file.filename}")
                
            except Exception as e:
                logger.error(f"Error processing image {image_file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to process image {image_file.filename}: {str(e)}"
                )
        
        # Convert images to PDF using img2pdf
        try:
            pdf_bytes = img2pdf.convert(image_list)
            logger.info(f"Successfully created PDF with {len(images)} pages")
        except Exception as e:
            logger.error(f"Error converting images to PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create PDF: {str(e)}")
        
        # Return PDF as streaming response
        pdf_stream = io.BytesIO(pdf_bytes)
        
        return StreamingResponse(
            pdf_stream,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=images-arranged.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

