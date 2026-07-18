---
name: nextjs-module
description: Create and maintain feature-based modules with views, components, hooks, api, and types following the standard architecture
compatibility: opencode
metadata:
  framework: nextjs
  category: module
---

## What I do

I create and manage feature-based modules following the architecture standard. Each module is self-contained and independently maintainable.

## Module Structure

Every module must follow this structure:

```
modules/<module-name>
├── views/          # Route-level screens
├── components/
│   ├── primitives/ # Small reusable UI pieces
│   ├── blocks/     # Reusable business components
│   └── sections/   # Large feature compositions
├── hooks/          # Business logic and state orchestration
├── api/            # API requests
├── types.ts        # Module-specific types
└── index.ts        # Public exports
```

## Views (`views/`)

Views represent complete screens. They are thin — they compose UI and delegate logic to hooks.

Example:
```
views/
├── login-view.tsx
├── register-view.tsx
└── forgot-password-view.tsx
```

Responsibilities:
- Screen composition
- View orchestration
- Connect hooks to UI

## Components (`components/`)

Components follow a strict one-directional dependency chain:

```
Views → Sections → Blocks → Primitives
```

### Primitives
Small reusable UI pieces (Badge, Avatar, Label, Indicator, Price Display).
File naming: kebab-case (e.g., `status-badge.tsx`)
- Must NOT import: Blocks, Sections, Views

### Blocks
Reusable business components (Card, Table, Form, List Item).
File naming: kebab-case (e.g., `rental-card.tsx`)
- May import: Primitives only
- Must NOT import: Sections, Views

### Sections
Large feature compositions (Dashboard Sections, Filters, Analytics Panels).
File naming: kebab-case (e.g., `customer-rentals-section.tsx`)
- May import: Blocks (primitives only if absolutely necessary)
- Must NOT import: Views

### Views
- May import: Sections only
- Must NOT import: Blocks, Primitives

### Forbidden patterns
- Skipping layers (e.g. Primitives → Sections, Primitives → Views, Blocks → Views)
- Reverse dependency (any lower layer importing a higher layer)
- Cross-layer coupling (any non-adjacent layer import)

## Component Minimization & Design Guidelines

To maintain clean and highly readable code, components must be kept as small and modular as possible:

1. **Minimize Component Size**: Break down complex components (like forms, multi-state cards, list items) into smaller sub-components. If a component exceeds ~150-200 lines, extract its sections.
   - For example, split a form card into a container, a fields component (`*-form-fields.tsx`), and a success state component (`*-success.tsx`).
   - Smaller helper components can reside in the same file if they are simple, or in separate files within the same directory for cleaner structure.
2. **Standardized Forms**:
   - Never use raw `<input>` or raw `<Input>` directly for form fields.
   - Use the custom form wrapper components from `@/shared/components/custom/form`, e.g., `Field.Input` or `Field.PasswordInput`.
   - These enhanced inputs support properties like `startAddon`, `endAddon`, `labelClassName`, and custom styling to handle prefix/suffix elements without raw HTML tags.
   - Wrap forms using React Hook Form's `<FormProvider>` to supply form context to child components (e.g. `<LoginFormFields />` or `<CreateLinkFormFields />`).
3. **UI and Logic Separation**:
   - Keep presentational components thin by delegating all logic, form handling, validation schemas, and API queries/mutations to custom hooks (e.g., `useLoginForm` or `useCreateLinkForm`).
   - UI components should only compose sub-components and pass data/handlers.

## Hooks (`hooks/`)

Business-specific hooks containing:
- Data fetching (React Query)
- Form state management
- Business workflows
- State orchestration

Hooks must be UI-agnostic — no JSX, no UI state, no UI imports.

File naming: camelCase with `use` prefix (e.g., `use-login-form.ts`)

## API (`api/`)

Contains HTTP requests only:
- Request payload mapping
- Response mapping
- API integration

Must NOT contain:
- React code (no hooks, no JSX)
- UI state
- Business logic

File naming: kebab-case (e.g., `login.ts`)

## Types (`types.ts`)

Module-specific TypeScript types and interfaces.
Naming: PascalCase (e.g., `LoginRequest`, `UserStatus`)

## Index (`index.ts`)

Barrel file that re-exports the module's public API:
```ts
export { LoginView } from "./views/login-view";
export { useLoginForm } from "./hooks/use-login-form";
export type { LoginRequest } from "./types";
```

## Enforcement

- Every module folder name must be kebab-case
- Every module must have all 6 subdirectories/files (views/, components/, hooks/, api/, types.ts, index.ts)
- No cross-module imports of non-public API
- Modules can only import from `@/shared/`, `@/core/`, or from their own internal files
