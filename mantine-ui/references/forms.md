# Mantine Forms

Package: `@mantine/form`

```bash
npm install @mantine/form
```

## Basic form

```tsx
import { useForm } from '@mantine/form';
import { TextInput, Button, Group } from '@mantine/core';

function DemoForm() {
  const form = useForm({
    mode: 'uncontrolled', // or 'controlled'
    initialValues: {
      name: '',
      email: '',
      age: 0,
    },
    validate: {
      name: (value) => (value.length < 2 ? 'Name too short' : null),
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      age: (value) => (value < 18 ? 'Must be 18+' : null),
    },
  });

  const handleSubmit = (values) => {
    console.log(values);
  };

  return (
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <TextInput
        label="Name"
        placeholder="Your name"
        key={form.key('name')}
        {...form.getInputProps('name')}
      />
      <TextInput
        label="Email"
        placeholder="your@email.com"
        key={form.key('email')}
        {...form.getInputProps('email')}
      />
      <Group justify="flex-end" mt="md">
        <Button type="submit">Submit</Button>
      </Group>
    </form>
  );
}
```

## Controlled vs uncontrolled

**Uncontrolled (recommended)** — better performance, no re-renders on keystroke:
```tsx
const form = useForm({ mode: 'uncontrolled', initialValues: {...} });
// Add key={form.key('fieldName')} to each input
```

**Controlled** — re-renders on every keystroke:
```tsx
const form = useForm({ mode: 'controlled', initialValues: {...} });
// No key prop needed
```

## Validation

### Sync validation (in `validate` object)

```tsx
const form = useForm({
  initialValues: { email: '' },
  validate: {
    email: (value) => {
      if (!value) return 'Required';
      if (!/^\S+@\S+$/.test(value)) return 'Invalid email';
      return null;
    },
  },
});
```

### Async validation

```tsx
const form = useForm({
  initialValues: { email: '' },
  validate: {
    email: async (value) => {
      const response = await fetch(`/api/check-email?email=${value}`);
      const taken = await response.json();
      return taken ? 'Email is already taken' : null;
    },
  },
});
```

### Validate on change / blur

```tsx
const form = useForm({
  validateInputOnChange: true,           // all fields
  validateInputOnBlur: ['email'],        // specific fields
  validateInputOnChange: ['name', 'email'],
});
```

## Nested values

```tsx
const form = useForm({
  initialValues: {
    user: {
      firstName: '',
      lastName: '',
    },
    address: {
      street: '',
      city: '',
    },
  },
});

// In JSX
<TextInput {...form.getInputProps('user.firstName')} />
<TextInput {...form.getInputProps('address.street')} />
```

## Arrays (dynamic fields)

```tsx
const form = useForm({
  initialValues: {
    members: [{ name: '', role: '' }],
  },
});

const fields = form.getValues().members.map((_, index) => (
  <Group key={index} mt="xs">
    <TextInput {...form.getInputProps(`members.${index}.name`)} />
    <TextInput {...form.getInputProps(`members.${index}.role`)} />
    <Button color="red" onClick={() => form.removeListItem('members', index)}>
      Remove
    </Button>
  </Group>
));

return (
  <>
    {fields}
    <Button onClick={() => form.insertListItem('members', { name: '', role: '' })}>
      Add Member
    </Button>
  </>
);
```

## Form-level actions

| Method | Purpose |
|---|---|
| `form.onSubmit(handler)` | Wrap `<form>` `onSubmit` |
| `form.getInputProps('field')` | Spread on any Mantine input |
| `form.key('field')` | Key prop for uncontrolled mode |
| `form.setFieldValue('field', value)` | Set a field |
| `form.setFieldError('field', 'error')` | Set error manually |
| `form.getValues()` | Get all values |
| `form.setValues(values)` | Set all values |
| `form.reset()` | Reset to initial values |
| `form.validate()` | Validate all fields, returns `hasErrors` |
| `form.isValid()` | Check if valid (async-aware) |
| `form.isDirty()` | Check if any field changed |
| `form.isTouched('field')` | Check if field was touched |
| `form.insertListItem('path', item)` | Add item to array |
| `form.removeListItem('path', index)` | Remove item from array |
| `form.reorderListItem('path', { from, to })` | Reorder items |
| `form.getListState()` | Get list state (for re-render) |
| `form.setInitialValues(values)` | Change initial values |
| `form.initialize(values)` | Reset + set new initial values |
| `form.resetDirty(values?)` | Reset to initial, optionally update initial |
| `form.values` | Access values (controlled) |

## useField (single field)

For stand-alone fields without a full form:

```tsx
import { useField } from '@mantine/form';

const field = useField({
  initialValue: '',
  validate: (value) => (value.length < 3 ? 'Too short' : null),
});

return <TextInput {...field.getInputProps()} />;
```

## createFormContext (form sharing)

Share a form across multiple components:

```tsx
const [FormProvider, useFormContext, useForm] = createFormContext();

// Parent
function Parent() {
  const form = useForm({ initialValues: { name: '', email: '' } });
  return (
    <FormProvider form={form}>
      <Child />
    </FormProvider>
  );
}

// Child
function Child() {
  const form = useFormContext();
  return <TextInput {...form.getInputProps('name')} />;
}
```

## Transformed values (serialization)

```tsx
const form = useForm({
  initialValues: { amount: 0 },
  transformValues: (values) => ({
    ...values,
    amount: values.amount * 100, // convert to cents
  }),
});
```

## TypeScript

```tsx
interface FormValues {
  name: string;
  email: string;
  age: number;
}

const form = useForm<FormValues>({
  initialValues: {
    name: '',
    email: '',
    age: 0,
  },
});
```
