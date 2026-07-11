from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.persistence.models.enums import ScenarioRunStatus
from app.scenarios.catalog import CANONICAL_SCENARIOS
from app.scenarios.exceptions import ScenarioReplayError
from app.scenarios.generators import generate_scenario
from app.scenarios.repository import ScenarioRepository
from app.scenarios.schemas import (
    CATALOG_VERSION,
    GENERATOR_VERSION,
    ProfileName,
    ScenarioConfig,
    ScenarioRunResult,
)


class ScenarioService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ScenarioRepository(session)

    def list_scenarios(self) -> list[dict[str, str]]:
        return [
            {"code": scenario.code, "name": scenario.name, "description": scenario.description}
            for scenario in self.repository.list_catalog()
        ]

    def run_scenario(
        self,
        scenario_code: str,
        seed: str | int,
        config: ScenarioConfig | None = None,
    ) -> ScenarioRunResult:
        active_config = config or ScenarioConfig()
        if scenario_code not in CANONICAL_SCENARIOS:
            raise ScenarioReplayError(f"unknown scenario: {scenario_code}")
        with self.session.begin():
            run_ref = active_config.requested_run_ref or self.repository.next_run_ref()
            self.repository.assert_run_ref_available(run_ref)
            generated = generate_scenario(scenario_code, seed, run_ref, active_config)
            refs = self.repository.reference_data_for(scenario_code)
            self.repository.create_run(generated, refs, active_config)
        return ScenarioRunResult(
            run_ref=generated.run_ref,
            scenario_code=generated.definition.code,
            status=ScenarioRunStatus.COMPLETED.value,
            seed=generated.seed,
            fingerprint=generated.fingerprint,
            generated_counts=generated.generated_counts,
        )

    def reset(self, run_ref_or_uuid: str) -> ScenarioRunResult:
        with self.session.begin():
            run = self.repository.find_run(run_ref_or_uuid)
            metadata = self.repository.run_created_metadata(run)
            self.repository.reset_run_data(run)
        return ScenarioRunResult(
            run_ref=str(metadata["run_ref"]),
            scenario_code=str(metadata["scenario_code"]),
            status=ScenarioRunStatus.PENDING.value,
            seed=str(metadata["seed"]),
            fingerprint="",
            generated_counts={},
        )

    def replay(self, run_ref_or_uuid: str) -> ScenarioRunResult:
        with self.session.begin():
            run = self.repository.find_run(run_ref_or_uuid)
            metadata = self.repository.run_created_metadata(run)
            if metadata["generator_version"] != GENERATOR_VERSION:
                raise ScenarioReplayError("generator version mismatch; replay refused")
            if metadata["catalog_version"] != CATALOG_VERSION:
                raise ScenarioReplayError("catalog version mismatch; replay refused")
            self.repository.reset_run_data(run)
            start_timestamp = datetime.fromisoformat(str(metadata["start_timestamp"]))
            config = ScenarioConfig(
                profile=cast(ProfileName, metadata["profile"]),
                start_timestamp=start_timestamp,
                requested_run_ref=str(metadata["run_ref"]),
            )
            generated = generate_scenario(
                str(metadata["scenario_code"]),
                str(metadata["seed"]),
                str(metadata["run_ref"]),
                config,
            )
            refs = self.repository.reference_data_for(str(metadata["scenario_code"]))
            run.status = ScenarioRunStatus.RUNNING
            run.started_at = generated.start_timestamp
            self.repository.persist_generated_records(run, generated, refs)
        return ScenarioRunResult(
            run_ref=generated.run_ref,
            scenario_code=generated.definition.code,
            status=ScenarioRunStatus.COMPLETED.value,
            seed=generated.seed,
            fingerprint=generated.fingerprint,
            generated_counts=generated.generated_counts,
        )
