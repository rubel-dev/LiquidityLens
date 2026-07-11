# Project Context

## Problem Summary
Multi-provider mobile financial service agents serve customers through separate providers while using one shared physical cash pool. The agent may appear healthy in total value while one provider e-money balance or the shared cash reserve is near shortage.

## Business Objective
Build a safe hackathon prototype that helps agents and provider teams understand liquidity pressure, unusual activity requiring review, data quality uncertainty, and operational ownership before service disruption.

## Canonical Principles
- Provider-specific e-money balances remain separate.
- Shared physical cash is a separate concept and is not attributed to any provider feed.
- No wallet merge, no real money transfer, no blocking, no freezing.
- No final risk determination or accusatory language.
- Human review is required for unusual activity.
- Missing, delayed, stale, or conflicting data reduces confidence.

## Adopted Judge-Facing Ideas
- Deceptive-total visualization.
- Provider-specific runway clock.
- Evidence fingerprint.
- Graceful degradation.
- Normal Eid/salary-day false-positive scenario.
- Story-driven demo.
- Demo reset and replay.
- Strong metrics.
- Detailed implementation task board.

## Deferred Optional Scope
Redis, Upstash, Kafka, microservices, separate provider deployments, mandatory WebSockets, network graph, Gantt timeline, sound alerts, complex model-learning feedback loops, more than one primary anomaly pattern, excessive cloud dependencies, and production-scale claims are deferred.
