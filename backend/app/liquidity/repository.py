import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.liquidity.exceptions import ForecastSubjectNotFoundError
from app.liquidity.schemas import (
    RULE_NAME,
    RULE_VERSION,
    DataQualityContext,
    DemandTransaction,
    EventContext,
    ForecastConfig,
    ForecastResult,
)
from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.analytics import (
    ConfidenceAssessment,
    EvidenceItem,
    LiquidityForecast,
    RuleVersion,
)
from app.persistence.models.audit import AuditEvent
from app.persistence.models.balance import ProviderBalanceSnapshot, SharedCashSnapshot
from app.persistence.models.enums import FeedQualityStatus, TransactionStatus
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.scenario import Scenario, ScenarioRun
from app.persistence.models.transaction import Transaction


class LiquidityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._active_rule: RuleVersion | None = None

    def require_agent(self, agent_id: uuid.UUID) -> Agent:
        agent = self.session.get(Agent, agent_id)
        if agent is None:
            raise ForecastSubjectNotFoundError(f"agent not found: {agent_id}")
        return agent

    def require_run(self, scenario_run_id: uuid.UUID | None) -> ScenarioRun | None:
        if scenario_run_id is None:
            return None
        run = self.session.get(ScenarioRun, scenario_run_id)
        if run is None:
            raise ForecastSubjectNotFoundError(f"scenario run not found: {scenario_run_id}")
        return run

    def provider_ids_for_agent(self, agent_id: uuid.UUID) -> tuple[uuid.UUID, ...]:
        return tuple(
            self.session.scalars(
                select(AgentProviderAccount.provider_id)
                .where(AgentProviderAccount.agent_id == agent_id)
                .order_by(AgentProviderAccount.provider_id)
            ).all()
        )

    def current_provider_balance(
        self,
        agent_id: uuid.UUID,
        provider_id: uuid.UUID,
        scenario_run_id: uuid.UUID | None,
        as_of: datetime,
    ) -> ProviderBalanceSnapshot | None:
        query = select(ProviderBalanceSnapshot).where(
            ProviderBalanceSnapshot.agent_id == agent_id,
            ProviderBalanceSnapshot.provider_id == provider_id,
            ProviderBalanceSnapshot.observed_at <= as_of,
        )
        if scenario_run_id is not None:
            query = query.where(ProviderBalanceSnapshot.scenario_run_id == scenario_run_id)
        return self.session.scalar(query.order_by(ProviderBalanceSnapshot.observed_at.desc()))

    def current_shared_cash(
        self,
        agent_id: uuid.UUID,
        scenario_run_id: uuid.UUID | None,
        as_of: datetime,
    ) -> SharedCashSnapshot | None:
        query = select(SharedCashSnapshot).where(
            SharedCashSnapshot.agent_id == agent_id,
            SharedCashSnapshot.observed_at <= as_of,
        )
        if scenario_run_id is not None:
            query = query.where(SharedCashSnapshot.scenario_run_id == scenario_run_id)
        return self.session.scalar(query.order_by(SharedCashSnapshot.observed_at.desc()))

    def validated_transactions(
        self,
        agent_id: uuid.UUID,
        provider_id: uuid.UUID | None,
        scenario_run_id: uuid.UUID | None,
        start: datetime,
        end: datetime,
    ) -> tuple[DemandTransaction, ...]:
        query = select(Transaction).where(
            Transaction.agent_id == agent_id,
            Transaction.status == TransactionStatus.COMPLETED,
            Transaction.occurred_at >= start,
            Transaction.occurred_at <= end,
        )
        if provider_id is not None:
            query = query.where(Transaction.provider_id == provider_id)
        if scenario_run_id is not None:
            query = query.where(Transaction.scenario_run_id == scenario_run_id)
        rows = self.session.scalars(query.order_by(Transaction.occurred_at)).all()
        return tuple(
            DemandTransaction(
                provider_id=row.provider_id,
                transaction_type=row.transaction_type,
                amount=Decimal(row.amount),
                occurred_at=row.occurred_at,
            )
            for row in rows
        )

    def data_quality_context(
        self,
        agent_id: uuid.UUID,
        provider_ids: tuple[uuid.UUID, ...],
        scenario_run_id: uuid.UUID | None,
        balance_quality: str | None = None,
    ) -> DataQualityContext:
        latest: list[FeedQualityStatus] = []
        for provider_id in provider_ids:
            query = select(ProviderFeedStatus).where(
                ProviderFeedStatus.provider_id == provider_id,
                ProviderFeedStatus.agent_id == agent_id,
            )
            if scenario_run_id is not None:
                query = query.where(ProviderFeedStatus.scenario_run_id == scenario_run_id)
            row = self.session.scalar(query.order_by(ProviderFeedStatus.observed_at.desc()))
            latest.append(FeedQualityStatus.MISSING if row is None else row.status)

        issues: list[str] = []
        multiplier = Decimal("1.00")
        complete = True
        penalties = {
            FeedQualityStatus.DELAYED: Decimal("0.80"),
            FeedQualityStatus.STALE: Decimal("0.80"),
            FeedQualityStatus.MISSING: Decimal("0.60"),
            FeedQualityStatus.CONFLICTING: Decimal("0.70"),
            FeedQualityStatus.INVALID: Decimal("0.50"),
        }
        for status in latest:
            if status in penalties:
                multiplier = min(multiplier, penalties[status])
                issues.append(f"{status.value} provider feed")
            if status in {
                FeedQualityStatus.MISSING,
                FeedQualityStatus.CONFLICTING,
                FeedQualityStatus.INVALID,
            }:
                complete = False
        if balance_quality in {"missing", "conflicting", "invalid"}:
            complete = False
            multiplier = min(multiplier, Decimal("0.60"))
            issues.append(f"{balance_quality} balance snapshot")
        elif balance_quality == "warning":
            multiplier = min(multiplier, Decimal("0.85"))
            issues.append("balance snapshot accepted with warning")
        return DataQualityContext(
            multiplier=multiplier,
            complete=complete,
            statuses=tuple(latest),
            issues=tuple(dict.fromkeys(issues)),
        )

    def event_context(self, run: ScenarioRun | None) -> EventContext:
        if run is None:
            return EventContext.STANDARD
        scenario = self.session.get(Scenario, run.scenario_id)
        if scenario is None:
            return EventContext.STANDARD
        if scenario.code == "eid_rush":
            return EventContext.EID
        if scenario.code == "salary_day_legitimate_spike":
            return EventContext.SALARY_DAY
        return EventContext.STANDARD

    def persist(self, result: ForecastResult, config: ForecastConfig) -> uuid.UUID:
        rule = self._rule_version(config)
        forecast_id = uuid.uuid4()
        forecast = LiquidityForecast(
            id=forecast_id,
            agent_id=result.agent_id,
            provider_id=result.provider_id,
            forecast_type=result.scope.value,
            forecast_time=result.generated_at,
            shortage_at=result.estimated_shortage_at,
            confidence=result.confidence,
        )
        self.session.add(forecast)
        self.session.flush([forecast])

        self.session.add(
            ConfidenceAssessment(
                subject_type="liquidity_forecast",
                subject_id=forecast.id,
                confidence=result.confidence,
                reasons={
                    "tier": result.confidence_tier,
                    "data_quality_impact": result.data_quality_impact,
                    "limitations": list(result.limitations),
                    "rule_version_id": str(rule.id),
                },
            )
        )
        summary = {
            "scope": result.scope.value,
            "current_balance": _decimal_or_none(result.current_balance),
            "expected_demand_rate_per_minute": _decimal_or_none(
                result.expected_demand_rate_per_minute
            ),
            "runway_minutes": _decimal_or_none(result.runway_minutes),
            "estimated_shortage_at": (
                None
                if result.estimated_shortage_at is None
                else result.estimated_shortage_at.isoformat()
            ),
            "risk_level": result.risk_level.value,
            "calculation_start": result.calculation_start.isoformat(),
            "calculation_end": result.calculation_end.isoformat(),
            "generated_at": result.generated_at.isoformat(),
            "rule_name": RULE_NAME,
            "rule_version": RULE_VERSION,
        }
        self.session.add(
            EvidenceItem(
                forecast_id=forecast.id,
                evidence_type="forecast_summary",
                payload=summary,
            )
        )
        for item in result.evidence:
            self.session.add(
                EvidenceItem(
                    forecast_id=forecast.id,
                    evidence_type=item.evidence_type,
                    payload={"label": item.label, "value": item.value, "detail": item.detail},
                )
            )
        self.session.add(
            AuditEvent(
                provider_id=result.provider_id,
                action="liquidity.forecast_created",
                entity_type="liquidity_forecast",
                entity_id=forecast.id,
                correlation_id=str(forecast.id),
                metadata_json={
                    "scope": result.scope.value,
                    "risk_level": result.risk_level.value,
                    "confidence": str(result.confidence),
                    "advisory_only": True,
                    "financial_action_executed": False,
                },
                new_state_summary=summary,
            )
        )
        return forecast_id

    def _rule_version(self, config: ForecastConfig) -> RuleVersion:
        if self._active_rule is not None:
            return self._active_rule
        rule = self.session.scalar(
            select(RuleVersion).where(
                RuleVersion.name == RULE_NAME,
                RuleVersion.version == RULE_VERSION,
            )
        )
        if rule is not None:
            self._active_rule = rule
            return rule
        rule = RuleVersion(
            id=uuid.uuid4(),
            name=RULE_NAME,
            version=RULE_VERSION,
            config={
                "rolling_window_minutes": config.rolling_window_minutes,
                "forecast_horizon_minutes": config.forecast_horizon_minutes,
                "minimum_transactions": config.minimum_transactions,
                "target_transactions": config.target_transactions,
                "volatility_adjustment": str(config.volatility_adjustment),
                "minimum_confidence": str(config.minimum_confidence),
                "accounting": {
                    "provider_e_money_consumption": "cash_in minus cash_out",
                    "shared_cash_outflow": "cash_out minus cash_in",
                },
            },
            active=True,
        )
        self.session.add(rule)
        self._active_rule = rule
        return rule


def _decimal_or_none(value: Decimal | None) -> str | None:
    return None if value is None else str(value)
