import django_filters
from django_filters import ModelChoiceFilter
from .models import *
from django.db.models import Count, Q, Max, Subquery, OuterRef, F, CharField, Value, Case, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta




# Para devolver el nombre por get 
class TipificacionNameFilter(ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'nombre'
        kwargs['field_name'] = 'nombre'
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            # Subquery para obtener la última gestión de cada aspirante
            latest_gestion = Gestiones.objects.filter(
                cel_aspirante=OuterRef('pk')
            ).order_by('-fecha').values('tipificacion__nombre')[:1]

            # Filtrar el queryset de aspirantes según la última tipificación
            return qs.annotate(
                ultima_tipificacion_nombre=Subquery(latest_gestion)
            ).filter(
                ultima_tipificacion_nombre=value.nombre
            ).distinct()
        return qs
    
from django_filters import ModelChoiceFilter

class EstadoAspiranteNameFilter(ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'nombre'
        kwargs['field_name'] = 'nombre'
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(estado__nombre=value.nombre)
        return qs

class ProgramaNameFilter(ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'nombre'
        kwargs['field_name'] = 'nombre'
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(programa__nombre=value.nombre)
        return qs

class SedeNameFilter(ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'nombre'
        kwargs['field_name'] = 'nombre'
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(sede__nombre=value.nombre)
        return qs

class ProcesoNameFilter(ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['to_field_name'] = 'nombre'
        kwargs['field_name'] = 'nombre'
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(proceso__nombre=value.nombre)
        return qs


class AspirantesFilter(django_filters.FilterSet):
    proceso_nombre = ProcesoNameFilter(queryset=Proceso.objects.all(), label='Proceso Nombre')
    cantidad_llamadas = django_filters.NumberFilter(method='filter_cantidad_llamadas', label='Cantidad de llamadas')
    cantidad_whatsapp = django_filters.NumberFilter(method='filter_cantidad_whatsapp', label='Cantidad de WhatsApp')
    cantidad_gestiones = django_filters.NumberFilter(method='filter_cantidad_gestiones', label='Cantidad de gestiones')
    estado_ultima_gestion = EstadoAspiranteNameFilter(queryset=Estados.objects.all(), label='Estado del aspirante')
    dias_ultima_gestion = django_filters.NumberFilter(method='filter_dias_ultima_gestion', label='Días desde la última gestión')
    fecha_ultima_gestion = django_filters.DateFilter(method='filter_fecha_ultima_gestion', label='Fecha de última gestión')
    tipificacion_ultima_gestion = TipificacionNameFilter(queryset=Tipificacion.objects.all(), label='Tipificacion última gestión')
    programa = ProgramaNameFilter(queryset=Programa.objects.all(), label='Programa')
    sede = SedeNameFilter(queryset=Sede.objects.all(), label='Sedes')
    # nit_empresa = django_filters.CharFilter(method='filter_nit_empresa', label='Nit empresa')
    mejor_gestion = django_filters.CharFilter(method='filter_mejor_gestion', label='Mejor Gestión')

    class Meta:
        model = Aspirantes
        fields = [
            'proceso_nombre',
            'cantidad_llamadas',
            'cantidad_whatsapp',
            'cantidad_gestiones',
            'dias_ultima_gestion',
            'fecha_ultima_gestion',
            'tipificacion_ultima_gestion',
            'estado_ultima_gestion',
            'programa',
            'sede',
            # 'nit_empresa',
            'mejor_gestion',
            # 'gestion_final',
        ]


    def filter_by_proceso_nombre(self, queryset, name, value):
        """
        Filtra los aspirantes por el nombre del proceso y aplica filtros adicionales.
        """
        return queryset.filter(proceso__nombre=value)


    def filter_cantidad_llamadas(self, queryset, name, value):
        llamadas_gestion = Tipo_gestion.objects.filter(nombre='Llamada').first()
        if llamadas_gestion:
            return queryset.annotate(
                cantidad_llamadas=Count('gestiones', filter=Q(gestiones__tipo_gestion=llamadas_gestion))
            ).filter(cantidad_llamadas=value) 
        return queryset


    def filter_cantidad_whatsapp(self, queryset, name, value):
        whatsapp_gestion = Tipo_gestion.objects.filter(nombre='WhatsApp').first()
        if whatsapp_gestion:
            return queryset.annotate(
                cantidad_whatsapp=Count('gestiones', filter=Q(gestiones__tipo_gestion=whatsapp_gestion))
            ).filter(cantidad_whatsapp=value) 
        return queryset


    def filter_cantidad_gestiones(self, queryset, name, value):
        return queryset.annotate(
            cantidad_gestiones=Count('gestiones')
        ).filter(cantidad_gestiones=value) 


    def filter_estado_ultima_gestion(self, queryset, name, value):
        if value:
            # Filtrar aspirantes por el estado directamente
            return queryset.filter(estado__nombre=value)
        return queryset


    def filter_dias_ultima_gestion(self, queryset, name, value):
        if value:
            try:
                dias = int(value)
                fecha_limite = timezone.now().date() - timedelta(days=dias)

                # Anotar con la última fecha de gestión
                queryset = queryset.annotate(
                    dias_ultima_gestion=Max('gestiones__fecha')
                )

                # Filtrar aspirantes cuya última gestión sea exactamente hace el número de días especificado
                return queryset.filter(
                    dias_ultima_gestion=fecha_limite
                )
            except ValueError:
                return queryset.none()
        return queryset



    def filter_fecha_ultima_gestion(self, queryset, name, value):
        if value:
            # Subquery para obtener la última fecha de gestión por cada aspirante
            subquery = Gestiones.objects.filter(
                cel_aspirante=OuterRef('celular')
            ).values('cel_aspirante').annotate(
                ultima_fecha=Max('fecha')
            ).values('ultima_fecha')

            # Anotar el queryset con la última fecha de gestión
            queryset = queryset.annotate(
                fecha_ultima_gestion=Subquery(subquery)
            ).filter(
                fecha_ultima_gestion=value
            )

        return queryset


    def filter_tipificacion_ultima_gestion(self, queryset, name, value):
        if value:
            # Buscar la tipificación por nombre
            try:
                tipificacion = Tipificacion.objects.get(nombre=value)
                # Filtrar por la tipificación encontrada
                return queryset.filter(
                    gestiones__tipificacion=tipificacion
                ).order_by('-gestiones__fecha').distinct()
            except Tipificacion.DoesNotExist:
                return queryset.none()
        return queryset


    def filter_mejor_gestion(self, queryset, name, value):
        if value:
            # Obtener la gestión con el valor de tipificación más bajo para cada aspirante
            mejor_gestion = Gestiones.objects.filter(
                cel_aspirante=OuterRef('pk')
            ).order_by('tipificacion__valor_tipificacion', '-fecha').values('pk')[:1]

            # Filtrar el queryset solo con los aspirantes cuya mejor gestión tiene la tipificación especificada
            queryset = queryset.annotate(
                mejor_gestion_pk=Subquery(mejor_gestion)
            ).filter(
                gestiones__pk=F('mejor_gestion_pk'),
                gestiones__tipificacion__nombre=value  # Ajustar el campo aquí
            ).distinct()

            return queryset
        return queryset


# Filters para los procesos
class ProcesosFilter(django_filters.FilterSet):
    proceso = django_filters.NumberFilter(field_name='proceso_id')
    fecha_inicio = django_filters.DateFilter(field_name='gestiones__fecha', lookup_expr='gte')
    fecha_fin = django_filters.DateFilter(field_name='gestiones__fecha', lookup_expr='lte')

    class Meta:
        model = Aspirantes
        fields = ['proceso', 'fecha_inicio', 'fecha_fin']


class EstadosFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Estados
        fields = ['nombre']

class ProgramaFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    descripcion = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Programa
        fields = ['nombre', 'descripcion']


class EmpresaFilter(django_filters.FilterSet):
    nit = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta: 
        model = Empresa
        fields = ['nit']


class Tipo_gestionFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Tipo_gestion
        fields = ['nombre']

class GestionesFilter(django_filters.FilterSet):
    cel_aspirante = django_filters.CharFilter(field_name='cel_aspirante__celular', lookup_expr='icontains')
    fecha = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='exact')
    tipo_gestion = django_filters.ModelChoiceFilter(queryset=Tipo_gestion.objects.all())
    observaciones = django_filters.CharFilter(lookup_expr='icontains')
    asesor = django_filters.ModelChoiceFilter(queryset=Asesores.objects.all())

    # Modelo y campos que se pueden filtrar
    class Meta:
        model = Gestiones
        fields = ['cel_aspirante', 'fecha', 'tipo_gestion', 'observaciones', 'asesor']

class AsesoresFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateFilter(field_name='gestiones__fecha', lookup_expr='gte', label='fecha inicio')
    fecha_fin = django_filters.DateFilter(field_name='gestiones__fecha', lookup_expr='lte', label='fecha final')
    id = django_filters.CharFilter(field_name='id', label='id')
    

    class Meta:
        model = Asesores
        fields = ['fecha_inicio', 'fecha_fin', 'id']