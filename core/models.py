from django.db import models
import uuid

class FileMap(models.Model):
    # This creates a long, random, unique string (e.g., 550e8400-e29b...)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The secret ID on Telegram
    message_id = models.BigIntegerField()
    
    # Metadata for better UX
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.uuid})"