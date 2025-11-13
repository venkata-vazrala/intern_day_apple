from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Run, Stage, StageResult, SubStageResult, SubStage


@receiver(post_save, sender=Run)
def create_stage_and_substage_results(sender, instance: Run, created, **kwargs):
    """When a Run is created, create StageResult and SubStageResult placeholders.

    This allows updating individual substage results later and ensures hierarchical data exists.
    """
    if not created:
        return

    stages = Stage.objects.filter(pipeline=instance.pipeline).order_by('order')
    for stage in stages:
        sres, _ = StageResult.objects.get_or_create(
            run=instance, stage=stage, defaults={'order': stage.order}
        )
        # create substage results
        substages = SubStage.objects.filter(stage=stage).order_by('order')
        for sub in substages:
            SubStageResult.objects.get_or_create(stage_result=sres, substage=sub)
