---
name: react-architecture
description: Copy-paste templates for React file and folder conventions - creating or refactoring a component, hook, provider or context, splitting a .tsx/.ts file past 200 lines, extracting a list row, and wiring the `@/` path alias. Use whenever adding, moving or splitting a component/hook/provider in a React project, or deciding where extracted logic belongs.
---

# React architecture

The rules are in the `react-doctrine` skill. This is the mechanical how-to.

## Component

`src/components/Button/` - three files, always.

```tsx
// Button.tsx
import type { ButtonProps } from './types';

export function Button({ label, onPress, variant = 'primary' }: ButtonProps) {
  return (
    <button className={variant === 'primary' ? 'btn-primary' : 'btn-ghost'} onClick={onPress}>
      {label}
    </button>
  );
}
```

```ts
// types.ts - types only, no runtime values
export interface ButtonProps {
  label: string;
  variant?: 'primary' | 'ghost';
  onPress: () => void;
}
```

```ts
// index.ts
export { Button } from './Button';
export type { ButtonProps } from './types';
```

Naming: always `types.ts`, never `Button.ts` - `./Button` would resolve to it
ahead of `Button.tsx`. Never `.d.ts`: `skipLibCheck` skips every `.d.ts`, ours
included, so an error in one is never reported. `import type` is required
(`verbatimModuleSyntax`).

Need a constant, enum or default object? `constants.ts` in the same folder, so
`types.ts` stays types only.

## Handlers

Declared above the `return`, passed by name (doctrine 13):

```tsx
export function Menu({ open, onToggle }: MenuProps) {
  const handleToggle = () => onToggle(!open);
  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') onToggle(false);
  };

  return (
    <div onKeyDown={handleKeyDown}>
      <button onClick={handleToggle}>Menu</button>
    </div>
  );
}
```

A handler that needs a list item's data means the row is its own component:

```tsx
// List.tsx
{items.map((item) => (
  <ListRow key={item.id} item={item} onSelect={onSelect} />
))}

// ListRow/ListRow.tsx
export function ListRow({ item, onSelect }: ListRowProps) {
  const handleSelect = () => onSelect(item.id);
  return <li><button onClick={handleSelect}>{item.label}</button></li>;
}
```

Render props follow the same rule: `const renderSummary = (open: boolean) => (...)`,
then `summary={renderSummary}`. Before adding `useCallback`, name which of the
doctrine's three cases it serves (a `memo` child, a hook dependency, a hook's
or context's return). None applies? Leave it a plain `const`.

## Splitting a file over 200 lines

1. Pull hook clusters out first (see below) - usually enough on its own.
2. Still long? Cut the JSX at its seams.
   - Piece only this component uses → nested folder, same three files:
     ```
     src/components/Card/
     ├── Card.tsx
     ├── types.ts
     ├── index.ts
     └── CardHeader/
         ├── CardHeader.tsx
         ├── types.ts
         └── index.ts
     ```
     The parent imports `./CardHeader`. The nested barrel is not re-exported
     from `Card/index.ts` unless callers outside actually need it.
   - Piece is generic or a second caller exists → new folder under
     `src/components/`, imported as `@/components/CardHeader`.

Don't split by arbitrary line count into `Part1`/`Part2`. If there's no seam,
the component is doing two jobs - find them, name them.

## Hook

```
src/hooks/useDrawer/
├── useDrawer.ts
├── types.ts       # only when the return/options shape needs a name
└── index.ts
```

```ts
// useDrawer.ts - every function a hook returns is stable (doctrine 13, case 3)
import { useCallback, useState } from 'react';
import type { UseDrawer } from './types';

export function useDrawer(initial = false): UseDrawer {
  const [isOpen, setIsOpen] = useState(initial);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);
  const close = useCallback(() => setIsOpen(false), []);
  return { isOpen, toggle, close };
}
```

Placement: used by one component → inside that component's folder
(`Card/useCardMetrics/`). Used by two or more → `src/hooks/`.

Hook past 200 lines → the pure parts (no React) move to `src/utils/`:
- one function, one file: `src/utils/formatCurrency.ts`
- a related set used together: `src/utils/dates/{parse.ts,format.ts,index.ts}`

`src/utils/` is exempt from the folder-per-thing rule. Don't build
`src/utils/formatCurrency/formatCurrency.ts`.

## Provider

`src/providers/MyContext/` - five files.

```ts
// context.ts
import { createContext } from 'react';
import type { MyContextValue } from './types';

export const MyContext = createContext<MyContextValue | undefined>(undefined);
```

```ts
// types.ts
import type { ReactNode } from 'react';

export interface MyContextValue {
  value: string;
  setValue: (next: string) => void;
}

export interface MyContextProviderProps {
  children: ReactNode;
  initialValue?: string;
}
```

```tsx
// MyContextProvider.tsx - the value is memoised: every consumer compares it
import { useMemo, useState } from 'react';
import { MyContext } from './context';
import type { MyContextProviderProps } from './types';

export function MyContextProvider({ children, initialValue = '' }: MyContextProviderProps) {
  const [value, setValue] = useState(initialValue);
  const ctx = useMemo(() => ({ value, setValue }), [value]);

  return <MyContext value={ctx}>{children}</MyContext>;
}
```

```ts
// useMyContext.ts
import { use } from 'react';
import { MyContext } from './context';
import type { MyContextValue } from './types';

export function useMyContext(): MyContextValue {
  const ctx = use(MyContext);
  if (!ctx) throw new Error('useMyContext must be used within <MyContextProvider>');
  return ctx;
}
```

```ts
// index.ts
export { MyContextProvider } from './MyContextProvider';
export { useMyContext } from './useMyContext';
export type { MyContextValue } from './types';
```

`context.ts` stays out of `index.ts` - consumers get the hook, not the raw
context. React 19: `<MyContext value={...}>` (no `.Provider`) and
`use(MyContext)` (no `useContext`). Functions in the value are `useCallback`s
or state setters.

A value that changes often (hover, pointer position) re-renders every consumer.
Split it into a second provider, so components that only need the slow values
don't re-render with it.

## Alias `@/`

Add both halves before writing the first `@/` import.

`tsconfig.app.json` → `compilerOptions`. No `baseUrl` - TypeScript 6
deprecates it and errors; paths resolve relative to the tsconfig without it:
```json
"paths": { "@/*": ["./src/*"] }
```

`vite.config.ts`:
```ts
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
});
```

Relative paths are legal only inside a folder (`./types`, `./CardHeader`).
Anything crossing a folder boundary uses `@/`.

## Before you call it done

- [ ] no file over 200 lines
- [ ] every component/hook/provider folder has an `index.ts`
- [ ] props typed in a sibling `types.ts`, imported with `import type`
- [ ] no `../` chains in imports
- [ ] no function written inside a JSX attribute; every `useCallback` has a reason
- [ ] `npm run build` (runs `tsc -b`) and `npm run lint` pass, and the
      `react-health` static scan is clean
