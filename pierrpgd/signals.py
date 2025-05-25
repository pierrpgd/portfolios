from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import About, Experience, Project

def update_order(sender, instance, created, **kwargs):
    if created:
        nb_objects = sender.objects.filter(profile=instance.profile).count()
        if nb_objects > 1:
            max_order = sender.objects.filter(profile=instance.profile).aggregate(models.Max('order'))['order__max']
            instance.order = max_order + 1
        instance.save()

# Enregistrement des signaux
receiver(post_save, sender=About)(update_order)
receiver(post_save, sender=Experience)(update_order)
receiver(post_save, sender=Project)(update_order)
