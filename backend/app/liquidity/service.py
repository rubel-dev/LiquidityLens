import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.liquidity.forecast import calculate_forecast
from app.liquidity.repository import LiquidityRepository
from app.liquidity.schemas import (
    ForecastConfig,
    ForecastRequest,
    ForecastResult,
    ForecastScope,
)


class LiquidityForecastingService:
    def __init__(self, session: Session, config: ForecastConfig | None = None) -> None:
        self.session = session
        self.config = config or ForecastConfig()
        self.repository = LiquidityRepository(session)

    def forecast_agent(
        self,
        agent_id: uuid.UUID,
        *,
        scenario_run_id: uuid.UUID | None = None,
        generated_at: datetime | None = None,
    ) -> tuple[ForecastResult, ...]:
        with self.session.begin():
            self.repository.require_agent(agent_id)
            run = self.repository.require_run(scenario_run_id)
            as_of = generated_at or (None if run is None else run.ended_at) or datetime.now(UTC)
            if as_of.tzinfo is None:
                raise ValueError("forecast generated timestamp must be timezone-aware")
            provider_ids = self.repository.provider_ids_for_agent(agent_id)
            event_context = self.repository.event_context(run)
            results: list[ForecastResult] = []

            for provider_id in provider_ids:
                balance = self.repository.current_provider_balance(
                    agent_id,
                    provider_id,
                    scenario_run_id,
                    as_of,
                )
                transactions = self.repository.validated_transactions(
                    agent_id,
                    provider_id,
                    scenario_run_id,
                    as_of - timedelta(minutes=self.config.rolling_window_minutes),
                    as_of,
                )
                quality = self.repository.data_quality_context(
                    agent_id,
                    (provider_id,),
                    scenario_run_id,
                    None if balance is None else balance.quality_status,
                )
                result = calculate_forecast(
                    ForecastRequest(
                        agent_id=agent_id,
                        provider_id=provider_id,
                        scope=ForecastScope.PROVIDER_E_MONEY,
                        current_balance=None if balance is None else balance.amount,
                        transactions=transactions,
                        generated_at=as_of,
                        event_context=event_context,
                        data_quality=quality,
                        config=self.config,
                    )
                )
                results.append(
                    replace(result, forecast_id=self.repository.persist(result, self.config))
                )

            cash = self.repository.current_shared_cash(agent_id, scenario_run_id, as_of)
            cash_transactions = self.repository.validated_transactions(
                agent_id,
                None,
                scenario_run_id,
                as_of - timedelta(minutes=self.config.rolling_window_minutes),
                as_of,
            )
            cash_quality = self.repository.data_quality_context(
                agent_id,
                provider_ids,
                scenario_run_id,
            )
            cash_result = calculate_forecast(
                ForecastRequest(
                    agent_id=agent_id,
                    provider_id=None,
                    scope=ForecastScope.SHARED_CASH,
                    current_balance=None if cash is None else cash.amount,
                    transactions=cash_transactions,
                    generated_at=as_of,
                    event_context=event_context,
                    data_quality=cash_quality,
                    config=self.config,
                )
            )
            results.append(
                replace(cash_result, forecast_id=self.repository.persist(cash_result, self.config))
            )
            self.session.flush()
            return tuple(results)
