# Security and Safety

## Guardrails
- Synthetic data only.
- No real credentials, PINs, OTPs, passwords, private keys, or customer identities.
- No real provider integration.
- No money movement, wallet merge, blocking, freezing, recovery, reversal, refill, or settlement.
- No final risk determination.
- Human review required for unusual activity.

## Localization Policy
Bengali, Banglish, and English explanations must include situation, evidence, confidence/uncertainty, and safe next step. Recommendations must be advisory: "Coordinate approved liquidity support through the responsible provider operations channel."

## Forbidden Language
- Do not use cleared-case wording that sounds like a final risk judgment.
- Use: "The pattern is consistent with expected demand; no additional review is currently recommended."
- Do not instruct a user to arrange a fixed amount as a command.

## Role and Provider Scope
Agent, operations, field officer, risk reviewer, manager, and demo operator roles are scoped. Provider-specific data must be filtered at API, service, repository, and UI layers.

## Demo Auth Specification
The MVP uses a demo-only role-selection login, not production authentication.

1. User selects a demo role from the UI: agent, operations, field officer, risk reviewer, manager, or demo operator.
2. Backend issues a short-lived JWT-like demo token with claims: `sub`, `role`, `provider_ids`, `area_ids`, `expires_at`.
3. API middleware resolves an `AuthContext` from the token before every scoped request.
4. Provider-scoped endpoints must receive `AuthContext`; requests outside the claim scope return 403.
5. Demo tokens must not contain real credentials and must not be accepted outside local/demo environments.

```typescript
interface AuthContext {
  user_id: string;
  role: "agent" | "operations" | "field_officer" | "risk_reviewer" | "manager" | "demo_operator";
  provider_ids: string[];
  area_ids: string[];
  is_demo: true;
}
```

## Deterministic Template Registry
Templates must use safe advisory language and must not declare wrongdoing. Required placeholders include `{provider_display_name}`, `{agent_label}`, `{runway_minutes}`, `{confidence_percent}`, `{uncertainty}`, `{velocity_count}`, `{window_minutes}`, `{group_size}`, and `{safe_next_step}`.

| Template ID | Language | Use | Template |
|---|---|---|---|
| TPL-LIQ-BN | Bengali | Liquidity shortage | `{provider_display_name} provider-er jonno {agent_label} outlet-e liquidity pressure dekha jacche. Estimated runway {runway_minutes} minutes. Confidence {confidence_percent}%. Uncertainty: {uncertainty}. Poroborti podokkhep: {safe_next_step}` |
| TPL-LIQ-BANGLISH | Banglish | Liquidity shortage | `{provider_display_name} provider er jonno {agent_label} outlet e liquidity pressure dekha jacche. Estimated runway {runway_minutes} minutes. Confidence {confidence_percent}%. Uncertainty: {uncertainty}. Next step: {safe_next_step}` |
| TPL-LIQ-EN | English | Liquidity shortage | `{provider_display_name} liquidity pressure is visible for {agent_label}. Estimated runway is {runway_minutes} minutes. Confidence {confidence_percent}%. Uncertainty: {uncertainty}. Next step: {safe_next_step}` |
| TPL-ANOM-BN | Bengali | Unusual activity | `{provider_display_name} provider-e {window_minutes} minute window-te {velocity_count} repeated or near-identical cash-out pattern dekha geche from {group_size} synthetic references. Confidence {confidence_percent}%. Ei pattern review proyojon; eti wrongdoing-er proof noy. Poroborti podokkhep: {safe_next_step}` |
| TPL-ANOM-BANGLISH | Banglish | Unusual activity | `{provider_display_name} provider e {window_minutes} minute window te {velocity_count} repeated or near-identical cash-out pattern dekha geche from {group_size} synthetic refs. Confidence {confidence_percent}%. Pattern ta review dorkar; eta wrongdoing proof na. Next step: {safe_next_step}` |
| TPL-ANOM-EN | English | Unusual activity | `{provider_display_name} shows {velocity_count} repeated or near-identical cash-out events in a {window_minutes} minute window from {group_size} synthetic references. Confidence {confidence_percent}%. This requires review and is not proof of wrongdoing. Next step: {safe_next_step}` |
| TPL-DQ-BN | Bengali | Data quality degraded | `{provider_display_name} data quality degraded: {uncertainty}. Confidence {confidence_percent}%. Confident forecast dewa jacche na. Poroborti podokkhep: provider operations channel-er maddhome data refresh coordinate korun.` |
| TPL-DQ-BANGLISH | Banglish | Data quality degraded | `{provider_display_name} data quality degraded: {uncertainty}. Confidence {confidence_percent}%. Confident forecast dewa jacche na. Next step: coordinate data refresh through provider operations channel.` |
| TPL-DQ-EN | English | Data quality degraded | `{provider_display_name} data quality is degraded: {uncertainty}. Confidence {confidence_percent}%. No confident forecast should be shown. Next step: coordinate a data refresh through the provider operations channel.` |
