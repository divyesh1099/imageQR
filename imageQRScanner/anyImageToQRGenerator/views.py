import io
import base64
import qrcode
from PIL import Image
from django.shortcuts import render

# Maximum raw data bytes allowed after compression (approximate, after base64 overhead)
MAX_RAW_BYTES = 2220

def compress_image(image, target_size=MAX_RAW_BYTES):
    """
    Compress the image iteratively by reducing quality and size until it fits under target_size.
    Returns a tuple of (compressed_image_bytes, final_format).
    """
    img_format = 'JPEG'  # using JPEG as a good compromise for compression
    quality = 85  # starting quality
    
    # Use BytesIO to store compressed image
    compressed_io = io.BytesIO()
    
    # Initial save
    image.save(compressed_io, format=img_format, quality=quality)
    size = compressed_io.tell()
    
    # Iteratively reduce quality until the compressed image size fits under target_size
    while size > target_size and quality > 10:
        quality -= 10
        compressed_io.seek(0)
        compressed_io.truncate(0)
        image.save(compressed_io, format=img_format, quality=quality)
        size = compressed_io.tell()
    
    # If still too large, try resizing the image
    while size > target_size:
        # Reduce size by 20%
        new_width = int(image.width * 0.8)
        new_height = int(image.height * 0.8)
        # Use Image.LANCZOS for high-quality downsampling
        image = image.resize((new_width, new_height), Image.LANCZOS)
        compressed_io.seek(0)
        compressed_io.truncate(0)
        image.save(compressed_io, format=img_format, quality=quality)
        size = compressed_io.tell()
    
    return compressed_io.getvalue(), img_format.lower()


def generate_qr_code(data):
    """
    Generates a QR code image from the provided base64-encoded data.
    """
    qr = qrcode.QRCode(
        version=40,
        error_correction=qrcode.constants.ERROR_CORRECT_L
    )
    qr.add_data(data, optimize=0)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white")
    # Save QR code image to BytesIO
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer.getvalue()


def compress_and_qr(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        try:
            # Open the uploaded image using Pillow
            image = Image.open(uploaded_file)
        except Exception as e:
            context['error'] = f"Error opening image: {str(e)}"
            return render(request, 'anyImageToQRGenerator/index.html', context)
        
        # Compress the image until it fits into the QR code capacity.
        compressed_data, img_format = compress_image(image)
        raw_size = len(compressed_data)
        
        # Encode the compressed image to a base64 string.
        b64_data = base64.b64encode(compressed_data).decode('ascii')
        
        # Generate the QR code image embedding the base64 string.
        qr_data = generate_qr_code(b64_data)
        qr_b64 = base64.b64encode(qr_data).decode('utf-8')
        
        context['qr_code'] = f"data:image/png;base64,{qr_b64}"
        context['raw_size'] = raw_size
        context['img_format'] = img_format.upper()
        context['message'] = "Image successfully compressed and embedded in QR code."
    return render(request, 'anyImageToQRGenerator/index.html', context)
