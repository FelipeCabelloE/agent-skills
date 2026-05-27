# `[editor]` Configuration Reference

Complete reference for all `[editor]` settings in `config.toml`. See `config-keymaps.md` for `[keys.*]` and `config-themes.md` for `[theme]`.

---

<!-- AUTO:editor-primitives -->
## Primitive fields

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `atomic-save` | `bool` | true | Whether to use atomic operations to write documents to disk. This prevents data loss if the editor is interrupted while writing the file, but may confuse some file watching/hot reloading programs. |
| `auto-completion` | `bool` | true | Enable automatic pop up of auto-completion |
| `auto-format` | `bool` | true | Enable automatic formatting on save1 |
| `auto-info` | `bool` | true | Whether to display info boxes |
| `bufferline` | `String` | "never" | Renders a line at the top of the editor displaying open buffers. Can be always, never or multiple (only shown if more than one buffer is in use) |
| `clipboard-provider` | `String` | Platform and environment specific. | Which API to use for clipboard interaction. One of pasteboard (MacOS), wayland, x-clip, x-sel, win32-yank, termux, tmux, windows, termcode, none, or a custom command set. |
| `color-modes` | `bool` | false | Whether to color the mode indicator with different colors depending on the mode itself |
| `completion-replace` | `bool` | false | Whether to make completions always replace the entire word and not just the part before the cursor |
| `completion-timeout` | `usize` | 250 | Time in milliseconds after typing a word character before completions are shown, set to 5 for instant. |
| `completion-trigger-len` | `usize` | 2 | The min-length of word under cursor to trigger autocompletion |
| `continue-comments` | `bool` | true | if helix should automatically add a line comment token if you create a new line inside a comment. |
| `cursorcolumn` | `bool` | false | Highlight all columns with a cursor |
| `cursorline` | `bool` | false | Highlight all lines with a cursor |
| `default-line-ending` | `String` | "native" | The line ending to use for new documents. Can be native, lf, crlf, ff, cr or nel. native uses the platform’s native line ending (crlf on Windows, otherwise lf). |
| `default-yank-register` | `char` | '"' | Default register used for yank/paste |
| `editor-config` | `bool` | true | Whether to read settings from EditorConfig files |
| `end-of-line-diagnostics` | `String` | "hint" | Minimum severity of diagnostics to render at the end of the line. Set to disable to disable entirely. Refer to the setting about inline-diagnostics for more details |
| `gutters` | `[String]` | ["diagnostics", "spacer", "line-numbers", "spacer", "diff"] | Gutters to display: Available are diagnostics and diff and line-numbers and spacer, note that diagnostics also includes other features like breakpoints, 1-width padding will be inserted if gutters is non-empty |
| `idle-timeout` | `usize` | 250 | Time in milliseconds since last keypress before idle timers trigger. |
| `indent-heuristic` | `String` | "hybrid" | How the indentation for a newly inserted line is computed: simple just copies the indentation level from the previous line, tree-sitter computes the indentation based on the syntax tree and hybrid combines both approaches. If the chosen heuristic is not available, a different one will be used as a fallback (the fallback order being hybrid -> tree-sitter -> simple). |
| `insert-final-newline` | `bool` | true | Whether to automatically insert a trailing line-ending on write if missing |
| `jump-label-alphabet` | `String` | "abcdefghijklmnopqrstuvwxyz" | The characters that are used to generate two character jump labels. Characters at the start of the alphabet are used first. |
| `kitty-keyboard-protocol` | `String` | "auto" | Whether to enable Kitty Keyboard Protocol. Can be enabled, disabled or auto |
| `line-number` | `String` | "absolute" | Line number display: absolute simply shows each line’s number, while relative shows the distance from the current line. When unfocused or in insert mode, relative will still show absolute line numbers |
| `middle-click-paste` | `bool` | true | Middle click paste support |
| `mouse` | `bool` | true | Enable mouse mode |
| `mouse-yank-register` | `String` | * | Which register to use for mouse yanks. |
| `path-completion` | `bool` | true | Enable filepath completion. Show files and directories if an existing path at the cursor was recognized, either absolute or relative to the current opened document or current working directory (if the buffer is not yet saved). Defaults to true. |
| `popup-border` | `String` | "none" | Draw border around popup, menu, all, or none |
| `preview-completion-insert` | `bool` | true | Whether to apply completion item instantly when selected |
| `rainbow-brackets` | `bool` | false | Whether to render rainbow colors for matching brackets. Requires tree-sitter rainbows.scm queries for the language. |
| `rulers` | `[]` | [] | List of column positions at which to display the rulers. Can be overridden by language specific rulers in languages.toml file |
| `scroll-lines` | `usize` | 3 | Number of lines to scroll per scroll wheel step |
| `scrolloff` | `usize` | 5 | Number of lines of padding around the edge of the screen when scrolling |
| `shell` | `String` | Unix: ["sh", "-c"]Windows: ["cmd", "/C"] | Shell to use when running external commands |
| `text-width` | `usize` | 80 | Maximum line length. Used for the :reflow command and soft-wrapping if soft-wrap.wrap-at-text-width is set |
| `trim-final-newlines` | `bool` | false | Whether to automatically remove line-endings after the final one on write |
| `trim-trailing-whitespace` | `bool` | false | Whether to automatically remove whitespace preceding line endings on write |
| `true-color` | `bool` | false | Whether to override automatic detection of terminal truecolor support in the event of a false negative |
| `undercurl` | `bool` | false | Whether to override automatic detection of terminal undercurl support in the event of a false negative |
| `workspace-lsp-roots` | `[]` | [] | Directories relative to the workspace root that are treated as LSP roots. Should only be set in .helix/config.toml |
<!-- /AUTO:editor-primitives -->

