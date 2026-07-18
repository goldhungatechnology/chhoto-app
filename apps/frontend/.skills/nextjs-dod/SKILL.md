---
name: nextjs-dod
description: Verify that frontend features are complete against the Definition of Done checklist
compatibility: opencode
metadata:
  framework: nextjs
  category: quality
---

## What I do

I verify features against the Definition of Done checklist. I check every item and report what's missing or incomplete.

## Definition of Done

A frontend feature is complete only when ALL of these are satisfied:

### Implementation
- [ ] Route implemented (page/route handler exists in `app/`)
- [ ] Types defined (request/response types, prop interfaces)
- [ ] API integration completed (requests wired up)
- [ ] Loading state handled (skeleton, spinner, or Suspense boundary)
- [ ] Error state handled (error boundary, error UI, fallback)
- [ ] Empty state handled (meaningful empty state for zero-data scenarios)

### Quality
- [ ] Responsive design verified (mobile, tablet, desktop breakpoints)
- [ ] Accessibility verified (keyboard nav, ARIA labels, screen reader support)
- [ ] Unit tests written (at minimum for hooks and utils, ideally for components)
- [ ] Code reviewed (self-review before submitting)

### Cleanliness
- [ ] No unused code remains (dead exports, unused imports, commented code)
- [ ] All imports follow project conventions (`@/` alias, barrel imports)
- [ ] Public exports exposed through `index.ts`
- [ ] No TODO/FIXME without a tracking ticket reference

## When to use me

Use this skill when:
- Completing a feature implementation
- Before opening a pull request
- After refactoring existing code
- During code review

## How to verify

For each item, I will:
1. Check the file system and code for the specific requirement
2. Report PASS/FAIL clearly
3. For FAIL items, explain exactly what needs to be fixed
4. Provide the exact file path and line where the issue exists
