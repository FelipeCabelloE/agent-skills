# Mantine Styling & Theming

## MantineProvider

The root of all theming. Wrap your app:

```tsx
import { createTheme, MantineProvider } from '@mantine/core';

const theme = createTheme({
  primaryColor: 'blue',
  defaultRadius: 'md',
  fontFamily: 'Inter, sans-serif',
  colors: {
    brand: ['#f0f', ...],  // 10 shades
  },
});

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="auto">
      {children}
    </MantineProvider>
  );
}
```

### Provider props

| Prop | Type | Description |
|---|---|---|
| `theme` | `MantineThemeOverride` | Theme overrides (partial, deep-merged) |
| `defaultColorScheme` | `'light' \| 'dark' \| 'auto'` | Default color scheme |
| `forceColorScheme` | `'light' \| 'dark'` | Force a scheme (ignores user/system) |
| `classNamesPrefix` | `string` | CSS class prefix (default: `'mantine'`) |
| `withCssVariables` | `boolean` | Generate CSS variables (default: `true`) |
| `withGlobalClasses` | `boolean` | Include global styles (default: `true`) |
| `getRootElement` | `() => HTMLElement` | Element for `data-mantine-color-scheme` |
| `cssVariablesSelector` | `string` | CSS selector for vars (default: `':root'`) |

## Theme object

### `createTheme` helper

Provides type safety. Common overrides:

```tsx
const theme = createTheme({
  primaryColor: 'violet',
  primaryShade: { light: 6, dark: 8 },
  autoContrast: true,
  defaultRadius: 'md',
  fontFamily: 'Inter, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, monospace',
  headings: {
    fontFamily: 'Inter, sans-serif',
    fontWeight: '600',
    sizes: {
      h1: { fontSize: rem(36), lineHeight: '1.4' },
      h2: { fontSize: rem(28), lineHeight: '1.4' },
    },
  },
  colors: {
    brand: colorsTuple('#8B5CF6'),  // generates 10 shades
  },
  spacing: {
    xs: rem(8),
    sm: rem(12),
    md: rem(20),
    lg: rem(28),
    xl: rem(40),
  },
  radius: {
    xs: rem(2),
    sm: rem(4),
    md: rem(8),
    lg: rem(16),
    xl: rem(32),
  },
  shadows: {
    md: '0 4px 12px rgba(0,0,0,0.1)',
    lg: '0 8px 24px rgba(0,0,0,0.12)',
  },
  components: {
    Button: {
      defaultProps: {
        variant: 'light',
        radius: 'md',
      },
      styles: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});
```

### `colorsTuple`

Generates a 10-shade color tuple from a single hex value:

```tsx
import { colorsTuple } from '@mantine/core';

const theme = createTheme({
  colors: {
    brand: colorsTuple('#8B5CF6'),
  },
});
```

### `virtualColor`

Creates a color that resolves differently in light/dark mode:

```tsx
import { virtualColor } from '@mantine/core';

const theme = createTheme({
  colors: {
    secondary: virtualColor({
      name: 'secondary',
      light: 'blue',   // uses blue in light mode
      dark: 'orange',   // uses orange in dark mode
    }),
  },
});
```

### `rem` and `em` utilities

```tsx
import { rem, em } from '@mantine/core';

const theme = createTheme({
  spacing: { xl: rem(40) },  // converts to rem
});
```

## Default colors

Mantine provides 14 default color palettes, each with 10 shades:

`dark`, `gray`, `red`, `pink`, `grape`, `violet`, `indigo`, `blue`, `cyan`, `teal`, `green`, `lime`, `yellow`, `orange`

Use as: `--mantine-color-blue-6`, `var(--mantine-color-gray-7)`, or prop value `"blue"`, `"gray"`, etc.

**Shade conventions:**
- 0–2: Light backgrounds / hover states
- 4–6: Default foreground (filled buttons, text)
- 7–9: Text on light, dark backgrounds

## Component default props

Override defaults for all instances of a component:

```tsx
const theme = createTheme({
  components: {
    TextInput: {
      defaultProps: {
        size: 'md',
        radius: 'sm',
      },
      styles: {
        label: { fontWeight: 600 },
        input: { borderColor: 'var(--mantine-color-gray-3)' },
      },
    },
    Modal: {
      defaultProps: {
        centered: true,
        size: 'lg',
      },
    },
  },
});
```

