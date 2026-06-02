# Mantine Extension Packages

## Notifications (`@mantine/notifications`)

```bash
npm install @mantine/notifications
```

```tsx
import { notifications } from '@mantine/notifications';
import '@mantine/notifications/styles.css';

// Wrap app in Notifications provider (once, in root)
import { Notifications } from '@mantine/notifications';

<MantineProvider>
  <Notifications position="top-right" />
  <App />
</MantineProvider>

// Usage anywhere
notifications.show({
  title: 'Success',
  message: 'Data saved successfully',
  color: 'green',
  icon: <IconCheck size={16} />,
  autoClose: 5000,
});

// Presets
notifications.show({ message: 'Loading...', color: 'blue', loading: true, autoClose: false });
notifications.update({ id: 'loading', message: 'Done!', color: 'green', loading: false });
notifications.hide('notification-id');
notifications.clean(); // Remove all
notifications.cleanQueue(); // Remove queued
```

## Modals manager (`@mantine/modals`)

```bash
npm install @mantine/modals
```

```tsx
import { modals } from '@mantine/modals';
import { ModalsProvider } from '@mantine/modals';
import '@mantine/modals/styles.css';

// Wrap app
<ModalsProvider>
  <App />
</ModalsProvider>

// Confirm dialog
modals.openConfirmModal({
  title: 'Delete post',
  children: <Text>Are you sure?</Text>,
  labels: { confirm: 'Delete', cancel: 'Cancel' },
  confirmProps: { color: 'red' },
  onConfirm: () => deletePost(),
});

// Custom modal
const modalId = modals.open({
  title: 'Custom',
  children: <MyForm onSuccess={() => modals.close(modalId)} />,
  size: 'lg',
});

modals.closeAll();
```

## Spotlight (`@mantine/spotlight`)

```bash
npm install @mantine/spotlight
```

```tsx
import { Spotlight, spotlight } from '@mantine/spotlight';
import '@mantine/spotlight/styles.css';

// Add to app
<Spotlight
  shortcut="mod + K"
  actions={[
    { id: 'dashboard', label: 'Dashboard', description: 'Go to dashboard', onClick: () => {} },
    { id: 'settings', label: 'Settings', onClick: () => {} },
  ]}
/>

// Open programmatically
spotlight.open();
```

## Carousel (`@mantine/carousel`)

```bash
npm install @mantine/carousel
```

```tsx
import { Carousel } from '@mantine/carousel';
import '@mantine/carousel/styles.css';

<Carousel withIndicators height={200} slideSize="33.33%" slideGap="md" loop>
  <Carousel.Slide>Slide 1</Carousel.Slide>
  <Carousel.Slide>Slide 2</Carousel.Slide>
  <Carousel.Slide>Slide 3</Carousel.Slide>
</Carousel>
```

## Dropzone (`@mantine/dropzone`)

```bash
npm install @mantine/dropzone
```

```tsx
import { Dropzone } from '@mantine/dropzone';
import '@mantine/dropzone/styles.css';

<Dropzone onDrop={(files) => console.log(files)} accept={['image/png', 'image/jpeg']} maxSize={5 * 1024 ** 2}>
  <Group justify="center" style={{ pointerEvents: 'none' }}>
    <IconUpload size={50} />
    <Text>Drag images here or click to select</Text>
  </Group>
</Dropzone>
```

## Rich text editor (`@mantine/tiptap`)

```bash
npm install @mantine/tiptap @tiptap/react @tiptap/extension-link @tiptap/starter-kit
```

```tsx
import { RichTextEditor, Link } from '@mantine/tiptap';
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import '@mantine/tiptap/styles.css';

const editor = useEditor({
  extensions: [StarterKit, Link],
  content: '<p>Start editing...</p>',
});

<RichTextEditor editor={editor}>
  <RichTextEditor.Toolbar>
    <RichTextEditor.ControlsGroup>
      <RichTextEditor.Bold />
      <RichTextEditor.Italic />
      <RichTextEditor.Link />
    </RichTextEditor.ControlsGroup>
  </RichTextEditor.Toolbar>
  <RichTextEditor.Content />
</RichTextEditor>
```

## Code highlight (`@mantine/code-highlight`)

```bash
npm install @mantine/code-highlight
```

```tsx
import { CodeHighlight, InlineCodeHighlight } from '@mantine/code-highlight';
import '@mantine/code-highlight/styles.css';

<CodeHighlight code="console.log('hello')" language="ts" />
<InlineCodeHighlight code="const x = 1" language="ts" />
```

## Charts (`@mantine/charts`)

```bash
npm install @mantine/charts recharts
```

```tsx
import { LineChart, BarChart, AreaChart } from '@mantine/charts';
import '@mantine/charts/styles.css';

const data = [
  { month: 'Jan', sales: 120, profit: 40 },
  { month: 'Feb', sales: 200, profit: 80 },
];

<LineChart
  h={300}
  data={data}
  dataKey="month"
  series={[
    { name: 'sales', color: 'blue.6' },
    { name: 'profit', color: 'teal.6' },
  ]}
  curveType="natural"
/>
```

### Available chart types
- `LineChart`, `AreaChart`, `BarChart` — standard series
- `ScatterChart` — scatter plot
- `PieChart` — pie/donut (use `data` not `dataKey`/`series`)
- `RadarChart` — radar/spider
- `RadialBarChart` — radial bar
- `FunnelChart` — funnel
- `CompositeChart` — mix of line + bar + area
- `Sparkline` — mini inline chart
- `DonutChart` — donut variant of pie
- `Tooltip` — custom tooltip component (reusable across chart types)

All charts share: `h`, `data`, `dataKey` (not for Pie), `series` (not for Pie), `withLegend`, `withTooltip`, `gridAxis`, `tickLine`, `valueFormatter`.

## Navigation progress (`@mantine/nprogress`)

```bash
npm install @mantine/nprogress
```

```tsx
import { nprogress } from '@mantine/nprogress';
import { NavigationProgress } from '@mantine/nprogress';
import '@mantine/nprogress/styles.css';

// In root layout
<NavigationProgress />

// During navigation
nprogress.start();
nprogress.set(50);
nprogress.increment();
nprogress.complete();
nprogress.reset();
nprogress.stop();
```

## Schedule (`@mantine/schedule`)

```bash
npm install @mantine/schedule @mantine/dates rrule
```

Calendar/scheduling components with day/week/month views.

## Store (`@mantine/store`)

```bash
npm install @mantine/store
```

```tsx
import { createStore, useStore } from '@mantine/store';

const store = createStore({
  key: 'my-store',
  state: { count: 0 },
});

function Counter() {
  const { count } = useStore(store);
  return <Text>{count}</Text>;
}

// Update from anywhere
store.setState({ count: 5 });
store.updateState((prev) => ({ count: prev.count + 1 }));
```

## MantineProvider variants

`@mantine/carousel`, `@mantine/tiptap`, `@mantine/notifications`,
`@mantine/modals`, `@mantine/spotlight`, `@mantine/nprogress`,
`@mantine/code-highlight`, `@mantine/dropzone`, `@mantine/charts`,
`@mantine/schedule`
all need their provider (if they have one) nested inside `MantineProvider`.

CSS files for each package must also be imported at the root, for example:
```tsx
import '@mantine/notifications/styles.css';
import '@mantine/spotlight/styles.css';
// etc.
```
