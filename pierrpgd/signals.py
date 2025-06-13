from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import About, Experience, Education, Project, Color, Profile

def update_order(sender, instance, created, **kwargs):
    if created:
        nb_objects = sender.objects.filter(profile=instance.profile).count()
        if nb_objects > 1:
            max_order = sender.objects.filter(profile=instance.profile).aggregate(models.Max('order'))['order__max']
            instance.order = max_order + 1
        instance.save()

def create_colors_for_profile(sender, instance, created, **kwargs):
    if created:
        # Crée une ou plusieurs couleurs par défaut
        Color.objects.create(red=255, green=255, blue=255, transparency=100, profile=instance)
        Color.objects.create(red=145, green=157, blue=197, transparency=100, profile=instance)
        Color.objects.create(red=15, green=23, blue=42, transparency=100, profile=instance)

# Enregistrement des signaux
receiver(post_save, sender=Profile)(create_colors_for_profile)
receiver(post_save, sender=Color)(update_order)
receiver(post_save, sender=About)(update_order)
receiver(post_save, sender=Experience)(update_order)
receiver(post_save, sender=Education)(update_order)
receiver(post_save, sender=Project)(update_order)
