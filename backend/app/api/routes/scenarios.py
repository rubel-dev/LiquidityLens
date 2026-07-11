from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import (
    RunScenarioRequest,
    ScenarioRunResponse,
    ScenarioSummaryResponse,
)
from app.auth.scope import AccessScope, get_access_scope
from app.persistence.database import get_db_session
from app.scenarios.exceptions import (
    DuplicateScenarioRunError,
    ScenarioNotFoundError,
    ScenarioReplayError,
)
from app.scenarios.schemas import ScenarioConfig
from app.scenarios.service import ScenarioService

router = APIRouter(tags=["scenarios"])
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)


@router.get("/scenarios", response_model=list[ScenarioSummaryResponse])
def list_scenarios(
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> list[object]:
    if not scope.has_any_role("demo", "manager", "ops"):
        raise HTTPException(status_code=403, detail="demo, ops, or manager role required")
    service = ScenarioService(session)
    with session.begin():
        return list(service.repository.list_catalog())


@router.post("/scenarios/{scenario_code}/run", response_model=ScenarioRunResponse, status_code=201)
def run_scenario(
    scenario_code: str,
    payload: RunScenarioRequest,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> ScenarioRunResponse:
    if not scope.has_any_role("demo", "manager"):
        raise HTTPException(status_code=403, detail="demo or manager role required")
    config = ScenarioConfig(profile="demo")  # type: ignore[arg-type]
    try:
        result = ScenarioService(session).run_scenario(scenario_code, payload.seed, config)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (DuplicateScenarioRunError, ScenarioReplayError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ScenarioRunResponse(
        run_ref=result.run_ref,
        scenario_code=result.scenario_code,
        status=result.status,
        seed=result.seed,
        fingerprint=result.fingerprint,
        generated_counts=result.generated_counts,
    )


@router.post("/scenario-runs/{run_id}/reset", response_model=ScenarioRunResponse)
def reset_scenario_run(
    run_id: str,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> ScenarioRunResponse:
    if not scope.has_any_role("demo", "manager"):
        raise HTTPException(status_code=403, detail="demo or manager role required")
    try:
        result = ScenarioService(session).reset(run_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ScenarioRunResponse(
        run_ref=result.run_ref,
        scenario_code=result.scenario_code,
        status=result.status,
        seed=result.seed,
        fingerprint=result.fingerprint,
        generated_counts=result.generated_counts,
    )


@router.post("/scenario-runs/{run_id}/replay", response_model=ScenarioRunResponse, status_code=201)
def replay_scenario_run(
    run_id: str,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> ScenarioRunResponse:
    if not scope.has_any_role("demo", "manager"):
        raise HTTPException(status_code=403, detail="demo or manager role required")
    try:
        result = ScenarioService(session).replay(run_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ScenarioReplayError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ScenarioRunResponse(
        run_ref=result.run_ref,
        scenario_code=result.scenario_code,
        status=result.status,
        seed=result.seed,
        fingerprint=result.fingerprint,
        generated_counts=result.generated_counts,
    )
