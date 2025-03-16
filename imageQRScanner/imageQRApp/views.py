import re
import base64
from django.shortcuts import render
from pyzbar.pyzbar import decode
from PIL import Image
import imghdr

def index(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('qrimage'):
        qrimage = request.FILES['qrimage']
        img = Image.open(qrimage)
        
        qr_decoded = decode(img)
        if qr_decoded:
            # Decode the QR code data using UTF-8, replacing errors.
            raw_data = qr_decoded[0].data.decode('utf-8', errors='replace')
            # Filter out any characters that are not valid in base64.
            b64_data = ''.join(re.findall(r'[A-Za-z0-9+/=]', raw_data))
            try:
                # Decode the cleaned base64 string back into binary image data.
                image_data = base64.b64decode(b64_data.encode('ascii'))
                
                # Determine the image type (e.g., 'png', 'bmp', or 'jpeg').
                image_type = imghdr.what(None, image_data)
                if image_type in ['png', 'bmp', 'jpeg']:
                    # Re-encode the image data for embedding in an HTML image element.
                    img_base64 = base64.b64encode(image_data).decode('utf-8')
                    context['img_url'] = f'data:image/{image_type};base64,{img_base64}'
                else:
                    context['data'] = 'Decoded binary data is not a supported image type.'
            except Exception as e:
                context['data'] = f'Error decoding base64: {str(e)}'
        else:
            context['data'] = 'No QR code detected.'

    return render(request, 'imageQRApp/index.html', context)
