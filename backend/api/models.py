from django.db import models
from django.contrib.auth.models import User
import os

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    
    summary_data = models.JSONField(null=True, blank=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f"{self.filename()} - {self.uploaded_at}"
