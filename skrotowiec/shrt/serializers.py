from rest_framework import serializers
from skrotowiec.shrt import models as shrt_models

class ShortenedURLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = shrt_models.ShortenedURL
        fields = ['url', 'full']
