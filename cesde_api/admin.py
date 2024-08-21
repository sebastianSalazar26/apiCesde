from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([ Estados, Aspirantes, Tipo_gestion, Asesores , Gestiones , Programa , Proceso , Tipificacion , Sede])
