from typing import Optional
from fastapi import APIRouter, Depends
from app.schemas.verification import (
    VerificationRunResponse,
    VerificationCheckResponse,
    ComplianceScoreResponse,
    ScoreComponentResponse,
    RiskAssessmentResponse,
    RiskFactorResponse,
    AIRecommendationResponse,
    FactComparisonResponse,
)
from app.services.verification_service import VerificationService
from app.dependencies import get_verification_service

router = APIRouter(tags=["Verification"])


@router.get("/verification-runs/{run_id}", response_model=VerificationRunResponse)
async def get_verification_run(
    run_id: str,
    verification_service: VerificationService = Depends(get_verification_service),
):
    run = await verification_service.get_run_by_id(run_id)

    # Map checks
    checks_res = []
    for c in run.checks:
        fc = None
        if c.fact_comparison:
            fc = FactComparisonResponse(
                matched=c.fact_comparison.matched,
                discrepancies=c.fact_comparison.discrepancies,
                field_comparisons=c.fact_comparison.field_comparisons,
            )
        checks_res.append(
            VerificationCheckResponse(
                id=c.id,
                run_id=c.run_id,
                requirement_code=c.requirement_code,
                rule_code=c.rule_code,
                check_name=c.check_name,
                document_type=c.document_type,
                document_id=c.document_id,
                status=c.status,
                extracted_facts=c.extracted_facts,
                source_facts=c.source_facts,
                fact_comparison=fc,
                reason=c.reason,
                evidence=c.evidence,
                evaluated_at=c.evaluated_at,
            )
        )

    # Map score
    score_res = None
    if run.score:
        score_res = ComplianceScoreResponse(
            total_score=run.score.total_score,
            passed_count=run.score.passed_count,
            failed_count=run.score.failed_count,
            review_count=run.score.review_count,
            na_count=run.score.na_count,
            components=[
                ScoreComponentResponse(
                    requirement_code=sc.requirement_code,
                    rule_code=sc.rule_code,
                    weight=sc.weight,
                    status=sc.status,
                    points_awarded=sc.points_awarded,
                    max_possible_points=sc.max_possible_points,
                    notes=sc.notes,
                )
                for sc in run.score.components
            ],
        )

    # Map risk
    risk_res = None
    if run.risk_assessment:
        risk_res = RiskAssessmentResponse(
            risk_level=run.risk_assessment.risk_level,
            risk_score=run.risk_assessment.risk_score,
            primary_risk_drivers=run.risk_assessment.primary_risk_drivers,
            risk_factors=[
                RiskFactorResponse(
                    category=rf.category,
                    severity=rf.severity,
                    description=rf.description,
                    impact=rf.impact,
                )
                for rf in run.risk_assessment.risk_factors
            ],
        )

    # Map AI recommendation
    ai_res = None
    if run.ai_recommendation:
        ai_res = AIRecommendationResponse(
            summary=run.ai_recommendation.summary,
            risk_explanation=run.ai_recommendation.risk_explanation,
            key_findings=run.ai_recommendation.key_findings,
            suggested_action=run.ai_recommendation.suggested_action,
            drafted_reason=run.ai_recommendation.drafted_reason,
        )

    return VerificationRunResponse(
        id=run.id,
        bid_id=run.bid_id,
        bidder_id=run.bidder_id,
        correlation_id=run.correlation_id,
        status=run.status,
        current_stage=run.current_stage,
        progress_pct=run.progress_pct,
        checks=checks_res,
        score=score_res,
        risk_assessment=risk_res,
        ai_recommendation=ai_res,
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
    )


@router.get("/verification-checks/{check_id}", response_model=VerificationCheckResponse)
async def get_verification_check(
    check_id: str,
    verification_service: VerificationService = Depends(get_verification_service),
):
    c = await verification_service.get_check_by_id(check_id)
    fc = None
    if c.fact_comparison:
        fc = FactComparisonResponse(
            matched=c.fact_comparison.matched,
            discrepancies=c.fact_comparison.discrepancies,
            field_comparisons=c.fact_comparison.field_comparisons,
        )
    return VerificationCheckResponse(
        id=c.id,
        run_id=c.run_id,
        requirement_code=c.requirement_code,
        rule_code=c.rule_code,
        check_name=c.check_name,
        document_type=c.document_type,
        document_id=c.document_id,
        status=c.status,
        extracted_facts=c.extracted_facts,
        source_facts=c.source_facts,
        fact_comparison=fc,
        reason=c.reason,
        evidence=c.evidence,
        evaluated_at=c.evaluated_at,
    )


@router.post("/verification-checks/{check_id}/retry", response_model=VerificationCheckResponse)
async def retry_verification_check(
    check_id: str,
    verification_service: VerificationService = Depends(get_verification_service),
):
    c = await verification_service.retry_check(check_id)
    fc = None
    if c.fact_comparison:
        fc = FactComparisonResponse(
            matched=c.fact_comparison.matched,
            discrepancies=c.fact_comparison.discrepancies,
            field_comparisons=c.fact_comparison.field_comparisons,
        )
    return VerificationCheckResponse(
        id=c.id,
        run_id=c.run_id,
        requirement_code=c.requirement_code,
        rule_code=c.rule_code,
        check_name=c.check_name,
        document_type=c.document_type,
        document_id=c.document_id,
        status=c.status,
        extracted_facts=c.extracted_facts,
        source_facts=c.source_facts,
        fact_comparison=fc,
        reason=c.reason,
        evidence=c.evidence,
        evaluated_at=c.evaluated_at,
    )
