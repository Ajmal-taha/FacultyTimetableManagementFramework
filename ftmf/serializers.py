from rest_framework import serializers
from .models import Subject

class SubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']