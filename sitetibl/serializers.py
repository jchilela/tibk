from rest_framework import serializers
from .models import Escala

class EscalaSerializer(serializers.ModelSerializer):
    irmao = serializers.StringRelatedField()
    funcao = serializers.StringRelatedField()

    class Meta:
        model = Escala
        fields = ['id', 'irmao', 'funcao']