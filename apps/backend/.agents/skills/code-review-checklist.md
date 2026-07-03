# Skill: Code Review Checklist

This document details the code review checklist for backend modifications.

## Architectural Review
- [ ] No layer separation rules are violated (e.g. `domain` layer has no dependencies on databases or web frameworks).
- [ ] Cross-module imports are restricted to event definitions or generic kernel interfaces.
- [ ] Use cases are injected using dependency-injector containers.

## Testing Coverage
- [ ] Unit tests cover business rule variations.
- [ ] Endpoint changes have integration tests verifying happy and error response payloads.
- [ ] Databases rollback successfully after each test execution.

## Code Quality and Style
- [ ] Code is formatted and linted with Ruff (`make lint` and `make format` pass).
- [ ] All inputs, outputs, class fields, and utility parameters are explicitly type annotated.
- [ ] No print statements remain; all logging is conducted via the central `logger`.
