import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import UploadedFile
from .serializers import UploadedFileSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'error': 'Username and Password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class UploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if 'file' not in request.data:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.data['file']
        if not file_obj.name.endswith('.csv'):
             return Response({"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)

    
        instance = UploadedFile.objects.create(user=request.user, file=file_obj)

        try:
            # Process with Pandas
            df = pd.read_csv(instance.file.path)
            
            # Basic validation of columns
            required_cols = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                instance.delete()
                return Response({"error": f"Missing columns: {missing}"}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate Summary
            summary = {
                "total_count": len(df),
                "averages": {
                    "Flowrate": df['Flowrate'].mean(),
                    "Pressure": df['Pressure'].mean(),
                    "Temperature": df['Temperature'].mean()
                },
                "type_distribution": df['Type'].value_counts().to_dict()
            }
            
            instance.summary_data = summary
            instance.save()

           
            files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
            if files.count() > 5:
                # Delete the ones after the 5th
                for f in files[5:]:
                    f.delete()

            serializer = UploadedFileSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            instance.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
        serializer = UploadedFileSerializer(files, many=True)
        return Response(serializer.data)

class DataDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            instance = UploadedFile.objects.get(pk=pk, user=request.user)
            df = pd.read_csv(instance.file.path)
            data = df.to_dict(orient='records')
            return Response(data)
        except UploadedFile.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
