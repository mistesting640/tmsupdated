# tickets/signals.py
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    if created:
        # Example: first user = admin, others = customer
        if User.objects.count() == 1:
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()
        else:
            customer_group, _ = Group.objects.get_or_create(name='Customer')
            instance.groups.add(customer_group)