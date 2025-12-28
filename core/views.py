from django.shortcuts import render, HttpResponse
from django.http import StreamingHttpResponse
from .client import get_client
from django.conf import settings
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from telethon.tl.types import DocumentAttributeFilename

async def index(request):
    """Renders the HTML page with the upload form."""
    return render(request, 'index.html')

@csrf_exempt
async def upload_file(request):
    """Handles the file upload via AJAX."""
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        
        # Read file content into memory
        content = file_obj.read()
        
        client = await get_client()
        
        try:
            # Upload to Telegram
            message = await client.send_file(
                settings.TG_CHANNEL_ID,
                file=content,
                caption=file_obj.name,
                force_document=True,
                attributes=[
                    DocumentAttributeFilename(file_name=file_obj.name)
                ]
            )
            # Return a simple HTML snippet to display in the result box
            return HttpResponse(f"""
                <div style="color: green; margin-bottom: 10px;"><b>Upload Successful!</b></div>
                File Name: {file_obj.name}<br>
                Size: {file_obj.size} bytes<br>
                <br>
                <a href="/download/{message.id}/" class="download-btn" target="_blank">Download File</a>
            """)
        except Exception as e:
            return HttpResponse(f"<span style='color:red'>Error: {str(e)}</span>", status=500)
            
    return HttpResponse("No file provided", status=400)

async def download_file(request, msg_id):
    """Streams the file from Telegram to the user."""
    client = await get_client()
    try:
        message = await client.get_messages(settings.TG_CHANNEL_ID, ids=int(msg_id))
    except ValueError:
        return HttpResponse("Invalid Message ID")

    if not message or not message.file:
        return HttpResponse("File not found in Telegram channel")

    file_name = message.file.name or f"file_{msg_id}"
    file_size = message.file.size
    mime_type, _ = mimetypes.guess_type(file_name)

    async def file_iterator():
        # iter_download yields chunks directly to the response stream
        async for chunk in client.iter_download(message.media):
            yield chunk

    response = StreamingHttpResponse(file_iterator(), content_type=mime_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    response['Content-Length'] = file_size
    return response