from django.db.models import Count
from .models import *

def obtener_estadisticas_generales(queryset):
    # Obtener estadísticas básicas por estado y proceso
    estadisticas_basicas = queryset.values('estado__nombre').annotate(count=Count('estado')).order_by('-count')

    # Contar gestiones por tipo de contacto
    gestiones_totales = queryset.filter(gestiones__isnull=False).count()
    contactabilidad_count = queryset.filter(gestiones__tipificacion__contacto=True).count()
    no_contactabilidad_count = queryset.filter(gestiones__tipificacion__contacto=False).count()

    # Calcular los porcentajes basados en gestiones
    contactabilidad_percentage = (contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0
    no_contactabilidad_percentage = (no_contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0

    # Integrar las estadísticas adicionales en la respuesta
    estadisticas = {
        'estadisticas_basicas': list(estadisticas_basicas),
        'contactabilidad': {
            'count': contactabilidad_count,
            'percentage': contactabilidad_percentage,
        },
        'no_contactabilidad': {
            'count': no_contactabilidad_count,
            'percentage': no_contactabilidad_percentage,
        },
    }

    return estadisticas


def obtener_estadisticas_por_fechas(queryset, fecha_inicio, fecha_fin):
    # Filtrar gestiones por el rango de fechas
    gestiones_filtradas = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
    
    # Obtener los IDs de los aspirantes relacionados con las gestiones filtradas
    aspirantes_ids = gestiones_filtradas.values_list('cel_aspirante_id', flat=True).distinct()
    
    # Filtrar aspirantes por los IDs obtenidos
    aspirantes_filtrados = Aspirantes.objects.filter(celular__in=aspirantes_ids)
    
    # Obtener estadísticas básicas por estado para los aspirantes filtrados
    estadisticas = aspirantes_filtrados.values('estado__nombre').annotate(count=Count('estado')).order_by('-count')

    return {
        'estadisticas': list(estadisticas),
    }


def obtener_contactabilidad(gestiones_queryset):
    # Total de gestiones
    gestiones_totales = gestiones_queryset.count()

    # Contar gestiones por tipo de contacto
    contactabilidad_count = gestiones_queryset.filter(tipificacion__contacto=True).count()
    no_contactabilidad_count = gestiones_queryset.filter(tipificacion__contacto=False).count()

    # Calcular porcentajes
    contactabilidad_percentage = (contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0
    no_contactabilidad_percentage = (no_contactabilidad_count / gestiones_totales * 100) if gestiones_totales > 0 else 0

    return {
        'contactabilidad': {
            'count': contactabilidad_count,
            'percentage': contactabilidad_percentage,
        },
        'no_contactabilidad': {
            'count': no_contactabilidad_count,
            'percentage': no_contactabilidad_percentage,
        },
    }