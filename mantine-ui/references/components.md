# Mantine Components Catalog

All components are imported from `@mantine/core` unless otherwise noted.

## Buttons & Actions

| Need | Component | Key Props |
|---|---|---|
| Primary action button | `<Button>` | `variant`: filled / light / outline / subtle / gradient / transparent / white / default |
| Icon-only button | `<ActionIcon>` | Same variants as Button, `size` |
| Close / dismiss | `<CloseButton>` | `size`, `variant` |
| Copy to clipboard | `<CopyButton>` | Renders children with `copied` state |
| File picker trigger | `<FileButton>` | `onChange`, `accept`, `multiple` |

Example:
```tsx
<Button variant="gradient" gradient={{ from: 'blue', to: 'cyan' }} loading>
  Submitting...
</Button>
<Button leftSection={<IconPlus size={16} />}>Add Item</Button>
<Button.Group>
  <Button variant="default">Left</Button>
  <Button variant="default">Right</Button>
</Button.Group>
```

## Inputs & Form Controls

| Need | Component | Key Props |
|---|---|---|
| Single-line text | `<TextInput>` | `label`, `description`, `error`, `placeholder` |
| Multi-line text | `<Textarea>` | Same as TextInput + `autosize`, `minRows`, `maxRows` |
| Number | `<NumberInput>` | `min`, `max`, `step`, `decimalScale`, `prefix`, `suffix` |
| Password | `<PasswordInput>` | Visibility toggle built in |
| Select (with search) | `<Select>` | `data` (array), `searchable`, `clearable`, `allowDeselect` |
| Multi-value select | `<MultiSelect>` | Same as Select + `maxValues` |
| Tags input | `<TagsInput>` | Free-form tag entry |
| Autocomplete | `<Autocomplete>` | `data`, `limit` |
| Native select | `<NativeSelect>` | Native `<select>` element with Mantine styling |
| Checkbox | `<Checkbox>` | `checked`, `indeterminate`, `label` |
| Radio group | `<Radio.Group>` | Children are `<Radio>` components |
| Switch (toggle) | `<Switch>` | `onLabel`, `offLabel`, `labelPosition` |
| Slider | `<Slider>` / `<RangeSlider>` | `min`, `max`, `step`, `marks`, `label` |
| Rating (stars) | `<Rating>` | `value`, `count`, `fractions`, `readOnly` |
| Color picker | `<ColorInput>` | With text field input |
| | `<ColorPicker>` | Full picker (saturation, hue, swatches) |
| File input | `<FileInput>` | `accept`, `multiple`, `clearable` |
| PIN / OTP | `<PinInput>` | `length`, `type`, `mask`, `oneTimeCode` |
| JSON input | `<JsonInput>` | `formatOnBlur`, `validationError`, `autosize` |
| Masked input | `<MaskInput>` | `mask` (pattern string) |

### Input states pattern

```tsx
<TextInput
  label="Email"
  placeholder="your@email.com"
  description="We'll never share your email"
  error={errors.email}
  disabled={isSubmitting}
  required
  withAsterisk
/>
```

## Layout & Containers

| Need | Component | Key Props |
|---|---|---|
| Page wrapper | `<Container>` | `size` (xs-xl or `'fluid'`) |
| Horizonal layout | `<Group>` | `gap`, `justify`, `align`, `wrap` |
| Vertical layout | `<Stack>` | `gap`, `align`, `justify` |
| Flexbox | `<Flex>` | `direction`, `wrap`, `justify`, `align`, `gap` |
| Grid (12-col) | `<Grid>` / `<Grid.Col>` | `gutter`, `span` (responsive) |
| Simple grid | `<SimpleGrid>` | `cols` (responsive), `spacing`, `verticalSpacing` |
| Center | `<Center>` | Centers children horizontally + vertically |
| App shell | `<AppShell>` | See layout section |
| Aspect ratio | `<AspectRatio>` | `ratio` (e.g. `16 / 9`) |
| Divider | `<Divider>` | `orientation`, `size`, `label`, `labelPosition` |
| Paper | `<Paper>` | White/elevated background container |
| Space | `<Space>` | `w` / `h` for spacing |

### Responsive grid
```tsx
<Grid>
  <Grid.Col span={{ base: 12, sm: 6, lg: 4 }}>Column 1</Grid.Col>
  <Grid.Col span={{ base: 12, sm: 6, lg: 4 }}>Column 2</Grid.Col>
  <Grid.Col span={{ base: 12, lg: 4 }}>Column 3</Grid.Col>
</Grid>
```

