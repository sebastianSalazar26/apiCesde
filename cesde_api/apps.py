from django.apps import AppConfig

class CesdeApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cesde_api'
    
    def ready(self):
        # Importa el archivo de señales para que las señales se registren
        import cesde_api.signals