---

## Enum fields

| Key | Type | Default | Valid values |
|---|---|---|---|
| `line-number` | `LineNumber` | `"absolute"` | `"absolute"`, `"relative"` |
| `bufferline` | `BufferLine` | `"never"` | `"never"`, `"always"`, `"multiple"` |
| `popup-border` | `PopupBorderConfig` | `"none"` | `"none"`, `"all"`, `"popup"`, `"menu"` |
| `indent-heuristic` | `IndentationHeuristic` | `"hybrid"` | `"simple"`, `"tree-sitter"`, `"hybrid"` |
| `clipboard-provider` | `ClipboardProvider` | auto-detected | See below |
| `end-of-line-diagnostics` | `DiagnosticFilter` | `"hint"` | `"disable"`, `"hint"`, `"info"`, `"warning"`, `"error"` |
| `default-line-ending` | `LineEndingConfig` | `"native"` | `"native"`, `"lf"`, `"crlf"` (with `unicode-lines`: `"ff"`, `"cr"`, `"nel"`) |
| `kitty-keyboard-protocol` | `KittyKeyboardProtocolConfig` | `"auto"` | `"auto"`, `"disabled"`, `"enabled"` |

### DiagnosticFilter values

| String | Shows |
|---|---|
| `"disable"` | Nothing |
| `"hint"` | Hints + everything above |
| `"info"` | Info + warning + error |
| `"warning"` | Warning + error |
| `"error"` | Errors only |

---

## Sub-config structs

### `[editor.gutters]`

```toml
[editor.gutters]
layout = ["diagnostics", "spacer", "line-numbers", "spacer", "diff"]
line-numbers = { min-width = 3 }
```

**`layout` elements:**
| Value | Panel |
|---|---|
| `"diagnostics"` | Diagnostic icons |
| `"line-numbers"` | Line numbers |
| `"spacer"` | Spacer gap |
| `"diff"` | Diff indicators |

### `[editor.auto-pairs]`

```toml
# Boolean shorthand
auto-pairs = true

# Custom pairs
[editor.auto-pairs]
"(" = ")"
"{" = "}"
"[" = "]"
"'" = "'"
```

### `[editor.word-completion]`

```toml
[editor.word-completion]
enable = true
trigger-length = 7       # min chars before word completion shows
```

### `[editor.auto-save]`

```toml
# Shorthand (same as focus-lost = true)
auto-save = true

# Full config
[editor.auto-save]
after-delay = { enable = false, timeout = 3000 }  # ms
focus-lost = false
```

### `[editor.file-picker]`

```toml
[editor.file-picker]
hidden = true               # hide dotfiles
follow-symlinks = true
deduplicate-links = true    # hide symlinks pointing into cwd
parents = true              # read ignore files from parent dirs
ignore = true               # respect .ignore
git-ignore = true           # respect .gitignore
git-global = true           # respect global gitignore
git-exclude = true          # respect .git/info/exclude
max-depth = <int>           # optional max recursion depth
```

### `[editor.file-explorer]`

```toml
[editor.file-explorer]
hidden = false
follow-symlinks = false
parents = false
ignore = false
git-ignore = false
git-global = false
git-exclude = false
flatten-dirs = true         # flatten single-child dirs
```

### `[editor.lsp]`

```toml
[editor.lsp]
enable = true
display-progress-messages = false   # show $/progress
display-messages = true             # show window/showMessage
auto-signature-help = true
display-signature-help-docs = true
display-inlay-hints = false
auto-document-highlight = false
inlay-hints-length-limit = <int>    # optional max chars
display-color-swatches = true
snippets = true
goto-reference-include-declaration = true
```

### `[editor.search]`

```toml
[editor.search]
smart-case = true           # case-insensitive unless uppercase in pattern
wrap-around = true
```

### `[editor.statusline]`

```toml
[editor.statusline]
left = ["mode", "spinner", "file-name", "read-only-indicator", "file-modification-indicator"]
center = []
right = ["diagnostics", "selections", "register", "position", "file-encoding"]
separator = "│"

[editor.statusline.mode]
normal = "NOR"
insert = "INS"
select = "SEL"

[editor.statusline.diagnostics]
severities = ["warning", "error"]

[editor.statusline.workspace-diagnostics]
severities = ["warning", "error"]
```