### Simple grid (auto-calculated)
```tsx
<SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }}>
  <Card>...</Card>
  <Card>...</Card>
  <Card>...</Card>
</SimpleGrid>
```

## Navigation

| Need | Component | Key Props |
|---|---|---|
| Links | `<Anchor>` | `href`, `target`, `underline` |
| Tabs | `<Tabs>` / `<Tabs.Tab>` / `<Tabs.Panel>` | `defaultValue`, `variant`, `orientation`, `keepMounted` |
| Dropdown menu | `<Menu>` / `<Menu.Item>` / `<Menu.Dropdown>` | `trigger` (hover/click), `openDelay` |
| Pagination | `<Pagination>` | `total`, `value`, `onChange`, `boundaries`, `siblings` |
| Stepper | `<Stepper>` / `<Stepper.Step>` | `active`, `orientation`, `allowStepSelect` |
| Breadcrumbs | `<Breadcrumbs>` | Children are `<Anchor>` elements |
| Burger icon | `<Burger>` | `opened`, `onClick` |
| Tree view | `<Tree>` | `data` (tree structure), `expandOnClick` |
| Tree select | `<TreeSelect>` | Like Select but with tree-structured options |
| NavLink | `<NavLink>` | `label`, `leftSection`, `children` (nested nav), `active` |
| ToC generator | `<TableOfContents>` | Auto-generated from heading structure |

### Tabs example
```tsx
<Tabs defaultValue="profile">
  <Tabs.List>
    <Tabs.Tab value="profile" leftSection={<IconUser size={16} />}>Profile</Tabs.Tab>
    <Tabs.Tab value="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel value="profile">Profile content</Tabs.Panel>
  <Tabs.Panel value="settings">Settings content</Tabs.Panel>
</Tabs>
```

### Menu example
```tsx
<Menu>
  <Menu.Target>
    <Button>Actions</Button>
  </Menu.Target>
  <Menu.Dropdown>
    <Menu.Label>User</Menu.Label>
    <Menu.Item leftSection={<IconUser size={14} />}>Profile</Menu.Item>
    <Menu.Item leftSection={<IconSettings size={14} />}>Settings</Menu.Item>
    <Menu.Divider />
    <Menu.Item color="red" leftSection={<IconLogout size={14} />}>Logout</Menu.Item>
  </Menu.Dropdown>
</Menu>
```

## Overlays & Modals

| Need | Component | Key Props |
|---|---|---|
| Modal dialog | `<Modal>` | `opened`, `onClose`, `title`, `size`, `fullScreen`, `centered` |
| Slide-in panel | `<Drawer>` | Same as Modal + `position` (left/right/top/bottom), `offset` |
| Floating dialog | `<Dialog>` | Fixed-position small dialog |
| Tooltip | `<Tooltip>` | `label`, `withArrow`, `position`, `multiline`, `openDelay` |
| Hover card | `<HoverCard>` | Hover-triggered popover with content |
| Popover | `<Popover>` | Click/hover trigger, custom positioning |
| Affix (fixed) | `<Affix>` | `position` object |
| Overlay | `<Overlay>` | `backgroundOpacity`, `blur`, `color`, `gradient` |
| Loading overlay | `<LoadingOverlay>` | `visible`, `loaderProps`, `overlayProps` |

### Modal pattern
```tsx
const [opened, { open, close }] = useDisclosure(false);

return (
  <>
    <Button onClick={open}>Open Modal</Button>
    <Modal opened={opened} onClose={close} title="My Modal" size="lg" centered>
      Modal content
    </Modal>
  </>
);
```

## Data Display

