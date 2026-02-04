from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    filename = serializers.CharField(read_only=True)

    class Meta:
        model = UploadedFile
        fields = ['id', 'user', 'file', 'uploaded_at', 'summary_data', 'filename']
        read_only_fields = ['user', 'summary_data']
