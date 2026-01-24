from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import cv2
import numpy as np
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
        
        # Decode using OpenCV
        img_array = np.array(image)
        detector = cv2.QRCodeDetector()
        data, vertices_array, binary_qrcode = detector.detectAndDecode(img_array)
        
        codes = []
        if data:
            codes.append({
                "type": "QRCODE",
                "data": data
            })
        
        if not codes:
            return JSONResponse(
                {
                    "error": "No QR codes or barcodes found in the image. Please ensure the code is clear and well-lit.",
                    "codes": []
                },
                status_code=200
            )
        
        return JSONResponse({
            "codes": codes,
            "count": len(codes)
        })
        
    except Exception as e:
        print(f"Error processing QR code: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"An error occurred while processing the image: {str(e)}"}, 
            status_code=500
        )

