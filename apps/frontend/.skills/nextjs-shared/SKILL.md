---
name: nextjs-shared
description: Create and manage shared components, hooks, lib utilities, providers, and types used across modules
compatibility: opencode
metadata:
  framework: nextjs
  category: shared
---

## What I do

I create and manage code in the shared layer — reusable, domain-independent code used across multiple modules.

> **Boundary**: The `shared/` layer holds reusable UI components, hooks, utilities, providers, and types. App-wide configuration (API base URL, constants, asset paths) belongs in `@/core/config/` instead.

## Shared Layer Structure

```
shared
├── components/     # Reusable UI components (form, logo, snackbar, etc.)
├── hooks/          # Domain-independent hooks
├── lib/            # Pure utility functions
├── providers/      # React context providers
└── types/          # Shared TypeScript types
```

## Shared Components (`components/`)

Each component is a folder with an `index.ts` barrel file:

```
shared/components/
├── form/
│   ├── index.ts
│   ├── input.tsx
│   ├── textarea.tsx
│   └── select.tsx
├── logo/
│   ├── index.ts
│   └── logo.tsx
└── snackbar/
    ├── index.ts
    └── snackbar.tsx
```

Rules:
- Every component folder MUST expose a public API through `index.ts`
- Folder name MUST match the primary component name (kebab-case)
- Consumers MUST import from the folder root: `import { Logo } from "@/shared/components/logo"`
- Do NOT import from nested paths like `@/shared/components/logo/logo`

## Shared Hooks (`hooks/`)

Domain-independent hooks only:
- `use-debounce.ts`
- `use-pagination.ts`
- `use-disclosure.ts`

Shared hooks must NOT contain business logic specific to any module.

## Shared Lib (`lib/`)

Pure utility functions and framework-independent helpers:
- `http-client.ts` — HTTP client configuration
- `asset.ts` — asset helpers
- `currency.ts` — currency formatting
- `date.ts` — date formatting/manipulation
- `time.ts` — time formatting/manipulation
- `cn.ts` — class name utility (clsx + tailwind-merge)

Lib files must:
- Be pure functions with no side effects
- Have no React dependencies
- Be fully testable
- Use kebab-case file naming

## Providers (`providers/`)

React context providers for cross-cutting concerns:
- Theme providers
- Authentication providers
- Toast/notification providers
- Query client providers

## Types (`types/`)

Shared TypeScript types, interfaces, and enums used across modules.
Use PascalCase naming.
