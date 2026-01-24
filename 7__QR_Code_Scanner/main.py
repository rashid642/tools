from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from pyzbar import pyzbar
from PIL import Image
import io

async def execute(request: Request):
    """
    Decode QR codes and barcodes from uploaded images.
    
    Returns JSON with decoded data:
    {
        "codes": [
            {
                "type": "QRCODE",
                "data": "decoded text or URL"
            }
        ]
    }
    """
    try:
        form = await request.form()
        file: UploadFile = form.get('file')
        
        if not file:
            return JSONResponse(
                {"error": "No image file provided"}, 
                status_code=400
            )
        
        # Read image content
        image_content = await file.read()
        
        # Validate it's an image
        try:
            image = Image.open(io.BytesIO(image_content))
        except Exception as e:
            return JSONResponse(
                {"error": "Invalid image file. Please upload a valid image (JPG, PNG, etc.)"}, 
                status_code=400
            )
        
        # Decode barcodes/QR codes
        decoded_objects = pyzbar.decode(image)
        
        if not decoded_objects:
            return JSONResponse(
                {
                    "error": "No QR codes or barcodes found in the image. Please ensure the code is clear and well-lit.",
                    "codes": []
                },
                status_code=200
            )
        
        # Extract decoded data
        codes = []
        for obj in decoded_objects:
            try:
                # Try UTF-8 decoding first
                decoded_data = obj.data.decode('utf-8')
            except UnicodeDecodeError:
                # Fall back to latin-1 if UTF-8 fails
                try:
                    decoded_data = obj.data.decode('latin-1')
                except:
                    decoded_data = str(obj.data)
            
            codes.append({
                "type": obj.type,
                "data": decoded_data
            })
        
        return JSONResponse({
            "codes": codes,
            "count": len(codes)
        })
        
    except Exception as e:
        print(f"Error processing QR code: {e}")
        return JSONResponse(
            {"error": f"An error occurred while processing the image: {str(e)}"}, 
            status_code=500
        )

