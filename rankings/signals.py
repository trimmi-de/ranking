from django.db.models.signals import pre_delete
from django.dispatch import receiver

from rankings.models import Match


@receiver(pre_delete, sender=Match)
def delete_related_teams(sender, instance, **kwargs):
    # Delete all related teams before deleting the match instance
    instance.teams.all().delete()
