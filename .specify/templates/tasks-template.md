# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with FastAPI dependencies
- [ ] T003 [P] Configure linting and formatting tools (Black, isort, flake8)
- [ ] T004 [P] Setup AI/ML dependencies (scikit-learn, pandas, numpy)
- [ ] T005 [P] Configure database connections (PostgreSQL + Redis)
- [ ] T006 [P] Setup monitoring and logging infrastructure

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### AI 에이전트 시스템 테스트
- [ ] T007 [P] Test market regime detection in tests/unit/test_market_regime_detection.py
- [ ] T008 [P] Test VWAP analysis in tests/unit/test_vwap_analysis.py
- [ ] T009 [P] Test volume profile analysis in tests/unit/test_volume_profile.py
- [ ] T010 [P] Test risk management system in tests/unit/test_risk_management.py
- [ ] T011 [P] Test AI agent communication in tests/integration/test_agent_communication.py

### 거래 시스템 테스트
- [ ] T012 [P] Contract test trading API endpoints in tests/contract/test_trading_api.py
- [ ] T013 [P] Integration test trading flow in tests/integration/test_trading_flow.py
- [ ] T014 [P] Performance test response times in tests/performance/test_response_times.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### AI 에이전트 핵심 구현
- [ ] T015 [P] Market regime detection model in src/ai/market_regime_detector.py
- [ ] T016 [P] VWAP analyzer in src/ai/vwap_analyzer.py
- [ ] T017 [P] Volume profile analyzer in src/ai/volume_profile_analyzer.py
- [ ] T018 [P] Meta-controller agent in src/ai/meta_controller.py
- [ ] T019 [P] Risk management system in src/ai/risk_manager.py
- [ ] T020 [P] Reinforcement learning optimizer in src/ai/rl_optimizer.py

### 거래 시스템 핵심 구현
- [ ] T021 [P] Trading strategy models in src/strategies/
- [ ] T022 [P] Market data processor in src/data/market_processor.py
- [ ] T023 [P] Trading execution engine in src/trading/execution_engine.py
- [ ] T024 [P] Position manager in src/trading/position_manager.py
- [ ] T025 [P] Trading API endpoints in src/api/trading.py

## Phase 3.4: Integration
- [ ] T026 Connect AI agents to database
- [ ] T027 Setup real-time market data streaming
- [ ] T028 Implement agent communication protocol
- [ ] T029 Connect trading engine to exchange APIs
- [ ] T030 Setup monitoring and alerting systems
- [ ] T031 Implement authentication and authorization
- [ ] T032 Setup CORS and security headers

## Phase 3.5: Polish
- [ ] T033 [P] Comprehensive unit test coverage (90%+)
- [ ] T034 Performance tests (<100ms response time)
- [ ] T035 [P] Update API documentation
- [ ] T036 [P] Update AI agent documentation
- [ ] T037 [P] Code optimization and refactoring
- [ ] T038 [P] Security audit and penetration testing
- [ ] T039 [P] Load testing and stress testing
- [ ] T040 [P] Manual testing and validation

## Dependencies
- Tests (T007-T014) before implementation (T015-T025)
- T015 (Market regime detector) blocks T018 (Meta-controller)
- T016 (VWAP analyzer) blocks T021 (Trading strategies)
- T017 (Volume profile analyzer) blocks T021 (Trading strategies)
- T019 (Risk manager) blocks T023 (Trading execution engine)
- T020 (RL optimizer) blocks T021 (Trading strategies)
- Implementation before integration (T015-T025 before T026-T032)
- Integration before polish (T026-T032 before T033-T040)

## Parallel Example
```
# Launch T007-T011 together (AI 에이전트 시스템 테스트):
Task: "Test market regime detection in tests/unit/test_market_regime_detection.py"
Task: "Test VWAP analysis in tests/unit/test_vwap_analysis.py"
Task: "Test volume profile analysis in tests/unit/test_volume_profile.py"
Task: "Test risk management system in tests/unit/test_risk_management.py"
Task: "Test AI agent communication in tests/integration/test_agent_communication.py"

# Launch T015-T020 together (AI 에이전트 핵심 구현):
Task: "Market regime detection model in src/ai/market_regime_detector.py"
Task: "VWAP analyzer in src/ai/vwap_analyzer.py"
Task: "Volume profile analyzer in src/ai/volume_profile_analyzer.py"
Task: "Risk management system in src/ai/risk_manager.py"
Task: "Reinforcement learning optimizer in src/ai/rl_optimizer.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task