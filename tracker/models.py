from django.db import models
from django.utils import timezone


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Team(models.Model):
    organization = models.ForeignKey(
        Organization, related_name='teams', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = (('organization', 'name'),)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.organization.name} / {self.name}"


class Project(models.Model):
    team = models.ForeignKey(Team, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = (('team', 'name'),)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.team} / {self.name}"


class Pipeline(models.Model):
    project = models.ForeignKey(Project, related_name='pipelines', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('project', 'name'),)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.project} / {self.name}"


class Stage(models.Model):
    DOD_TYPES = (('manual', 'Manual'), ('auto', 'Automated'))

    pipeline = models.ForeignKey(Pipeline, related_name='stages', on_delete=models.CASCADE)
    owner_team = models.ForeignKey('Team', null=True, blank=True, related_name='owned_stages', on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    weight = models.FloatField(default=0.0)
    order = models.IntegerField(default=0)
    definition_of_done = models.TextField(blank=True)
    auto_check_endpoint = models.CharField(max_length=512, blank=True)
    dod_type = models.CharField(max_length=10, choices=DOD_TYPES, default='manual')

    class Meta:
        ordering = ('order',)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.pipeline.name} :: {self.name}"


class SubStage(models.Model):
    DOD_TYPES = (('manual', 'Manual'), ('auto', 'Automated'))

    stage = models.ForeignKey(Stage, related_name='substages', on_delete=models.CASCADE)
    owner_team = models.ForeignKey('Team', null=True, blank=True, related_name='owned_substages', on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    weight = models.FloatField(default=0.0)
    order = models.IntegerField(default=0)
    definition_of_done = models.TextField(blank=True)
    auto_check_endpoint = models.CharField(max_length=512, blank=True)
    dod_type = models.CharField(max_length=10, choices=DOD_TYPES, default='manual')

    class Meta:
        ordering = ('order',)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.stage.name} :: {self.name}"


class Run(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    pipeline = models.ForeignKey(Pipeline, related_name='runs', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def overall_score(self) -> float:
        """Compute the weighted overall score for this run.

        Weighted calculation:
        - For each stage, compute stage_completion from substages (weighted by substage.weight).
        - Stage contribution = stage.weight * stage_completion.
        - Normalize by total stage weight (if not 1.0).
        """
        from .services import calculate_run_score

        return calculate_run_score(self.id)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Run {self.id} - {self.pipeline.name} - {self.status}"


class StageResult(models.Model):
    run = models.ForeignKey(Run, related_name='stage_results', on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, related_name='results', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Run.STATUS_CHOICES, default='pending')
    completion_percentage = models.FloatField(default=0.0)

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = (('run', 'stage'),)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.run} :: {self.stage.name} ({self.completion_percentage}%)"


class SubStageResult(models.Model):
    stage_result = models.ForeignKey(
        StageResult, related_name='substage_results', on_delete=models.CASCADE
    )
    substage = models.ForeignKey(SubStage, related_name='results', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Run.STATUS_CHOICES, default='pending')
    completion_percentage = models.FloatField(default=0.0)
    auto_validated = models.BooleanField(default=False)

    class Meta:
        unique_together = (('stage_result', 'substage'),)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.stage_result.run} :: {self.substage.name} ({self.completion_percentage}%)"
