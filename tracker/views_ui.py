from typing import Any, Dict

from django.views.generic import ListView, DetailView

from .models import Pipeline, StageResult, SubStageResult


class PipelineListView(ListView):
    template_name = 'tracker/pipeline_list.html'
    context_object_name = 'pipelines'

    def get_queryset(self):
        return Pipeline.objects.select_related('project__team__organization').order_by('project__team__name', 'project__name', 'name')


class PipelineDashboardView(DetailView):
    template_name = 'tracker/pipeline_dashboard.html'
    model = Pipeline
    context_object_name = 'pipeline'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        pipeline: Pipeline = self.object

        run = pipeline.runs.order_by('-created_at').first()
        ctx['latest_run'] = run
        stages_data = []

        stages = pipeline.stages.select_related('owner_team').order_by('order')
        stage_results_map = {}
        sub_results_map = {}
        if run:
            sresults = StageResult.objects.filter(run=run).select_related('stage')
            stage_results_map = {sr.stage_id: sr for sr in sresults}
            ssresults = SubStageResult.objects.filter(stage_result__run=run).select_related('substage')
            # map by substage id
            for ssr in ssresults:
                sub_results_map[ssr.substage_id] = ssr

        for stage in stages:
            sres = stage_results_map.get(stage.id)
            substages_list = []
            for sub in stage.substages.select_related('owner_team').order_by('order'):
                ssr = sub_results_map.get(sub.id)
                substages_list.append({
                    'id': sub.id,
                    'name': sub.name,
                    'owner_team': getattr(sub.owner_team, 'name', None),
                    'weight': sub.weight,
                    'completion': (ssr.completion_percentage if ssr else 0.0),
                    'status': (ssr.status if ssr else 'pending'),
                })

            stages_data.append({
                'id': stage.id,
                'name': stage.name,
                'owner_team': getattr(stage.owner_team, 'name', None),
                'weight': stage.weight,
                'stage_completion': (sres.completion_percentage if sres else 0.0),
                'status': (sres.status if sres else 'pending'),
                'substages': substages_list,
            })

        ctx['stages'] = stages_data
        ctx['overall_score'] = (run.overall_score if run else 0.0)
        return ctx
