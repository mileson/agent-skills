---
name: tailwind-v4-shadcn
description: |
 Set up Tailwind v4 with shadcn/ui using @theme inline pattern and CSS variable architecture. Four-step pattern: CSS variables, Tailwind mapping, base styles, automatic dark mode. Prevents 8 documented errors.

 Use when initializing React projects with Tailwind v4, or fixing colors not working, tw-animate-css errors, @theme inline dark mode conflicts, @apply breaking, v3 migration issues.
user-invocable: true
---

# Tailwind v4 + shadcn/ui Production Stack

**Production-tested**: WordPress Auditor (https://wordpress-auditor.webfonts.workers.dev)
**Last Updated**: 2026-01-20
**Versions**: tailwindcss@4.1.18, @tailwindcss/vite@4.1.18
**Status**: Production Ready

---

## Quick Start (Follow This Exact Order)

```bash
# 1. Install dependencies
pnpm add tailwindcss @tailwindcss/vite
pnpm add -D @types/node tw-animate-css
pnpm dlx shadcn@latest init

# 2. Delete v3 config if exists
rm tailwind.config.ts # v4 doesn't use this file
```

**vite.config.ts**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
 plugins: [react(), tailwindcss()],
 resolve: { alias: { '@': path.resolve(__dirname, './src') } }
})
```

**components.json** (CRITICAL):
```json
{
 "tailwind": {
 "config": "",
 "css": "src/index.css",
 "baseColor": "slate",
 "cssVariables": true
 }
}
```

---

## The Four-Step Architecture (MANDATORY)

Skipping steps will break your theme. Follow exactly:

### Step 1: Define CSS Variables at Root

```css
/* src/index.css */
@import "tailwindcss";
@import "tw-animate-css";

:root {
 --background: hsl(0 0% 100%);
 --foreground: hsl(222.2 84% 4.9%);
 --primary: hsl(221.2 83.2% 53.3%);
}

.dark {
 --background: hsl(222.2 84% 4.9%);
 --foreground: hsl(210 40% 98%);
 --primary: hsl(217.2 91.2% 59.8%);
}
```

**Critical**: Define at root level (NOT inside `@layer base`). Use `hsl()` wrapper.

### Step 2: Map Variables to Tailwind Utilities

```css
@theme inline {
 --color-background: var(--background);
 --color-foreground: var(--foreground);
 --color-primary: var(--primary);
}
```

**Why**: Generates utility classes (`bg-background`, `text-primary`). Without this, utilities won't exist.

### Step 3: Apply Base Styles

```css
@layer base {
 body {
 background-color: var(--background);
 color: var(--foreground);
 }
}
```

**Critical**: Reference variables directly. Never double-wrap: `hsl(var(--background))`.

### Step 4: Result - Automatic Dark Mode

```tsx
<div className="bg-background text-foreground">
 {/* No dark: variants needed - theme switches automatically */}
</div>
```

---

## Dark Mode Setup

**1. Create ThemeProvider** (see `templates/theme-provider.tsx`)

**2. Wrap App**:
```typescript
import { ThemeProvider } from '@/components/theme-provider'

ReactDOM.createRoot(document.getElementById('root')!).render(
 <ThemeProvider defaultTheme="system" storageKey="ui-theme">
 <App />
 </ThemeProvider>
)
```

---

## Critical Rules

### Always Do:

1. Wrap colors with `hsl()` in `:root`/`.dark`: `--bg: hsl(0 0% 100%);`
2. Use `@theme inline` to map all CSS variables
3. Set `"tailwind.config": ""` in components.json
4. Delete `tailwind.config.ts` if exists
5. Use `@tailwindcss/vite` plugin (NOT PostCSS)

### Never Do:

1. Put `:root`/`.dark` inside `@layer base` (causes cascade issues)
2. Use `.dark { @theme { } }` pattern (v4 doesn't support nested @theme)
3. Double-wrap colors: `hsl(var(--background))`
4. Use `tailwind.config.ts` for theme (v4 ignores it)
5. Use `@apply` directive (deprecated in v4, see error #7)
6. Use `dark:` variants for semantic colors (auto-handled)
7. Use `@apply` with `@layer base` or `@layer components` classes (v4 breaking change - use `@utility` instead)
8. Wrap ANY styles in `@layer base` without understanding CSS layer ordering

---

## Common Errors & Solutions

This skill prevents **8 documented errors**.

### 1. tw-animate-css Import Error

**Error**: "Cannot find module 'tailwindcss-animate'"
**Cause**: shadcn/ui deprecated `tailwindcss-animate` for v4.
**Solution**:
```bash
pnpm add -D tw-animate-css