## CSS modules with postcss-preset-mantine

### Setup

Requires `postcss-preset-mantine` in `postcss.config.cjs` (see main SKILL.md).

### Writing styles

```css
/* MyComponent.module.css */
.root {
  background-color: light-dark(
    var(--mantine-color-white),
    var(--mantine-color-dark-7)
  );
  padding: var(--mantine-spacing-md);
  border-radius: var(--mantine-radius-md);
  border: rem(1px) solid var(--mantine-color-gray-3);
}

/* Responsive: hide above small breakpoint */
.mobile-only {
  @media (min-width: $mantine-breakpoint-sm) {
    display: none;
  }
}

/* PostCSS mixins (convenience) */
.title {
  /* Hover style with color scheme awareness */
  &:hover {
    @mixin hover {
      background-color: var(--mantine-color-blue-light);
    }
  }
}

/* Light/dark aware */
.body {
  @mixin light {
    background-color: var(--mantine-color-white);
  }
  @mixin dark {
    background-color: var(--mantine-color-dark-6);
  }
}
```

### Available postcss-preset-mantine mixins

| Mixin | Purpose |
|---|---|
| `@mixin light` | Styles only in light mode |
| `@mixin dark` | Styles only in dark mode |
| `@mixin hover` | Styles on hover (works on touch devices too) |
| `@mixin rtl` | Styles in RTL direction |
| `@mixin ltr` | Styles in LTR direction |
| `@mixin smaller-than` | `@media (max-width: $breakpoint)` |
| `@mixin larger-than` | `@media (min-width: $breakpoint)` |

### Using styles in components

```tsx
import classes from './MyComponent.module.css';

function MyComponent() {
  return (
    <div className={classes.root}>
      <p className={classes.title}>Content</p>
    </div>
  );
}
```

## Styles API (targeting component internals)

Every Mantine component has named style targets. Use `classNames` to target them:

```tsx
// See docs for each component's StylesNames types
<TextInput
  label="Name"
  classNames={{
    root: classes.inputRoot,
    label: classes.customLabel,
    input: classes.customInput,
    error: classes.customError,
  }}
/>
```

Or use `styles` for dynamic values:

```tsx
<TextInput
  label="Name"
  styles={{
    input: { borderColor: hasError ? 'red' : undefined },
    label: { fontSize: rem(14) },
  }}
/>
```

## Responsive styles

### Style prop values (all spacing, sizing, display props)

```tsx
<Group
  justify={{ base: 'center', sm: 'space-between' }}
  direction={{ base: 'column', sm: 'row' }}
  gap={{ base: 'xs', sm: 'md' }}
>
```

### Visibility by breakpoint

```tsx
<Text hiddenFrom="sm">Visible only on mobile (hidden from sm and up)</Text>
<Text visibleFrom="md">Visible only on medium screens and up</Text>
```

### Visibility by color scheme

```tsx
<Text lightHidden>Hidden in light mode</Text>
<Text darkHidden>Hidden in dark mode</Text>
```

### `useMatches` for responsive hook values

```tsx
import { useMatches } from '@mantine/core';

const buttonText = useMatches({
  base: 'Submit',
  sm: 'Submit Form',
  lg: 'Submit the Registration Form',
});
```

## Light/dark scheme values

Use `light-dark()` CSS function (built into Mantine's PostCSS):

```css
.element {
  color: light-dark(
    var(--mantine-color-black),
    var(--mantine-color-white)
  );
  background: light-dark(
    var(--mantine-color-gray-0),
    var(--mantine-color-dark-8)
  );
}
```

Or use mixins:
```css
.element {
  @mixin light { color: var(--mantine-color-black); }
  @mixin dark { color: var(--mantine-color-white); }
}
```

## Global styles

To add global CSS rules (e.g., for body or html elements):

```tsx
// In your layout/root component
import '@mantine/core/styles.css';
import './global.css';
```

```css
/* global.css */
body {
  background-color: var(--mantine-color-body);
  color: var(--mantine-color-text);
}
```

## Key UX patterns

- **`autoContrast: true`** — automatically adjusts text contrast on colored backgrounds
- **`focusRing: 'auto'`** — shows focus ring only on keyboard navigation (default)
- **`respectReducedMotion: true`** — respects user's `prefers-reduced-motion`
- **`defaultGradient`** — sets the default gradient for gradient variant buttons
