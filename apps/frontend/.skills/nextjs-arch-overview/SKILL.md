---
name: nextjs-arch-overview
description: Comprehensive reference for the Next.js architecture including all layers, rules, and conventions
compatibility: opencode
metadata:
  framework: nextjs
  category: reference
  scope: comprehensive
---

## What I do

I provide the complete architecture reference. When you need to understand the full system — layers, their responsibilities, and how they interact — load this skill.

## Package Manager

This project uses **pnpm**. Never use `npm` or `npx`. Use `pnpm dlx shadcn@latest` to add shadcn UI components to `src/shared/components/ui/`.

## Architecture Principles

- Feature-Based Modular Design
- Clean Separation of Concerns
- Scalable Folder Structure
- App Router (Next.js)
- Consistent Naming Conventions
- Reusable Shared Components
- Predictable Import Paths

## Four Layers

### 1. App Layer (`src/app/`)
Route definitions and layout composition ONLY.
- Route registration
- Layout composition
- Metadata definition
- Route grouping
- Route protection
- Must NOT contain: business logic, API requests, data transformation, complex state

### 2. Modules Layer (`src/modules/`)
Every business domain owns its implementation.
Self-contained and independently maintainable.
Each module has: views/, components/, hooks/, api/, types.ts, index.ts

### 3. Shared Layer (`src/shared/`)
Reusable code shared across modules.
Contains: components/, hooks/, lib/, providers/, types/

### 4. Core Layer (`src/core/`)
Application-wide configuration and infrastructure.
- Environment configuration
- API client setup (base URL, interceptors, default headers)
- Global constants (app name, pagination defaults, feature flags)
- Static asset management (image paths, icons, CDN references)

Contains: config/api.ts, config/constants.ts, config/assets.ts
Modules import from `@/core/config/...` — NOT from `@/shared/`.

## Module Internal Structure

```
modules/<name>/
├── views/         # Screens (thin, delegate to hooks)
├── components/
│   ├── primitives # Small UI pieces (Badge, Avatar, Label)
│   ├── blocks/    # Business components (Card, Table, Form)
│   └── sections/  # Feature compositions (Dashboard, Filters)
├── hooks/         # Business logic, data fetching, state (UI-agnostic)
├── api/           # HTTP requests only (no React code)
├── types.ts       # Module types
└── index.ts       # Public API barrel
```

## Component Dependency Rules

Strict one-directional dependency chain:

```
Views → Sections → Blocks → Primitives
```

| Layer      | May import                    | Must NOT import                  |
|------------|-------------------------------|----------------------------------|
| Primitives | —                             | Blocks, Sections, Views          |
| Blocks     | Primitives only               | Sections, Views                  |
| Sections   | Blocks (primitives if needed) | Views                            |
| Views      | Sections only                 | Blocks, Primitives               |

Forbidden: skipping layers, reverse dependencies, cross-layer coupling.

## Shared Layer Structure

```
shared/
├── components/    # Each in own folder with index.ts
├── hooks/         # Domain-independent (useDebounce, usePagination)
├── lib/           # Pure utilities (http-client, currency, date, cn)
├── providers/     # React context providers
└── types/         # Shared types
```

## Conventions Summary

- Folders: kebab-case
- Files: kebab-case
- Components: PascalCase
- Hooks: camelCase with `use` prefix
- Types/Enums: PascalCase
- Constants: SCREAMING_SNAKE_CASE
- Every folder has `index.ts` barrel
- Named exports everywhere (except app pages use default)
- `@/` alias imports — no deep relative imports
- Modules import from `@/shared/` and `@/core/` and own internals only

## Definition of Done

Every feature must have:
- Route, types, API integration
- Loading, error, empty states
- Responsive and accessible design
- Unit tests
- No dead code or TODO without ticket
- Proper exports through index.ts
