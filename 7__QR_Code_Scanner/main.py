from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io

# Try pyzbar first, fall back to cv2 if needed
try:
    from pyzbar import pyzbar
    USE_PYZBAR = True
except ImportError:
    USE_PYZBAR = False
    try:
        import cv2
        import numpy as np
        USE_CV2 = True
    except ImportError:
        USE_CV2 = False

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
        
        # Decode using available library
        codes = []
        
        if USE_PYZBAR:
            # Use pyzbar (preferred)
            decoded_objects = pyzbar.decode(image)
            
            for obj in decoded_objects:
                try:
                    decoded_data = obj.data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        decoded_data = obj.data.decode('latin-1')
                    except:
                        decoded_data = str(obj.data)
                
                codes.append({
                    "type": obj.type,
                    "data": decoded_data
                })
        
        elif USE_CV2:
            # Use OpenCV as fallback
            img_array = np.array(image)
            detector = cv2.QRCodeDetector()
            data, vertices_array, binary_qrcode = detector.detectAndDecode(img_array)
            
            if data:
                codes.append({
                    "type": "QRCODE",
                    "data": data
                })
        
        else:
            return JSONResponse(
                {"error": "QR code scanning library not available. Please install pyzbar or opencv-python."}, 
                status_code=500
            )
        
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

