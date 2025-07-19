from django.conf import settings
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'adult':
            group, _ = Group.objects.get_or_create(name='Adult')
        elif instance.role == 'kid':
            group, _ = Group.objects.get_or_create(name='Kid')
        else:
            return 

        instance.groups.add(group)