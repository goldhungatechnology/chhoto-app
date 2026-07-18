---
name: nextjs-conventions
description: Enforce consistent naming conventions and export patterns across all layers of the Next.js project
compatibility: opencode
metadata:
  framework: nextjs
  category: conventions
---

## What I do

I enforce naming conventions, export patterns, and import rules across the entire project. I review code for compliance and fix violations.

## Naming Conventions

| Item      | Convention           | Example             |
|-----------|----------------------|---------------------|
| Folder    | kebab-case           | `quantity-selector` |
| File      | kebab-case           | `login-form.tsx`    |
| Component | PascalCase           | `LoginForm`         |
| Hook      | camelCase with `use` | `useLoginForm`      |
| Type      | PascalCase           | `LoginRequest`      |
| Enum      | PascalCase           | `UserStatus`        |
| Constant  | SCREAMING_SNAKE_CASE | `DEFAULT_PAGE_SIZE` |

## Export Convention

Every folder MUST expose its public API through `index.ts`.

### Correct pattern:

```
logo/
├── index.ts
└── logo.tsx
```

```ts
// index.ts
export { Logo } from "./logo";
```

### Consumer import:

```ts
import { Logo } from "@/shared/components/logo";
```

### Benefits:
- Cleaner imports
- Better encapsulation
- Easier refactoring
- Consistent project structure

## Rules

1. Every directory that contains components/modules MUST have an `index.ts` barrel file
2. Barrel files MUST only re-export — no implementation code
3. Use named exports, NOT default exports (except for Next.js page/layout files in `app/`)
4. Next.js pages in `app/` MUST use default exports
5. Import paths MUST use the `@/` alias — no relative imports that go up multiple levels (`../../`)
6. Module-internal files should NOT be exported from the barrel file — only public API
7. No circular dependencies between modules
8. A module can import from `@/shared/` and `@/core/` but NOT from other modules directly

## File Extensions

- `.tsx` for files with JSX
- `.ts` for files without JSX (hooks, api, lib, types)
- Never use `.js` or `.jsx`

## Validation Checklist

- [ ] Folder name is kebab-case
- [ ] File name is kebab-case
- [ ] Component is PascalCase
- [ ] Hook is camelCase with `use` prefix
- [ ] Type/interface is PascalCase
- [ ] Enum is PascalCase
- [ ] Constant is SCREAMING_SNAKE_CASE
- [ ] Barrel file exists
- [ ] No default exports (except app pages)
- [ ] Named exports used everywhere
- [ ] Import uses `@/` alias
