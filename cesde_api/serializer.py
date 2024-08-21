from rest_framework import serializers
from .models import *
from datetime import datetime
from .models import *


class SedeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sede
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = ['nombre']


class TipoGestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_gestion
        fields = '__all__'


class GestionSerializer(serializers.ModelSerializer):
    tipo_gestion = serializers.SerializerMethodField()
    tipificacion = serializers.SerializerMethodField()
    asesor = serializers.SerializerMethodField()
    estado_aspirante = serializers.CharField(source='cel_aspirante.estado.nombre')

    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion',
                'observaciones', 'tipificacion', 'asesor', 'estado_aspirante']

    def get_tipo_gestion(self, obj):
        return obj.tipo_gestion.nombre

    def get_tipificacion(self, obj):
        return obj.tipificacion.nombre

    def get_asesor(self, obj):
        if obj.asesor:
            return {
                'id': obj.asesor.id,
                'nombre_completo': obj.asesor.nombre_completo
            }
        return None

class ProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programa
        fields = '__all__'

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class ProcesoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proceso
        fields = '__all__'

class AsesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asesores
        fields = '__all__'

class TipificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipificacion
        fields = '__all__'

