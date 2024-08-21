from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'sede', SedeViewSet)
router.register(r'asesores' , AsesorViewSet)
router.register(r'estados', EstadoViewSet)
router.register(r'aspirantes', AspiranteViewSet)
router.register(r'filter-procesos', FilterProcesosViewSet, basename='filter-procesos')
router.register(r'aspirantes-filter', AspiranteFilterViewSet, basename='aspirantes-filter')
router.register(r'consulta_asesores', ConsultaAsesoresViewSet, basename='consulta_asesores')
router.register(r'estadisticas', EstadisticasViewSet, basename='estadisticas')
router.register(r'tipo-gestion', TipoGestionViewSet)
router.register(r'programas', ProgramaViewSet)
router.register(r'empresas', EmpresaViewSet)
router.register(r'procesos', ProcesoViewSet )
router.register(r'tipificaciones' , TipificacionViewSet)
router.register(r'gestiones', GestionViewSet)
router.register(r'historico', HistoricoViewSet, basename='historico')


urlpatterns = [
    path('', include(router.urls)),
    path('cargar_csv/', Cargarcsv.as_view(), name='cargar_csv'),

]
