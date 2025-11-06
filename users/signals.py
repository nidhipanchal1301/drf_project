from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import User



@receiver(pre_save, sender=User)
def before_user_save(sender, instance, **kwargs):
    # Capitalize username before saving
    if instance.username:
        instance.username = instance.username.capitalize()
    print(f"Pre Save: About to save user — {instance.username}")


@receiver(post_save, sender=User)
def after_user_save(sender, instance, created, **kwargs):
    if created:
        print(f"Post Save: New user created — {instance.username}")
    else:
        print(f"Post Save: Existing user updated — {instance.username}")


@receiver(post_delete, sender=User)
def after_user_delete(sender, instance, **kwargs):
    print(f"Post Delete: User deleted — {instance.username}")
