import random
from django.core.management.base import BaseCommand
from django.utils import timezone

from tracker.models import Pipeline, Run, StageResult


class Command(BaseCommand):
    help = 'Simulate a run for a pipeline (creates Run and random Stage/SubStage results)'

    def add_arguments(self, parser):
        parser.add_argument('pipeline_id', type=int, help='Pipeline ID to simulate')

    def handle(self, *args, **options):
        pid = options['pipeline_id']
        try:
            pipeline = Pipeline.objects.get(pk=pid)
        except Pipeline.DoesNotExist:
            self.stderr.write('Pipeline not found')
            return

        run = Run.objects.create(pipeline=pipeline, name=f"Simulated run {timezone.now().isoformat()}", status='running')

        # stage and substage results were auto-created by signals; populate them
        for sres in StageResult.objects.filter(run=run):
            # random completion for stage
            s_completion = 0.0
            for ssr in sres.substage_results.all():
                val = random.choice([0, 25, 50, 75, 100])
                ssr.completion_percentage = val
                ssr.status = 'completed' if val == 100 else 'running'
                ssr.save()
                s_completion += (ssr.completion_percentage or 0.0)

            # average completion across substages
            num = max(sres.substage_results.count(), 1)
            sres.completion_percentage = round(s_completion / num, 2)
            sres.status = 'completed' if sres.completion_percentage == 100 else 'running'
            sres.save()

        # finish run
        run.status = 'completed'
        run.end_time = timezone.now()
        run.save()

        self.stdout.write(self.style.SUCCESS(f'Created simulated run {run.id} for pipeline {pipeline.id}'))
