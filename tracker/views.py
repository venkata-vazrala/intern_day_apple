from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Pipeline, Run, StageResult, SubStageResult
from .serializers import PipelineSerializer, RunSerializer
from .services import calculate_run_score


class PipelineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer

    @action(detail=True, methods=['get'])
    def trend(self, request, pk=None):
        """Return trend metrics for last N runs. Accepts ?n=10"""
        pipeline = self.get_object()
        n = int(request.query_params.get('n', 10))
        runs = pipeline.runs.order_by('-created_at')[:n]
        data = []
        for run in runs:
            data.append({'run_id': run.id, 'created_at': run.created_at, 'score': run.overall_score})
        return Response(data)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().order_by('-created_at')
    serializer_class = RunSerializer

    def create(self, request, *args, **kwargs):
        """Create a Run and return it. Expects pipeline_id in body."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = serializer.save()
        return Response(self.get_serializer(run).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_stage(self, request, pk=None):
        """Update stage or substage status. Body should contain 'stage_id' or 'substage_id' and fields to update."""
        run = self.get_object()
        stage_id = request.data.get('stage_id')
        substage_id = request.data.get('substage_id')

        if substage_id:
            try:
                ssr = SubStageResult.objects.get(stage_result__run=run, substage_id=substage_id)
            except SubStageResult.DoesNotExist:
                return Response({'detail': 'SubStageResult not found'}, status=404)
            # update allowed fields
            for fld in ('status', 'completion_percentage', 'start_time', 'end_time', 'auto_validated'):
                if fld in request.data:
                    setattr(ssr, fld, request.data[fld])
            ssr.save()
        elif stage_id:
            try:
                sr = StageResult.objects.get(run=run, stage_id=stage_id)
            except StageResult.DoesNotExist:
                return Response({'detail': 'StageResult not found'}, status=404)
            for fld in ('status', 'completion_percentage', 'start_time', 'end_time'):
                if fld in request.data:
                    setattr(sr, fld, request.data[fld])
            sr.save()
        else:
            return Response({'detail': 'stage_id or substage_id required'}, status=400)

        # Recalculate overall score
        score = calculate_run_score(run.id)
        return Response({'overall_score': score})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Return full hierarchical breakdown for a run."""
        run = self.get_object()
        serializer = self.get_serializer(run)
        return Response(serializer.data)
