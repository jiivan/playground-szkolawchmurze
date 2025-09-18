from rest_framework import permissions
from rest_framework import viewsets
from skrotowiec.shrt.models import ShortenedURL
from skrotowiec.shrt.serializers import ShortenedURLSerializer

class ShortenedURLViewSet(viewsets.ModelViewSet):
    """API endpoint that allows urls to be created or viewed"""
    queryset = ShortenedURL.objects.all().order_by('-date_created')
    serializer_class = ShortenedURLSerializer

    def get_permissions(self):
        if self.action in ('create', 'retrieve'):
            return [permissions.AllowAny()]
        return super().get_permissions()
