# Task Board

| Phase | Task | Requirement IDs | Status |
|---|---|---|---|
| 0 | Review and merge governance commit | DOC-001,QUALITY-001 | Done |
| 1 | Scaffold repository foundation | ARCH-001,ARCH-002,API-001,DB-001 | Done |
| 1 | Add backend/frontend tooling | QUALITY-001,QUALITY-002,CI-001,CI-002 | Done |
| 2 | Add SQLAlchemy models and Alembic migrations | DB-001,FR-001,FR-002,FR-008,NFR-002,NFR-003,NFR-004,DATA-001,DATA-002,DATA-003 | Done |
| 3 | Add deterministic synthetic scenarios | DATA-001,DATA-002,DATA-003,FR-002,FR-009,FR-012,NFR-003,NFR-004,SEC-001,SAFE-001,SAFE-002,SAFE-003,DEMO-002 | Done |
| 4 | Add provider ingestion and validation | FR-001,FR-002,NFR-003,NFR-004,DATA-001,DATA-002,DATA-003,DB-001,SEC-001,SAFE-001,SAFE-002,SAFE-003 | Done |
| 5 | Add liquidity runway engine | FR-004,NFR-003,NFR-004,MET-001,MET-002 | Done; unit, controlled synthetic metrics, and Neon PostgreSQL persistence verified |
| 6 | Add primary anomaly engine | FR-005,FR-006,MET-003,MET-004,MET-005 | Done; unit metrics and Neon persistence verified |
| 7 | Add confidence fusion | NFR-003,SAFE-002,SAFE-003 | Done; deterministic weakest-signal fusion and advisory recommendations verified |
| 8 | Add explanation provider and fallback | FR-010,FR-011 | Not Started |
| 9 | Add alerts and cases | FR-007,FR-008,NFR-002,SAFE-003 | Done; advisory lifecycle, evidence, confidence, and audit persistence verified |
| 10 | Add RBAC/provider-scope auth and AuthContext middleware contract | NFR-004 | Provider/area scope checks done; identity authentication remains |
| 11 | Add `/api/v1` endpoints using AuthContext | API-001,NFR-004 | Requested alert and case routes done; OpenAPI and validation tested |
| 12 | Build agent UI | FR-001,FR-003,FR-004 | Done with contract-aligned demo fixtures; API integration pending |
| 13 | Build operations UI | FR-007,FR-008 | Done with local lifecycle preview; API integration pending |
| 14 | Build risk UI | FR-006,SAFE-002 | Done with evidence, uncertainty, and safe language previews |
| 15 | Add metrics and observability | MET-001, MET-002, MET-003, MET-004, MET-005, MET-006, MET-007, MET-008, MET-009, MET-010, MET-011, MET-012 | Frontend evidence surface done; backend metrics pending |
| 16 | Add failure-mode tests | FAIL-001, FAIL-002, FAIL-003, FAIL-004, FAIL-005, FAIL-006, FAIL-007 | Frontend missing-feed, offline-health, safe-language, and lifecycle interactions verified; backend pending |
| 17 | Package demo | DEMO-001,DEMO-002 | Not Started |
| 18 | Release prep | QUALITY-002 | Not Started |
