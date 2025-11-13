from django.contrib import admin

from .models import (
    Organization, Team, Project, Pipeline, Stage, SubStage,
    Run, StageResult, SubStageResult,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'team')


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'created_at')


class SubStageInline(admin.TabularInline):
    model = SubStage
    extra = 0


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pipeline', 'owner_team', 'weight', 'order')
    inlines = [SubStageInline]


@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'status', 'start_time', 'end_time')


@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'run', 'stage', 'completion_percentage')


@admin.register(SubStageResult)
class SubStageResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'stage_result', 'substage', 'completion_percentage', 'auto_validated')
