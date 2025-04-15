from rest_framework import serializers
from .models import B2BLead, B2CLead

class B2BLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BLead
        fields = '__all__'


class B2CLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2CLead
        fields = '__all__'