**StatusLineElement values:**
| Value | Shows |
|---|---|
| `"mode"` | Current mode (NOR/INS/SEL) |
| `"spinner"` | LSP activity spinner |
| `"file-name"` | Relative file path |
| `"file-base-name"` | Basename only |
| `"file-absolute-path"` | Full path |
| `"file-modification-indicator"` | Modified indicator |
| `"read-only-indicator"` | `[readonly]` |
| `"file-encoding"` | Encoding |
| `"file-line-ending"` | CRLF/LF |
| `"file-indent-style"` | Tabs/spaces |
| `"file-type"` | Language ID |
| `"diagnostics"` | Error/warning count |
| `"workspace-diagnostics"` | Workspace error/warning |
| `"selections"` | Cursor count |
| `"primary-selection-length"` | Chars in primary selection |
| `"position"` | Cursor position |
| `"position-percentage"` | Cursor % in file |
| `"separator"` | Separator string |
| `"spacer"` | Space |
| `"total-line-numbers"` | Total lines |
| `"version-control"` | VCS info |
| `"register"` | Active register indicator |
| `"current-working-directory"` | CWD |

### `[editor.cursor-shape]`

```toml
[editor.cursor-shape]
normal = "block"
insert = "bar"
select = "underline"
```

**CursorKind values:** `"block"`, `"bar"`, `"underline"`, `"hidden"`

### `[editor.soft-wrap]`

```toml
[editor.soft-wrap]
enable = false
max-wrap = 20                # max chars per wrapped line
max-indent-retain = 40       # max indent to preserve on wrap
wrap-indicator = "↪"         # wrap indicator char
wrap-at-text-width = false   # wrap at text-width instead of screen edge
```

### `[editor.whitespace]`

```toml
# Simple: render all or none
[editor.whitespace]
render = "all"   # or "none"

# Per-character control
[editor.whitespace.render]
default = "none"   # optional
space = "none"
nbsp = "none"
nnbsp = "none"
tab = "none"
newline = "none"

# Custom characters
[editor.whitespace.characters]
space = "·"      # U+00B7
nbsp = "⍽"       # U+237D
nnbsp = "␣"      # U+2423
tab = "→"        # U+2192
tabpad = " "     # trailing tab fill
newline = "⏎"    # U+23CE
```

### `[editor.indent-guides]`

```toml
[editor.indent-guides]
render = false
character = "│"
skip-levels = 0
```

### `[editor.smart-tab]`

```toml
[editor.smart-tab]
enable = true
supersede-menu = false    # tab dismisses completion menu
```

### `[editor.terminal]`

```toml
[editor.terminal]
command = "kitty"
args = []
```

Auto-detected (in order): tmux (if in tmux), WezTerm, Windows Terminal, conhost.

### `[editor.buffer-picker]`

```toml
[editor.buffer-picker]
start-position = "current"   # or "previous"
```

### `[editor.inline-diagnostics]`

```toml
[editor.inline-diagnostics]
cursor-line = "warning"         # DiagnosticFilter
other-lines = "disable"         # DiagnosticFilter
min-diagnostic-width = 40
prefix-len = 1
max-wrap = 20
max-diagnostics = 10
```

### `[editor.popup-border]`

| Value | Effect |
|---|---|
| `"none"` | No border |
| `"all"` | Border on all popups |
| `"popup"` | Border on doc popups |
| `"menu"` | Border on completion menus |

### Clipboard providers

```toml
# String provider name
clipboard-provider = "xclip"

# Or custom command
[editor.clipboard-provider]
yank = { command = "xclip", args = ["-selection", "clipboard"] }
paste = { command = "xclip", args = ["-selection", "clipboard", "-o"] }
# yank-primary / paste-primary — optional for primary selection
```

**Built-in provider names:**
<!-- AUTO:clipboard-providers -->
### Clipboard providers

| Name | Platform |
| --- | --- |
| `"pasteboard"` | macOS |
| `"wayland"` | Linux (wl-copy/wl-paste) |
| `"xclip"` | Linux |
| `"xsel"` | Linux |
| `"win32yank"` | Windows |
| `"tmux"` | tmux |
| `"termux"` | Android |
| `"termcode"` | Terminal escape sequences |
| `"windows"` | Windows API |
| `"none"` | Disabled |
<!-- /AUTO:clipboard-providers -->

---

## Example: complete minimal config

```toml
theme = "catppuccin_mocha"

[editor]
scrolloff = 8
cursorline = true
line-number = "relative"
bufferline = "multiple"
color-modes = true
auto-save = { focus-lost = true }
soft-wrap = { enable = true }
indent-guides = { render = true }

[editor.lsp]
display-inlay-hints = true

[editor.cursor-shape]
normal = "block"
insert = "bar"
select = "underline"

[editor.statusline]
left = ["mode", "spinner", "file-name"]
right = ["diagnostics", "selections", "position"]

[editor.whitespace]
render = "all"

[editor.file-picker]
hidden = false
```
