# Deployment

Deployment is demo-only. Final hosting remains unresolved.

## Required CI/Sonar Secrets
- SONAR_TOKEN
- SONAR_HOST_URL
- SONAR_PROJECT_KEY

## Deployment Principles
- No production provider systems.
- No production customer data.
- Environment files contain placeholders only.
- Health and readiness endpoints are documented API contracts but not implemented yet.

## Demo Readiness
Keep a local fallback demo and recorded screenshots/video as backup. Do not claim production readiness.
