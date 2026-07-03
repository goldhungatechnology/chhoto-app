# Skill: Testing Guidelines

This document details testing strategies and rules.

## Test Structures
- **Unit Tests**: Test single class, utility, or domain model in isolation. Mock database/network interactions.
- **Integration Tests**: Verify end-to-end endpoint logic, utilizing the `async_client` fixture to hit routes and verifying DB results directly.

## Rules for Writing Tests
- All test files must be inside the `tests/` directory and begin with `test_`.
- Make sure to use the function-scoped `db_session` or `async_client` fixtures to automatically execute tests within transactional rollbacks. This ensures test isolation.
- Use `@pytest.mark.asyncio` for all asynchronous test functions.
- Run tests locally using `make test`.
