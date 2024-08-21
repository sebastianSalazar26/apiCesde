from rest_framework import serializers
from .models import *
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Q

class ConsultaAsesoresSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=15)
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    cantidad_matriculas = serializers.SerializerMethodField()
    cantidad_liquidaciones = serializers.SerializerMethodField()
    fecha_inicio = serializers.SerializerMethodField()
    fecha_fin = serializers.SerializerMethodField()

    class Meta:
        model = Asesores
        fields = [
            'id',
            'nombre_completo',
            'cantidad_llamadas',
            'cantidad_whatsapp',
            'cantidad_gestiones',
            'cantidad_matriculas',  
            'cantidad_liquidaciones',
            'fecha_inicio',
            'fecha_fin'
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.nombre_completo}".strip()

    def get_fecha_range(self):
        fecha_inicio = self.context['request'].query_params.get('fecha_inicio')
        fecha_fin = self.context['request'].query_params.get('fecha_fin')
        return fecha_inicio, fecha_fin

    def get_cantidad_llamadas(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        llamadas_gestion = Tipo_gestion.objects.filter(nombre='Llamada').first()
        if llamadas_gestion:
            query = Gestiones.objects.filter(asesor=obj, tipo_gestion=llamadas_gestion)
            if fecha_inicio:
                query = query.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                query = query.filter(fecha__lte=fecha_fin)
            return query.count()
        return 0

    def get_cantidad_whatsapp(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        whatsapp_gestion = Tipo_gestion.objects.filter(nombre='WhatsApp').first()
        if whatsapp_gestion:
            query = Gestiones.objects.filter(asesor=obj, tipo_gestion=whatsapp_gestion)
            if fecha_inicio:
                query = query.filter(fecha__gte=fecha_inicio)
            if fecha_fin:
                query = query.filter(fecha__lte=fecha_fin)
            return query.count()
        return 0

    def get_cantidad_gestiones(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        query = Gestiones.objects.filter(asesor=obj)
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.count()

    def get_cantidad_matriculas(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        matriculado_tipificacion = 'matriculado'
        query = Gestiones.objects.filter(
            asesor=obj,
            tipificacion__nombre=matriculado_tipificacion
        )
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.distinct().count()

    def get_cantidad_liquidaciones(self, obj):
        fecha_inicio, fecha_fin = self.get_fecha_range()
        liquidado_tipificacion = 'liquidado'
        query = Gestiones.objects.filter(
            asesor=obj,
            tipificacion__nombre=liquidado_tipificacion
        )
        if fecha_inicio:
            query = query.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha__lte=fecha_fin)
        return query.distinct().count()

    # Función para obtener la fecha de la primera gestión (fecha_inicio)
    def get_fecha_inicio(self, obj):
        primera_gestion = Gestiones.objects.filter(
            asesor=obj, fecha__isnull=False).order_by('fecha').first()
        if primera_gestion:
            return primera_gestion.fecha.strftime('%Y-%m-%d')
        return None

    # Función para obtener la fecha de la última gestión (fecha_fin)
    def get_fecha_fin(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            asesor=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
            return ultima_gestion.fecha.strftime('%Y-%m-%d')
        return None
    