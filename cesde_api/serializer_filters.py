from rest_framework import serializers
from .models import *
from datetime import datetime

# Define las constantes con los valores proporcionados
TIPIFICACIONES_INTERESADO = {
    'Matriculado': 1.0,
    'Liquidacion': 2.0,
    'En_proceso_de_selección': 14.0,
    'Interesado_en_seguimiento': 15.0,
}

TIPIFICACIONES_EN_SEGUIMIENTO = {
    'Volver_a_llamar': 16.0,
}

TIPIFICACIONES_NO_CONTACTADO = {
    'Primer_intento_de_contacto': 20.0,
    'Segundo_intento_de_contacto': 19.0,
    'Tercer_intento_de_contacto': 18.0,
    'Fuera_de_servicio': 17.0,
}

TIPIFICACIONES_DESCARTADO = {
    'Número_inválido': 3.0,
    'Imposible_contacto': 4.0,
    'Por_ubicacion': 5.0,
    'No_Manifiesta_motivo': 6.0,
    'Proxima_convocatoria': 7.0,
    'Eliminar_de_la_base': 8.0,
    'Sin_perfil': 9.0,
    'Sin_tiempo': 10.0,
    'Sin_interes': 11.0,
    'Ya_esta_estudiando_en_otra_universidad': 12.0,
    'Otra_area_de_interés': 13.0,
}

TIPIFICACIONES_OPCIONALES = {
    'Informacion_general_': 21.0,
    'No_Manifiesta_motivo': 22.0,
    'no': 23.0,
    'Cliente_en_seguimiento': 24.0,
    'TIMEOUTCHAT': 25.0,
    'Equivocado': 26.0,
    'Se_remite_a_otras_áreas': 27.0,
    'TIMEOUTACW': 28.0,
    'Cuelga_Telefono': 29.0,
    '': 30.0,
    'nan': 31.0,
}


class AspiranteFilterSerializer(serializers.ModelSerializer):
    nit = serializers.CharField(source='documento')
    nombre_completo = serializers.SerializerMethodField()
    cantidad_llamadas = serializers.SerializerMethodField()
    cantidad_whatsapp = serializers.SerializerMethodField()
    cantidad_gestiones = serializers.SerializerMethodField()
    fecha_ultima_gestion = serializers.SerializerMethodField()
    dias_ultima_gestion = serializers.SerializerMethodField()
    sede = serializers.CharField(source='sede.nombre')
    ultima_tipificacion = serializers.SerializerMethodField()
    programa_formacion = serializers.CharField(source='programa.nombre')
    nit_empresa = serializers.CharField(source='empresa.nit')
    proceso = serializers.CharField(source='proceso.nombre')
    estado_ultima_gestion = serializers.SerializerMethodField()
    mejor_gestion = serializers.SerializerMethodField()
    gestion_final = serializers.SerializerMethodField()
        

    class Meta:
        model = Aspirantes
        fields = [
            'nombre_completo',
            'nit', 
            'sede',
            'nit_empresa',  
            'programa_formacion', 
            'proceso',
            'celular',
            'cantidad_llamadas',  
            'cantidad_whatsapp', 
            'cantidad_gestiones',
            'fecha_ultima_gestion', 
            'dias_ultima_gestion',
            'ultima_tipificacion', 
            'estado_ultima_gestion',
            'mejor_gestion', 
            'gestion_final'
        ]


    # Funcion para traer el nombre completo del aspirante
    def get_nombre_completo(self, obj):
        return obj.nombre

    # Funcion para llevar el conteo de llamadas del aspirante

    def get_cantidad_llamadas(self, obj):
        llamadas_gestion = Tipo_gestion.objects.filter(
            nombre='Llamada').first()
        if llamadas_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=llamadas_gestion).count()
        return 0

    def get_cantidad_whatsapp(self, obj):
        whatsapp_gestion = Tipo_gestion.objects.filter(
            nombre='WhatsApp').first()

        # Filtramos el modelo Gestiones para contar todas las gestiones asociadas al aspirante actual (obj) y que tengan el tipo de gestión encontrado (llamadas_gestion). count() devuelve el número de estas gestiones.
        if whatsapp_gestion:
            return Gestiones.objects.filter(cel_aspirante=obj, tipo_gestion=whatsapp_gestion).count()
        return 0

    # Funcion para llevar el conteo  de gestiones

    def get_cantidad_gestiones(self, obj):
        cantidad_gestiones = Gestiones.objects.filter(
            cel_aspirante=obj).count()
        return cantidad_gestiones

    # Función para obtener la fecha de la última gestión del celular adicional 
    def get_fecha_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_gestion:
        # Formatear la fecha para que solo devuelva año, mes y día
            return ultima_gestion.fecha.strftime('%Y-%m-%d')
        return "Ninguno"
    
    # Función para obtener el estado de la última gestión del celular adicional
    def get_estado_ultima_gestion(self, obj):
        # Obtener el estado directamente desde el modelo Aspirantes
        if obj.estado:
            return obj.estado.nombre  # Accede al nombre del estado
        return "Ninguno"


    def get_ultima_tipificacion(self, obj):
        ultima_tipificacion = Gestiones.objects.filter(
            cel_aspirante=obj, fecha__isnull=False).order_by('-fecha').first()
        if ultima_tipificacion:
            # El estado de la última gestión se obtiene de la tipificación relacionada
            return ultima_tipificacion.tipificacion.nombre
        return "Ninguno"

    def get_dias_ultima_gestion(self, obj):
        ultima_gestion = Gestiones.objects.filter(
            cel_aspirante=obj,
            fecha__isnull=False
        ).order_by('-fecha').first()
        if ultima_gestion:
            fecha_ultima = ultima_gestion.fecha.date() if isinstance(
                ultima_gestion.fecha, datetime) else ultima_gestion.fecha
            delta = datetime.now().date() - fecha_ultima
            return delta.days
        return "Ninguno"
    
    # codigo nuevo
    def get_mejor_gestion(self, obj):
        gestiones = Gestiones.objects.filter(cel_aspirante=obj)
        if gestiones.exists():
            mejor_tipificacion = gestiones.order_by('tipificacion__valor_tipificacion').first()
            if mejor_tipificacion:
                return mejor_tipificacion.tipificacion.nombre
        return "Ninguno"

    def get_gestion_final(self, obj):
        gestiones = Gestiones.objects.filter(cel_aspirante=obj)
        if gestiones.exists():
            mejor_tipificacion = gestiones.order_by('tipificacion__valor_tipificacion').first()
            if mejor_tipificacion:
                return self.determine_gestion_final(mejor_tipificacion.tipificacion.nombre)
        return 'Desconocido'

    def determine_gestion_final(self, nombre_tipificacion):
        if nombre_tipificacion in TIPIFICACIONES_INTERESADO:
            return 'Interesado'
        elif nombre_tipificacion in TIPIFICACIONES_EN_SEGUIMIENTO:
            return 'En seguimiento'
        elif nombre_tipificacion in TIPIFICACIONES_NO_CONTACTADO:
            return 'No contactado'
        elif nombre_tipificacion in TIPIFICACIONES_DESCARTADO:
            return 'Descartado'
        elif nombre_tipificacion in TIPIFICACIONES_OPCIONALES:
            return 'Tipificaciones opcionales'
        return 'Desconocido'
