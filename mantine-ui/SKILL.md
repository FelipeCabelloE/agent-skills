---
name: mantine-ui
description: >
  Comprehensive guide for building UIs with Mantine (the React component library
  and hooks collection from mantine.dev). Covers component selection, theming,
  hooks, forms, and best practices. Use this skill whenever the user mentions
  Mantine, @mantine/* packages, wants to add UI components (buttons, inputs,
  modals, tables, navigation), set up theming or styling, manage forms, or
  implement any UI pattern in a React project that has Mantine as a dependency
  — even if they don't explicitly name a component. This is the go-to skill for
  all Mantine-related tasks including setup, component usage, theming, hooks,
  responsive design, and accessibility.
---

# Mantine UI — Guideline

A React component library and hooks collection. These instructions help you use Mantine correctly and effectively.

## First principles

Mantine components are imported from `@mantine/core` (or other `@mantine/*` packages) and used as standard React components. Every component accepts:
- **size**, **color**, **radius**, **variant** — consistent across most components
- **style props** — `m`, `p`, `bg`, `c`, `w`, `h`, `flex`, `display`, etc., all support responsive values
- **`hiddenFrom`/`visibleFrom`** — responsive visibility by breakpoint
- **`lightHidden`/`darkHidden`** — visibility by color scheme

Components are **polymorphic** — the `component` prop changes the rendered HTML element:
```tsx
<Text component="a" href="https://example.com">Link</Text>
<NavLink component={Link} to="/dashboard" />  // React Router
```

## Setup (required before any component can render)

Wrap the app root in `MantineProvider` (usually in `layout.tsx` or `App.tsx`):

```tsx
import { createTheme, MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';

const theme = createTheme({
  primaryColor: 'blue',
  defaultRadius: 'md',
});

export default function App({ children }) {
  return (
    <MantineProvider theme={theme}>
      {children}
    </MantineProvider>
  );
}
```

For SSR (Next.js), also add `ColorSchemeScript` to `<head>` and spread `mantineHtmlProps` on `<html>`:

```tsx
import { ColorSchemeScript, mantineHtmlProps } from '@mantine/core';

export default function RootLayout({ children }) {
  return (
    <html lang="en" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

PostCSS config (`postcss.config.cjs`) is required for `postcss-preset-mantine`:

```js
module.exports = {
  plugins: {
    'postcss-preset-mantine': {},
    'postcss-simple-vars': {
      variables: {
        'mantine-breakpoint-xs': '36em',
        'mantine-breakpoint-sm': '48em',
        'mantine-breakpoint-md': '62em',
        'mantine-breakpoint-lg': '75em',
        'mantine-breakpoint-xl': '88em',
      },
    },
  },
};
```

## Choosing components by need

Read the relevant reference file for the task at hand:

- **`references/components.md`** — Component catalog by UI need. Use when the user wants any UI element: buttons, inputs, modals, tables, navigation, layouts, overlays, data display, etc. Each category includes the primary component, import path, and key props.

- **`references/hooks.md`** — Hook catalog by need. Use when the user wants state management, DOM interaction, media queries, keyboard shortcuts, storage, or any hook-based behavior. Each hook includes import path and typical usage.

- **`references/styling.md`** — Theming, CSS modules, responsive styles, Styles API. Use when the user wants to customize component appearance, override default styles, set up the theme object, add custom colors, or handle responsive design.

- **`references/forms.md`** — Mantine form library (`@mantine/form`). Use when the user needs form state management, validation, or field-level logic.

- **`references/extensions.md`** — Additional packages: notifications, modals manager, spotlight, nprogress, carousel, dropzone, code highlight, tiptap, charts, schedule.

## Styling approach (opinionated)

Always prefer these patterns in order:

1. **Component props** — `color`, `size`, `variant`, `radius`, `style` prop for simple overrides
2. **Theme overrides** — `createTheme({ components: { Button: { defaultProps: { ... } } } })` for app-wide defaults
3. **CSS modules** — `.module.css` files with `postcss-preset-mantine` for custom component styles:

   ```tsx
   // MyComponent.module.css
   .root {
     background-color: var(--mantine-color-blue-6);
     padding: var(--mantine-spacing-md);
     @media (max-width: $mantine-breakpoint-sm) {
       padding: var(--mantine-spacing-xs);
     }
   }
   ```

4. **Styles API** — Use `classNames` or `styles` prop when you need to target internal elements of a component

### Responsive values

Use the `StyleProp` pattern for responsive style props:

```tsx
<Group p={{ base: 'sm', sm: 'md', lg: 'xl' }}>
  {/* responsive padding */}
</Group>

<Text hiddenFrom="sm" visibleFrom="md">
  Hidden on small, visible on medium+
</Text>
```

### CSS variables reference

Key CSS variables available from the Mantine theme:

| Variable | Purpose |
|---|---|
| `--mantine-color-{name}-{1-9}` | Color shades (e.g. `--mantine-color-blue-6`) |
| `--mantine-spacing-{xs-xl}` | Spacing tokens |
| `--mantine-radius-{xs-xl}` | Radius tokens |
| `--mantine-font-size-{xs-xl}` | Font size tokens |
| `--mantine-font-family` | Primary font family |
| `--mantine-line-height-{xs-xl}` | Line height tokens |
| `--mantine-shadow-{xs-xl}` | Box shadow tokens |
| `--mantine-breakpoint-{xs-xl}` | Breakpoints (in em) |
| `--mantine-primary-color-{filled,light,...}` | Resolved primary color |
| `--mantine-color-body` | Body background (auto light/dark) |
| `--mantine-color-text` | Text color (auto light/dark) |

## Color scheme (light/dark)

Mantine supports light, dark, and auto (follows system preference). The `useMantineColorScheme` hook provides control:

```tsx
import { useMantineColorScheme, ActionIcon, Group } from '@mantine/core';
import { IconSun, IconMoon } from '@tabler/icons-react';

function ThemeToggle() {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  return (
    <ActionIcon onClick={toggleColorScheme} variant="outline">
      {colorScheme === 'dark' ? <IconSun /> : <IconMoon />}
    </ActionIcon>
  );
}
```

## Accessibility

Mantine components are built with accessibility in mind, but some patterns deserve attention:

- Pass `aria-label` to icon-only buttons (`ActionIcon`, `CloseButton`)
- Use `label` prop on inputs (it renders a `<label>` element)
- Use `description` and `error` props on inputs for assistive descriptions
- Modal/Drawer focus is trapped automatically
- `Tooltip` has built-in `role="tooltip"` behavior
- Use `NavLink` for navigation menus (proper focus management)

## Icon library

Mantine uses **Tabler Icons** (`@tabler/icons-react`) by convention:

```bash
npm install @tabler/icons-react
```

```tsx
import { IconUser, IconSettings } from '@tabler/icons-react';
<Button leftSection={<IconUser size={16} />}>Profile</Button>
```

## Project conventions

- Import components from their package: `@mantine/core`, `@mantine/hooks`, `@mantine/form`, etc.
- CSS files from packages are imported once at the root: `import '@mantine/core/styles.css'`
- Use CSS modules for custom styles, not inline `style` props (unless dynamic values)
- Prefer `Group` and `Stack` for layout instead of manual flexbox
- Use `Container` for page-width constraints
- Use `AppShell` for full-page application layouts (navbar, header, sidebar)
