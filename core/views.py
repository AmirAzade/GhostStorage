from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import StreamingHttpResponse
from .client import get_client
from django.conf import settings
import mimetypes
from django.views.decorators.csrf import csrf_exempt
from telethon.tl.types import DocumentAttributeFilename
from .models import FileMap

async def index(request):
    """Renders the HTML page with the upload form."""
    return render(request, 'index.html')

@csrf_exempt
async def upload_file(request):
    """Handles upload and saves metadata to DB."""
    if request.method == 'POST' and request.FILES.get('file'):
        file_obj = request.FILES['file']
        content = file_obj.read()
        
        client = await get_client()
        
        try:
            # 1. Upload to Telegram
            message = await client.send_file(
                settings.TG_CHANNEL_ID,
                file=content,
                caption=file_obj.name,
                force_document=True,
                attributes=[DocumentAttributeFilename(file_name=file_obj.name)]
            )

            # 2. Save Mapping to Database (Sync operation inside Async view)
            # We use a wrapper or simple ORM call since simple inserts are fast
            file_map = await FileMap.objects.acreate(
                message_id=message.id,
                file_name=file_obj.name,
                file_size=file_obj.size
            )
            
            # 3. Return the UUID link
            download_url = f"/download/{file_map.uuid}/"
            
            return HttpResponse(f"""
                <div style="color: green; margin-bottom: 10px;"><b>Upload Successful!</b></div>
                File: {file_obj.name}<br>
                UUID: {file_map.uuid}<br>
                <br>
                <a href="{download_url}" class="download-btn" target="_blank">Download File</a>
            """)
        except Exception as e:
            return HttpResponse(f"<span style='color:red'>Error: {str(e)}</span>", status=500)
            
    return HttpResponse("No file provided", status=400)

async def download_file(request, file_uuid):
    """Retrieves file ID from DB using UUID and streams it."""
    
    # 1. Look up the mapping in the Database
    # We use 'aget' for async retrieval
    try:
        file_entry = await FileMap.objects.aget(uuid=file_uuid)
    except FileMap.DoesNotExist:
        return HttpResponse("File link invalid or expired", status=404)

    client = await get_client()
    
    # 2. Use the hidden message_id from the DB
    try:
        message = await client.get_messages(settings.TG_CHANNEL_ID, ids=file_entry.message_id)
    except ValueError:
        return HttpResponse("Message not found in Telegram")

    if not message or not message.file:
        return HttpResponse("File missing on Telegram server")

    # 3. Stream the file
    file_name = file_entry.file_name
    file_size = file_entry.file_size
    mime_type, _ = mimetypes.guess_type(file_name)

    async def file_iterator():
        async for chunk in client.iter_download(message.media):
            yield chunk

    response = StreamingHttpResponse(file_iterator(), content_type=mime_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    response['Content-Length'] = file_size
    return response