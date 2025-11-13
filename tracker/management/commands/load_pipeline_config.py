import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tracker.models import Pipeline, Stage, SubStage, Project, Team, Organization


class Command(BaseCommand):
    help = 'Load or update a pipeline configuration from a JSON file in configs/'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to pipeline JSON config')

    def handle(self, *args, **options):
        path = Path(options['path'])
        if not path.exists():
            raise CommandError(f'Config file not found: {path}')

        data = json.loads(path.read_text())

        pipeline_name = data.get('pipeline_name') or data.get('name')
        description = data.get('description', '')
        project_name = data.get('project', 'Default Project')
        team_name = data.get('team', 'Default Team')
        org_name = data.get('organization', 'Default Org')

        with transaction.atomic():
            org, _ = Organization.objects.get_or_create(name=org_name)
            team, _ = Team.objects.get_or_create(organization=org, name=team_name)
            project, _ = Project.objects.get_or_create(team=team, name=project_name)

            pipeline, created = Pipeline.objects.get_or_create(project=project, name=pipeline_name, defaults={'description': description})
            if not created:
                pipeline.description = description
                pipeline.save()

            # stages
            stages = data.get('stages', [])
            for s_idx, s in enumerate(stages):
                # Resolve owner team for the stage if provided
                stage_owner_team = None
                owner_team_name = s.get('owner_team')
                if owner_team_name:
                    stage_owner_team, _ = Team.objects.get_or_create(organization=org, name=owner_team_name)
                stage_obj, _ = Stage.objects.update_or_create(
                    pipeline=pipeline, name=s['name'],
                    defaults={
                        'weight': float(s.get('weight', 0.0)),
                        'order': s_idx,
                        'definition_of_done': s.get('definition_of_done', ''),
                        'dod_type': s.get('type', 'manual'),
                        'auto_check_endpoint': s.get('endpoint', ''),
                        'owner_team': stage_owner_team,
                    }
                )

                for ss_idx, ss in enumerate(s.get('substages', [])):
                    sub_owner_team = None
                    ss_owner_team_name = ss.get('owner_team')
                    if ss_owner_team_name:
                        sub_owner_team, _ = Team.objects.get_or_create(organization=org, name=ss_owner_team_name)
                    SubStage.objects.update_or_create(
                        stage=stage_obj, name=ss['name'],
                        defaults={
                            'weight': float(ss.get('weight', 0.0)),
                            'order': ss_idx,
                            'definition_of_done': ss.get('definition_of_done', ''),
                            'dod_type': ss.get('type', 'manual'),
                            'auto_check_endpoint': ss.get('endpoint', ''),
                            'owner_team': sub_owner_team,
                        }
                    )

        self.stdout.write(self.style.SUCCESS(f'Loaded pipeline: {pipeline.name}'))
