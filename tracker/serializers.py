from rest_framework import serializers

from .models import (
    Pipeline, Stage, SubStage, Run, StageResult, SubStageResult, Team,
)


class TeamSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class SubStageSerializer(serializers.ModelSerializer):
    owner_team = TeamSlimSerializer(read_only=True)
    class Meta:
        model = SubStage
        fields = ('id', 'name', 'weight', 'order', 'definition_of_done', 'dod_type', 'auto_check_endpoint', 'owner_team')


class StageSerializer(serializers.ModelSerializer):
    owner_team = TeamSlimSerializer(read_only=True)
    substages = SubStageSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ('id', 'name', 'weight', 'order', 'definition_of_done', 'dod_type', 'auto_check_endpoint', 'owner_team', 'substages')


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = ('id', 'name', 'description', 'stages')


class SubStageResultSerializer(serializers.ModelSerializer):
    substage = SubStageSerializer(read_only=True)

    class Meta:
        model = SubStageResult
        fields = ('id', 'substage', 'start_time', 'end_time', 'status', 'completion_percentage', 'auto_validated')


class StageResultSerializer(serializers.ModelSerializer):
    stage = StageSerializer(read_only=True)
    substage_results = SubStageResultSerializer(many=True, read_only=True)

    class Meta:
        model = StageResult
        fields = ('id', 'stage', 'start_time', 'end_time', 'status', 'completion_percentage', 'substage_results')


class RunSerializer(serializers.ModelSerializer):
    pipeline = PipelineSerializer(read_only=True)
    pipeline_id = serializers.PrimaryKeyRelatedField(queryset=Pipeline.objects.all(), write_only=True, source='pipeline')
    stage_results = StageResultSerializer(many=True, read_only=True)

    class Meta:
        model = Run
        fields = ('id', 'name', 'pipeline', 'pipeline_id', 'start_time', 'end_time', 'status', 'overall_score', 'stage_results')
        read_only_fields = ('overall_score',)