| Need | Component | Key Props |
|---|---|---|
| Avatar | `<Avatar>` | `src`, `name` (initials), `color`, `radius`, `size` |
| Badge / tag | `<Badge>` | `variant`, `color`, `size`, `leftSection`, `fullWidth` |
| Card | `<Card>` | `shadow`, `radius`, `padding`, `withBorder` |
| Table | `<Table>` | `data` (array of objects), `striped`, `highlightOnHover`, `withTableBorder`, `withColumnBorders` |
| Image | `<Image>` | `src`, `alt`, `fallbackSrc`, `radius`, `w`, `h` |
| Progress bar | `<Progress>` | `value`, `color`, `striped`, `animated`, `sections` (multiple bars) |
| Ring progress | `<RingProgress>` | `sections`, `size`, `thickness`, `label` (center) |
| Semi-circle | `<SemiCircleProgress>` | `value`, `labelPosition`, `orientation` |
| Skeleton | `<Skeleton>` | `height`, `width`, `radius`, `animate`, `visible` (children) |
| Timeline | `<Timeline>` / `<Timeline.Item>` | `active`, `color`, `bulletSize`, `lineWidth` |
| Notification | `<Notification>` | `color`, `icon`, `title`, `withCloseButton`, `loading` |
| Marquee | `<Marquee>` | Auto-scrolling content |
| Rolling number | `<RollingNumber>` | Animated number counter |
| Number formatter | `<NumberFormatter>` | `value`, `decimalScale`, `prefix`, `suffix`, `thousandSeparator` |
| Highlight | `<Highlight>` | `highlight` (substring or array of substrings) |
| Mark | `<Mark>` | Highlighted inline text |
| Code / Kbd | `<Code>` / `<Kbd>` | Inline code / keyboard keys |
| List | `<List>` / `<List.Item>` | `type`, `withPadding`, `center`, `icon` |
| Blockquote | `<Blockquote>` | `cite`, `color`, `icon` |
| TableOfContents | `<TableOfContents>` | Auto-generated ToC from content headings |
| Spoiler | `<Spoiler>` | `maxHeight`, `showLabel`, `hideLabel` |

### Card pattern
```tsx
<Card shadow="sm" padding="lg" radius="md" withBorder>
  <Card.Section>
    <Image src="/image.jpg" height={160} alt="Image" />
  </Card.Section>
  <Group justify="space-between" mt="md" mb="xs">
    <Text fw={500}>Title</Text>
    <Badge color="pink">Tag</Badge>
  </Group>
  <Text size="sm" c="dimmed">Description text</Text>
  <Button variant="light" fullWidth mt="md">Action</Button>
</Card>
```

### Table pattern
```tsx
<Table striped highlightOnHover withTableBorder>
  <Table.Thead>
    <Table.Tr>
      <Table.Th>Name</Table.Th>
      <Table.Th>Email</Table.Th>
      <Table.Th>Role</Table.Th>
    </Table.Tr>
  </Table.Thead>
  <Table.Tbody>
    {data.map((row) => (
      <Table.Tr key={row.id}>
        <Table.Td>{row.name}</Table.Td>
        <Table.Td>{row.email}</Table.Td>
        <Table.Td>{row.role}</Table.Td>
      </Table.Tr>
    ))}
  </Table.Tbody>
</Table>
```

## Feedback

| Need | Component | Key Props |
|---|---|---|
| Alert | `<Alert>` | `title`, `color`, `icon`, `withCloseButton`, `variant` |
| Notification toast | `@mantine/notifications` | See extensions reference |
| Progress | `<Progress>` | See data display |
| Loader | `<Loader>` | `type` (bars/oval/dots), `color`, `size` |
| Skeleton | `<Skeleton>` | Loading placeholder |

## AppShell (full application layout)

```tsx
import { AppShell, Burger, Group, NavLink } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';

export default function AppLayout() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <h1>My App</h1>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <NavLink label="Dashboard" leftSection={<IconDashboard size={16} />} />
        <NavLink label="Settings" leftSection={<IconSettings size={16} />} />
      </AppShell.Navbar>

      <AppShell.Main>
        {/* Page content here */}
      </AppShell.Main>
    </AppShell>
  );
}
```

## Accordion (expandable sections)

```tsx
<Accordion defaultValue="item-1">
  <Accordion.Item value="item-1">
    <Accordion.Control>Section 1</Accordion.Control>
    <Accordion.Panel>Content 1</Accordion.Panel>
  </Accordion.Item>
  <Accordion.Item value="item-2">
    <Accordion.Control>Section 2</Accordion.Control>
    <Accordion.Panel>Content 2</Accordion.Panel>
  </Accordion.Item>
</Accordion>
```

## Other utilities

| Component | Purpose |
|---|---|
| `<Collapse>` | Animated expand/collapse |
| `<ScrollArea>` | Styled scrollbar |
| `<Transition>` | CSS transition wrapper |
| `<FocusTrap>` | Trap focus within container |
| `<Portal>` | Render children to a different DOM node |
| `<Splitter>` | Resizable panel split |
| `<Fieldset>` | Grouped form fields |
| `<Pill>` | Removable tag |
| `<PillsInput>` | Input with pill/tag sub-elements |
| `<Indicator>` | Dot/badge indicator on child (e.g., online status) |
| `<ThemeIcon>` | Icon container with theme colors |
