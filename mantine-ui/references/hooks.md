# Mantine Hooks Catalog

All hooks are imported from `@mantine/hooks`:

```tsx
import { useDisclosure, useClickOutside, useMediaQuery } from '@mantine/hooks';
```

## State Management

| Need | Hook | Usage |
|---|---|---|
| Boolean toggle (modal, drawer) | `useDisclosure(initialState?)` | Returns `[opened, { open, close, toggle }]` |
| Counter | `useCounter(initialValue, { min, max, step })` | Returns `[value, { increment, decrement, set, reset }]` |
| Toggle between values | `useToggle([...values])` | `[value, toggle]` — cycles through options |
| Object state (like class setState) | `useSetState(initial)` | `[state, setState]` where setState merges partial |
| Array state | `useListState(initial?)` | `[list, { append, prepend, remove, reorder, filter, setItem, ... }]` |
| State with undo/redo | `useStateHistory(value, { limit })` | `[state, { push, undo, redo }]` |
| Queue (limited capacity) | `useQueue({ initialValues, limit })` | `[state, { add, update, clean }]` |
| Previous value | `usePrevious(value)` | Returns previous render's value |
| Map state | `useMap(initial?)` | `[map, { get, set, delete, clear }]` |
| Set state | `useSet(initial?)` | `[set, { add, has, delete, clear, toggle }]` |
| Force update | `useForceUpdate()` | Returns `() => void` — call to re-render |
| Selection manager | `useSelection(data, defaultValue?)` | `[selection, { select, deselect, toggle, clear, isSelected }]` |
| Uncontrolled pattern | `useUncontrolled({ value, defaultValue, onChange })` | For building controlled/uncontrolled components |

## UI & DOM Interaction

| Need | Hook | Usage |
|---|---|---|
| Detect click outside | `useClickOutside(handler)` | Returns a ref to attach |
| Hover state | `useHover()` | `{ ref, hovered }` |
| Focus trap | `useFocusTrap(active?)` | Returns ref, traps Tab key |
| Focus within | `useFocusWithin()` | `{ ref, focused }` |
| Intersection observer | `useIntersection(options?)` | `{ ref, entry }` |
| In viewport | `useInViewport()` | `{ ref, inViewport }` |
| Element size | `useElementSize()` | `{ ref, width, height }` |
| Resize observer | `useResizeObserver()` | Returns `[ref, { width, height }]` |
| Smooth scroll to | `useScrollIntoView(options?)` | `{ targetRef, scrollableRef, scrollIntoView }` |
| Scroll direction | `useScrollDirection()` | Returns `'up'` or `'down'` |
| Scroll spy (headings) | `useScrollSpy({ selector, options })` | Returns `{ active, items }` for ToC |
| Hide on scroll | `useHeadroom({ fixedAt, ... })` | `{ ref, pinned }` — header show/hide |
| Text selection | `useTextSelection()` | `{ selection, text }` |
| Mouse position | `useMouse()` | `{ ref, x, y, ... }` |
| Drag move | `useMove(handler, options?)` | `{ ref, active }` — for custom sliders |
| Radial move | `useRadialMove(handler)` | For angle/circular sliders |
| Drag interaction | `useDrag(handler)` | `{ ref, active }` |
| Long press | `useLongPress(handler, options?)` | `{ ref }` — fires after threshold |
| Splitter (panels) | `useSplitter(options?)` | For resizable split panels |
| Collapse animation | `useCollapse(opened)` | `{ ref, height }` |
| Roving tabindex | `useRovingIndex({ ... })` | Keyboard navigation in lists |
| Merge refs | `useMergedRef(...refs)` | Merge multiple refs into one |

## Media & Environment

| Need | Hook | Usage |
|---|---|---|
| Media query | `useMediaQuery(query, initialValue?)` | `matches: boolean \| null` — `'(max-width: 768px)'` |
| Color scheme | `useColorScheme(initialValue?)` | Returns `'light' \| 'dark'` — detects OS preference |
| Reduced motion | `useReducedMotion()` | Returns `true/false` |
| Operating system | `useOs()` | Returns `'windows' \| 'macos' \| 'linux' \| 'android' \| 'ios' \| ...` |
| Screen orientation | `useOrientation()` | `{ angle, type }` |
| Viewport size | `useViewportSize()` | `{ width, height }` |

## Browser & Network

| Need | Hook | Usage |
|---|---|---|
| Local storage state | `useLocalStorage({ key, defaultValue })` | `[value, setValue]` — persisted |
| Session storage | `useSessionStorage({ key, defaultValue })` | Same pattern |
| Read local (read-only) | `readLocalStorageValue({ key })` | Returns stored value |
| Document title | `useDocumentTitle(title)` | Sets document.title |
| Page visibility | `useDocumentVisibility()` | Returns `'visible' \| 'hidden'` |
| Window scroll | `useWindowScroll()` | `[{ x, y }, scrollTo]` |
| Window event | `useWindowEvent(type, handler, options?)` | Typed event listener |
| Event listener | `useEventListener(type, handler, options?)` | Returns ref to attach |
| Mutation observer | `useMutationObserver(callback, options?)` | Returns ref |
| Hash tracking | `useHash()` | `[hash, setHash]` — URL fragment |
| Fullscreen | `useFullscreen()` | `{ ref, toggle, fullscreen }` |
| | `useFullscreenDocument()` | Fullscreen on document |
| | `useFullscreenElement()` | Fullscreen on specific element |
| Favicon | `useFavicon(url)` | Dynamic favicon |
| Idle detection | `useIdle(timeout, events?)` | Returns `boolean` — true if user idle |
| Page leave | `usePageLeave(handler)` | Fires when mouse leaves page |
| Eye dropper | `useEyeDropper()` | `{ supported, open }` |
| Clipboard | `useClipboard({ timeout? })` | `{ copy, copied, reset, error }` |
| Fetch | `useFetch(url, options?)` | `{ data, loading, error, abort, refresh }` |
| File dialog | `useFileDialog(options?)` | `{ files, open, reset }` |

## Hotkeys & Timers

| Need | Hook | Usage |
|---|---|---|
| Keyboard shortcuts | `useHotkeys(hotkeys)` | `useHotkeys([['mod+K', () => {...}]])` |
| Timeout | `useTimeout(callback, delay, options?)` | `{ start, clear, reset }` |
| Interval | `useInterval(callback, delay, options?)` | `{ start, stop, toggle, active }` |

### Hotkey format

```tsx
useHotkeys([
  ['mod+K', () => spotlight.open()],          // Ctrl/Cmd+K
  ['shift+Enter', handleSubmit],               // Shift+Enter
  ['alt+1', () => setActiveTab('profile')],     // Alt+1
  ['mod+shift+N', createNewItem],              // Ctrl/Cmd+Shift+N
]);
```

Modifier keys: `mod` (Cmd on Mac, Ctrl on others), `shift`, `alt`, `ctrl`, `meta`.

## Utility

| Need | Hook / Function |
|---|---|
| Unique ID | `useId()` |
| Dev logging | `useLogger(name, props)` — logs prop changes in dev |
| Validated state | `useValidatedState(initial, validation, value)` |
| Pagination | `usePagination({ total, siblings, boundaries, page, onChange })` |
| Input mask | `useMask({ mask, ... })` — also `formatMask`, `unmask`, `isMaskComplete` |
| Random ID | `randomId()` — utility function |

## Input state shortcut

```tsx
import { useInputState } from '@mantine/hooks';

const [value, setValue] = useInputState('initial');
return <TextInput value={value} onChange={setValue} />;
// setValue works as an onChange handler directly
```
