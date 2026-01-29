from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import io
import os
import sys

# Fix for macOS zbar library path
if sys.platform == 'darwin':
    os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pyzbar not available: {e}")
    PYZBAR_AVAILABLE = False

async def execute(request: Request):
    """
    Decode QR codes and barcodes from uploaded images using multiple detection strategies.
    
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
        print(f"[QR Scanner] Processing: {file.filename} ({len(image_content)} bytes)")
        
        # Validate it's an image
        try:
            pil_image = Image.open(io.BytesIO(image_content))
        except Exception as e:
            return JSONResponse(
                {"error": "Invalid image file. Please upload a valid image (JPG, PNG, etc.)"}, 
                status_code=400
            )
        
        # Convert PIL image to OpenCV format
        img_array = np.array(pil_image.convert('RGB'))
        
        # Try multiple detection strategies
        codes = []
        
        # Strategy 1: pyzbar (most reliable for standard QR codes) - if available
        if PYZBAR_AVAILABLE:
            codes.extend(decode_with_pyzbar(pil_image))
            if codes:
                print(f"[QR Scanner] Decoded using pyzbar strategy")
        
        # Strategy 2: OpenCV QRCodeDetector (good for some cases)
        if not codes:
            codes.extend(decode_with_opencv(img_array))
            if codes:
                print(f"[QR Scanner] Decoded using OpenCV strategy")
        
        # Strategy 3: Try with image preprocessing (most thorough)
        if not codes:
            codes.extend(decode_with_preprocessing(pil_image, img_array))
            if codes:
                print(f"[QR Scanner] Decoded using preprocessing strategy")
        
        # Remove duplicates
        unique_codes = []
        seen_data = set()
        for code in codes:
            if code['data'] not in seen_data:
                unique_codes.append(code)
                seen_data.add(code['data'])
        
        if not unique_codes:
            print("[QR Scanner] No codes detected")
            return JSONResponse(
                {
                    "error": "No QR codes or barcodes found in the image. Please ensure the code is clear and well-lit.",
                    "codes": []
                },
                status_code=200
            )
        
        print(f"[QR Scanner] Success: {len(unique_codes)} code(s) found - Types: {[c['type'] for c in unique_codes]}")
        return JSONResponse({
            "codes": unique_codes,
            "count": len(unique_codes)
        })
        
    except Exception as e:
        print(f"Error processing QR code: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"An error occurred while processing the image: {str(e)}"}, 
            status_code=500
        )


def decode_with_pyzbar(pil_image):
    """Decode using pyzbar library"""
    codes = []
    if not PYZBAR_AVAILABLE:
        return codes
    try:
        decoded_objects = pyzbar.decode
        (pil_image)
        for obj in decoded_objects:
            codes.append({
                "type": obj.type,
                "data": obj.data.decode('utf-8')
            })
    except Exception as e:
        print(f"pyzbar decoding error: {e}")
    return codes


def decode_with_opencv(img_array):
    """Decode using OpenCV QRCodeDetector"""
    codes = []
    try:
        detector = cv2.QRCodeDetector()
        data, vertices_array, binary_qrcode = detector.detectAndDecode(img_array)
        if data:
            codes.append({
                "type": "QRCODE",
                "data": data
            })
    except Exception as e:
        print(f"OpenCV decoding error: {e}")
    return codes


def decode_with_preprocessing(pil_image, img_array):
    """Try decoding with various image preprocessing techniques"""
    codes = []
    
    # Preprocessing strategies
    preprocessed_images = []
    
    # 1. Increase contrast
    try:
        enhancer = ImageEnhance.Contrast(pil_image)
        preprocessed_images.append(enhancer.enhance(2.0))
    except:
        pass
    
    # 2. Convert to grayscale and apply thresholding
    try:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed_images.append(Image.fromarray(thresh))
    except:
        pass
    
    # 3. Adaptive thresholding
    try:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY, 11, 2)
        preprocessed_images.append(Image.fromarray(adaptive_thresh))
    except:
        pass
    
    # 4. Increase sharpness
    try:
        enhancer = ImageEnhance.Sharpness(pil_image)
        preprocessed_images.append(enhancer.enhance(2.0))
    except:
        pass
    
    # 5. Adjust brightness
    try:
        enhancer = ImageEnhance.Brightness(pil_image)
        preprocessed_images.append(enhancer.enhance(1.5))
    except:
        pass
    
    # Try decoding each preprocessed image
    for processed_img in preprocessed_images:
        if codes:
            break
        
        # Try pyzbar (if available)
        if PYZBAR_AVAILABLE:
            try:
                decoded_objects = pyzbar.decode(processed_img)
                for obj in decoded_objects:
                    codes.append({
                        "type": obj.type,
                        "data": obj.data.decode('utf-8')
                    })
            except:
                pass
        
        if codes:
            break
        
        # Try OpenCV
        try:
            img_np = np.array(processed_img)
            if len(img_np.shape) == 2:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
            detector = cv2.QRCodeDetector()
            data, vertices_array, binary_qrcode = detector.detectAndDecode(img_np)
            if data:
                codes.append({
                    "type": "QRCODE",
                    "data": data
                })
        except:
            pass
    
    return codes



