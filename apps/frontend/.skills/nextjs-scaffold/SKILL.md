---
name: nextjs-scaffold
description: Scaffold Next.js projects following the standard architecture with App Router, feature-based modules, and shared layer
compatibility: opencode
metadata:
  framework: nextjs
  category: scaffolding
---

## What I do

I scaffold Next.js project structures following the architecture standard. I create the complete folder hierarchy with correct conventions.

## Package Manager

This project uses **pnpm**. All commands must use `pnpm`, never `npm` or `npx`. Use `pnpm dlx shadcn@latest` (not `npx shadcn`) to add shadcn components.

## Folder Structure

Create this exact structure:

```
src
├── app
│   ├── (public)
│   ├── (auth)
│   ├── dashboard
│   ├── api
│   ├── layout.tsx
│   └── page.tsx
├── modules
├── shared
│   ├── components
│   ├── hooks
│   ├── lib
│   ├── providers
│   └── types
├── core
│   └── config
│       ├── api.ts
│       ├── assets.ts
│       └── constants.ts
├── middleware.ts
└── tests
```

## Rules

- All folders use kebab-case
- Route groups use parentheses: `(public)`, `(auth)`
- `app/layout.tsx` and `app/page.tsx` are the root layout and entry
- `middleware.ts` lives at `src/middleware.ts`
- `tests` directory mirrors `src` structure for unit/integration tests
- Do NOT create files inside route group folders directly — they are just grouping boundaries
- Do NOT put business logic in `app/` — only route definitions and layout composition

## App Layer Responsibilities

The `app/` layer is ONLY for:
- Route registration
- Layout composition
- Metadata definition (`generateMetadata` or `metadata` export)
- Route grouping `(group)`
- Route protection via middleware

The `app/` layer must NOT contain:
- Business logic
- API requests
- Data transformation
- Complex state management

Example `app/login/page.tsx`:
```tsx
import { LoginView } from "@/modules/auth/views";

export default function Page() {
  return <LoginView />;
}
```

## Core Layer Responsibilities

The `core/` layer holds application-wide configuration and infrastructure:
- `config/api.ts`: Base URL, HTTP client setup, interceptors, default headers
- `config/assets.ts`: Static image paths, global icons, CDN references
- `config/constants.ts`: App name, pagination defaults, feature flags, global enums

Import example:
```ts
import { API_BASE_URL } from "@/core/config/api";
import { DEFAULT_PAGE_SIZE } from "@/core/config/constants";
```

## Import Paths

Use `@/` alias for all imports:
- `@/modules/<name>/...`
- `@/shared/components/...`
- `@/shared/hooks/...`
- `@/shared/lib/...`
- `@/shared/types/...`
- `@/core/config/...`
