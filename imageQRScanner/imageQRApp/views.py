import base64
from django.shortcuts import render
from pyzbar.pyzbar import decode
from PIL import Image
import io
import imghdr

def index(request):
    context = {}
    if request.method == 'POST' and request.FILES['qrimage']:
        qrimage = request.FILES['qrimage']
        img = Image.open(qrimage)

        qr_decoded = decode(img)

        if qr_decoded:
            qr_data = qr_decoded[0].data
            image_type = imghdr.what(None, qr_data)

            if image_type in ['png', 'bmp', 'jpeg']:
                img_base64 = base64.b64encode(qr_data).decode()
                context['img_url'] = f'data:image/{image_type};base64,{img_base64}'
            else:
                context['data'] = qr_data.decode('utf-8', errors='replace')
        else:
            context['data'] = 'No QR code detected.'

    return render(request, 'imageQRApp/index.html', context)
