from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.conf import settings  # aby odwołać się do User modelu
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'adult':
            group, _ = Group.objects.get_or_create(name='Adult')
        elif instance.role == 'kid':
            group, _ = Group.objects.get_or_create(name='Kid')
        else:
            return  # brak dopasowania, nic nie robimy

        instance.groups.add(group)