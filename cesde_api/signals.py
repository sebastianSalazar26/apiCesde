from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Gestiones, Aspirantes

@receiver(post_save, sender=Gestiones)
def actualizar_estado_aspirante(sender, instance, **kwargs):
    # Llama al método de actualización de estado en el aspirante relacionado
    aspirante = instance.aspirante  # Asume que tienes una relación ForeignKey
    aspirante.actualizar_estado()