from sqlalchemy.orm import Session

from app.scenarios.schemas import ScenarioRunResult
from app.scenarios.service import ScenarioService


def reset_scenario_run(session: Session, run_ref_or_uuid: str) -> ScenarioRunResult:
    return ScenarioService(session).reset(run_ref_or_uuid)