# Add to src/index.css:
@import "tailwindcss";
@import "tw-animate-css";
```

### 2. Colors Not Working

**Error**: `bg-primary` doesn't apply styles
**Cause**: Missing `@theme inline` mapping
**Solution**:
```css
@theme inline {
 --color-background: var(--background);
 --color-foreground: var(--foreground);
 --color-primary: var(--primary);
}
```

### 3. Dark Mode Not Switching

**Error**: Theme stays light/dark
**Cause**: Missing ThemeProvider
**Solution**: Create ThemeProvider, wrap app, verify `.dark` class toggles on `<html>` element.

### 4. Duplicate @layer base

**Error**: "Duplicate @layer base" in console
**Cause**: shadcn init adds `@layer base` - don't add another
**Solution**: Single `@layer base` block.

### 5. Build Fails with tailwind.config.ts

**Error**: "Unexpected config file"
**Cause**: v4 doesn't use `tailwind.config.ts` (v3 legacy)
**Solution**: `rm tailwind.config.ts`

### 6. @theme inline Breaks Dark Mode in Multi-Theme Setups

**Error**: Dark mode doesn't switch when using `@theme inline` with custom variants
**Cause**: `@theme inline` bakes variable VALUES into utilities at build time.
**Solution**: Use `@theme` (without inline) for multi-theme scenarios.

**When to use inline**: Single theme + dark mode toggle (like shadcn/ui default)
**When NOT to use inline**: Multi-theme systems, dynamic theme switching beyond light/dark

### 7. @apply with @layer base/components (v4 Breaking Change)

**Error**: `Cannot apply unknown utility class: custom-button`
**Cause**: In v4, only classes defined with `@utility` are available to `@apply`.
**Migration**:
```css
/* v4 pattern (required) */
@utility custom-button {
 @apply px-4 py-2 bg-blue-500;
}
```

### 8. @layer base Styles Not Applying

**Error**: Styles defined in `@layer base` seem to be ignored
**Cause**: v4 uses native CSS layers. Base styles CAN be overridden by utility layers.
**Solution**: Don't use `@layer base` - define styles at root level:
```css
@import "tailwindcss";

body {
 background-color: var(--background);
}
```

---

## Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| `bg-primary` doesn't work | Missing `@theme inline` | Add `@theme inline` block |
| Colors all black/white | Double `hsl()` wrapping | Use `var(--color)` not `hsl(var(--color))` |
| Dark mode not switching | Missing ThemeProvider | Wrap app in ThemeProvider |
| Build fails | `tailwind.config.ts` exists | Delete file |
| Animation errors | Using `tailwindcss-animate` | Install `tw-animate-css` |

---

## What's New in Tailwind v4

### OKLCH Color Space (December 2024)

Tailwind v4.0 replaced the entire default color palette with OKLCH, a perceptually uniform color space.

**Why OKLCH**:
- **Perceptual consistency**: HSL's "50% lightness" is visually inconsistent across hues
- **Better gradients**: Smooth transitions without muddy middle colors
- **Wider gamut**: Supports colors beyond sRGB on modern displays

**Browser Support** (January 2026): Chrome 111+, Firefox 113+, Safari 15.4+, Edge 111+. Global coverage: 93.1%

**Automatic Fallbacks**: Tailwind generates sRGB fallbacks for older browsers.

### Built-in Features (No Plugin Needed)

**Container Queries** (built-in as of v4.0):
```tsx
<div className="@container">
 <div className="@lg:grid-cols-2">
 Content responds to container width, not viewport
 </div>
</div>
```

**Line Clamp** (built-in as of v3.3):
```tsx
<p className="line-clamp-3">Truncate to 3 lines with ellipsis...</p>
```

---

## Tailwind v4 Plugins

Use `@plugin` directive (NOT `require()` or `@import`):

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

**Common Plugin Errors**:
```css
/* WRONG - v3 syntax */
@import "@tailwindcss/typography";

/* CORRECT - v4 syntax */
@plugin "@tailwindcss/typography";
```

---

## Migration from v3

**Key Changes**:
- Delete `tailwind.config.ts`
- Move theme to CSS with `@theme inline`
- Replace `@tailwindcss/line-clamp` (now built-in: `line-clamp-*`)
- Replace `tailwindcss-animate` with `tw-animate-css`
- Update plugins: `require()` → `@plugin`

**Warning**: The `@tailwindcss/upgrade` utility often fails. Manual migration recommended.

---

## Setup Checklist

- [ ] `@tailwindcss/vite` installed (NOT postcss)
- [ ] `vite.config.ts` uses `tailwindcss()` plugin
- [ ] `components.json` has `"config": ""`
- [ ] NO `tailwind.config.ts` exists
- [ ] `src/index.css` follows 4-step pattern
- [ ] ThemeProvider wraps app
- [ ] Theme toggle works

---

## Official Documentation

- **shadcn/ui Vite Setup**: https://ui.shadcn.com/docs/installation/vite
- **shadcn/ui Tailwind v4**: https://ui.shadcn.com/docs/tailwind-v4
- **Tailwind v4 Docs**: https://tailwindcss.com/docs

---

**Last Updated**: 2026-01-20
**Skill Version**: 3.0.0
**Tailwind v4**: 4.1.18 (Latest)
