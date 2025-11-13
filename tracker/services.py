from .models import Run


def calculate_run_score(run_id: int) -> float:
    """Calculate weighted overall score for a run.

    Algorithm:
    - For each stage in the run, compute stage_completion as weighted sum of its substage completions.
      Each substage contributes: (substage.weight / total_substage_weight) * (completion_percentage / 100)
    - Stage contribution = stage.weight * stage_completion
    - Overall = sum(stage_contributions) / total_stage_weights

    Returns a float between 0.0 and 100.0 representing percentage complete.
    """
    try:
        run = Run.objects.get(pk=run_id)
    except Run.DoesNotExist:
        return 0.0

    total_stage_weight = 0.0
    overall_score = 0.0

    for sres in run.stage_results.select_related('stage').all():
        stage = sres.stage
        total_stage_weight += stage.weight

        # gather substage results and weights
        sub_results = sres.substage_results.select_related('substage').all()
        if not sub_results:
            # if no substages, use stage result percentage directly
            stage_completion = (sres.completion_percentage or 0.0) / 100.0
        else:
            # normalize substage weights
            total_sub_w = sum((sr.substage.weight or 0.0) for sr in sub_results) or 1.0
            stage_completion = 0.0
            for sr in sub_results:
                w = (sr.substage.weight or 0.0) / total_sub_w
                stage_completion += w * ((sr.completion_percentage or 0.0) / 100.0)

        overall_score += (stage.weight or 0.0) * stage_completion

    if total_stage_weight <= 0:
        return 0.0

    # normalize to percentage
    normalized = overall_score / total_stage_weight
    return round(normalized * 100.0, 2)
