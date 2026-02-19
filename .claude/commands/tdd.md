---
description: "Enforce test-driven development: write tests FIRST, then implement minimal code to pass"
---

# /tdd - Test-Driven Development

Enforce TDD methodology: scaffold interfaces, generate tests FIRST, then implement minimal code to pass. Target 80%+ coverage.

## TDD Cycle

```
RED -> GREEN -> REFACTOR -> REPEAT

RED:      Write a failing test
GREEN:    Write minimal code to pass
REFACTOR: Improve code, keep tests passing
REPEAT:   Next feature/scenario
```

## Workflow

1. **Define Interfaces** - Types and function signatures first
2. **Write Failing Tests (RED)** - Tests that will fail because code does not exist
3. **Run Tests** - Verify they fail for the right reason
4. **Implement Minimal Code (GREEN)** - Just enough to make tests pass
5. **Run Tests** - Verify they pass
6. **Refactor** - Improve code while keeping tests green
7. **Check Coverage** - Add more tests if below 80%

## DO

- Write the test FIRST, before any implementation
- Run tests and verify they FAIL before implementing
- Write minimal code to make tests pass
- Refactor only after tests are green
- Add edge cases and error scenarios
- Aim for 80%+ coverage (100% for critical code)

## DO NOT

- Write implementation before tests
- Skip running tests after each change
- Write too much code at once
- Ignore failing tests
- Test implementation details (test behavior)
- Mock everything (prefer integration tests)

## Test Types

- **Unit**: happy path, edge cases, error conditions, boundary values
- **Integration**: API endpoints, database operations, external services
- **E2E**: critical user flows, multi-step processes

## Coverage Requirements

- 80% minimum for all code
- 100% required for: financial calculations, auth logic, security code, core business logic

## Integration

- Use `/plan` first to understand what to build
- Use `/code-review` to review implementation
- Use `/commit` to commit when done
