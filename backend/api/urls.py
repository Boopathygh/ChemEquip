from django.urls import path
from .views import UploadView, HistoryView, DataDetailView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('upload/', UploadView.as_view(), name='api-upload'),
    path('history/', HistoryView.as_view(), name='api-history'),
    path('data/<int:pk>/', DataDetailView.as_view(), name='api-data-detail'),
]
