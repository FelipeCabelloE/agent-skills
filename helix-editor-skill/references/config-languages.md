# `languages.toml` Configuration Reference

Complete reference for language, language server, formatter, and DAP debugger configuration.

---

## Three-layer merge

1. **Built-in** — compiled from `languages.toml` at repo root
2. **Global** — `~/.config/helix/languages.toml`
3. **Project-local** — `<workspace>/.helix/languages.toml` (only if workspace is trusted)

Merge depth = 3. Arrays of `[[language]]` tables matched by `name` field. Higher priority layers override lower.

Workspace trust controlled by `editor.insecure` in global `config.toml`.

---

## Top-level structure

```toml
[[language]]
# per-language config (see below)

[language-server.rust-analyzer]
# LSP server definitions referenced by [[language]] blocks
command = "rust-analyzer"
args = []
timeout = 20
config = { check = { command = "clippy" } }
```

---

## `[[language]]` fields

<!-- AUTO:language-fields -->
## `[[language]]` fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | — | — | The name of the language |
| `language-id` | — | — | The language-id for language servers, checkout the table at TextDocumentItem for the right id |
| `scope` | — | — | A string like source.js that identifies the language. Currently, we strive to match the scope names used by popular TextMate grammars and by the Linguist library. Usually source.<name> or text.<name> in case of markup languages |
| `injection-regex` | — | — | regex pattern that will be tested against a language name in order to determine whether this language should be used for a potential language injection site. |
| `file-types` | — | — | The filetypes of the language, for example ["yml", "yaml"]. See the file-type detection section below. |
| `shebangs` | — | — | The interpreters from the shebang line, for example ["sh", "bash"] |
| `roots` | — | — | A set of marker files used for LSP working directory selection. Helix starts at the file, walks upward, and remembers the topmost i.e. last directory that contains a marker file. For example Cargo.lock, yarn.lock |
| `auto-format` | — | — | Whether to autoformat this language when saving |
| `diagnostic-severity` | — | — | Minimal severity of diagnostic for it to be displayed. (Allowed values: error, warning, info, hint) |
| `comment-tokens` | — | — | The tokens to use as a comment token, either a single token "//" or an array ["//", "///", "//!"] (the first token will be used for commenting). Also configurable as comment-token for backwards compatibility |
| `block-comment-tokens` | — | — | The start and end tokens for a multiline comment either an array or single table of { start = "/*", end = "*/"}. The first set of tokens will be used for commenting, any pairs in the array can be uncommented |
| `indent` | — | — | The indent to use. Has sub keys unit (the text inserted into the document when indenting; usually set to N spaces or "\t" for tabs) and tab-width (the number of spaces rendered for a tab) |
| `language-servers` | — | — | The Language Servers used for this language. See below for more information in the section Configuring Language Servers for a language |
| `grammar` | — | — | The tree-sitter grammar to use (defaults to the value of name) |
| `formatter` | — | — | The formatter for the language, it will take precedence over the lsp when defined. The formatter must be able to take the original file as input from stdin and write the formatted file to stdout. The filename of the current buffer can be passed as argument by using the %{buffer_name} expansion variable. See below for more information in the Configuring the formatter command |
| `soft-wrap` | — | — | editor.softwrap |
| `text-width` | — | — | Maximum line length. Used for the :reflow command and soft-wrapping if soft-wrap.wrap-at-text-width is set, defaults to editor.text-width |
| `rulers` | — | — | Overrides the editor.rulers config key for the language. |
| `path-completion` | — | — | Overrides the editor.path-completion config key for the language. |
| `word-completion` | — | — | Overrides the editor.word-completion configuration for the language. |
| `workspace-lsp-roots` | — | — | Directories (relative to the workspace root) that stop the upward root search early. Meant for project-specific hard overrides in a local .helix/config.toml; |
| `persistent-diagnostic-sources` | — | — | An array of LSP diagnostic sources assumed unchanged when the language server resends the same set of diagnostics. Helix can track the position for these diagnostics internally instead. Useful for diagnostics that are recomputed on save. |
| `rainbow-brackets` | — | — | Overrides the editor.rainbow-brackets config key for the language |
<!-- /AUTO:language-fields -->

---

## `FileType` format

```toml
# Simple extension
file-types = ["rs", "py", "js"]

# Glob pattern (for specific filenames)
file-types = ["rs", { glob = "Cargo.toml" }, { glob = "**/test/**" }]
```

---

## `[language-server.*]` fields

```toml
[language-server.rust-analyzer]
command = "rust-analyzer"
args = []
environment = { RUST_LOG = "info" }     # optional env vars
timeout = 20                              # request timeout (seconds)
config = { checkOnSave = true }           # initializationOptions
required-root-patterns = ["Cargo.toml"]   # optional: only start if root matches
```

### Referencing in `[[language]]`

```toml
[[language]]
name = "rust"
language-servers = [
  "rust-analyzer",                                              # use all features
  { name = "typescript-language-server", except-features = ["format"] }  # exclude format
]
```

<!-- AUTO:feature-flags -->
### Feature flags (21)

Toggle per language server with `only-features` or `except-features`:

| Flag string | Feature |
| --- | --- |
| `format` | Formatting |
| `goto-declaration` | Goto declaration |
| `goto-definition` | Goto definition |
| `goto-type-definition` | Goto type definition |
| `goto-reference` | Goto references |
| `goto-implementation` | Goto implementation |
| `signature-help` | Signature help |
| `hover` | Hover docs |
| `document-highlight` | Document highlight |
| `completion` | Code completion |
| `code-action` | Code actions |
| `document-links` | Document links |
| `workspace-command` | Workspace commands |
| `document-symbols` | Document symbols |
| `workspace-symbols` | Workspace symbols |
| `diagnostics` | Pull diagnostics |
| `pull-diagnostics` | Pull diagnostics (push-alternative) |
| `rename-symbol` | Rename symbol |
| `inlay-hints` | Inlay hints |
| `document-colors` | Document colors |
| `call-hierarchy` | Call hierarchy |
<!-- /AUTO:feature-flags -->

---

<!-- AUTO:grammar-config -->
## Tree-sitter grammar configuration

The source for a language's tree-sitter grammar is specified in a `[[grammar]]` section in `languages.toml`. For example:

```toml
[[grammar]]
name = "mylang"
source = { git = "https://github.com/example/mylang", rev = "a250c4582510ff34767ec3b7dcdd3c24e8c8aa68" }
```

### Grammar fields

| Key     | Type     | Description                                                        |
|---------|----------|--------------------------------------------------------------------|
| `name`  | `String` | The name of the tree-sitter grammar                                |
| `source`| `Table`  | The method of fetching the grammar (see below)                     |

The `source` table supports these sub-keys for git-hosted grammars:

| Key       | Description                                                                    |
|-----------|--------------------------------------------------------------------------------|
| `git`     | A git remote URL from which the grammar should be cloned                       |
| `rev`     | The revision (commit hash or tag) which should be fetched                      |
| `subpath` | A path within the grammar directory to build (for repos hosting multiple grammars) |

### `use-grammars` (top-level key)

Controls which grammars are fetched and built by `hx --grammar fetch` and `hx --grammar build`. Must appear **before** any `[[language]]` or `[[grammar]]` sections.

```toml
# Only these grammars
use-grammars = { only = ["rust", "c", "cpp"] }

# All except these
use-grammars = { except = ["yaml", "json"] }
```

When omitted, all grammars are fetched and built.
<!-- /AUTO:grammar-config -->

---

## DAP Debugger Configuration

Defined under `[language.debugger]` inside a `[[language]]` block.

### `DebugAdapterConfig`

```toml
[[language]]
name = "rust"

[language.debugger]
name = "lldb-dap"
transport = "stdio"            # "stdio" | "tcp"
command = "lldb-dap"
args = []

# For TCP transport:
# transport = "tcp"
# command = "dlv"
# args = ["dap"]
# port-arg = "-l 127.0.0.1:{}"

[language.debugger.quirks]
absolute-paths = false          # workaround for adapter quirks
```

### `DebugAdapterConfig` fields

| Field | Type | Description |
|---|---|---|
| `name` | `String` | Adapter identifier |
| `transport` | `String` | `"stdio"` (spawn+stdin/stdout) or `"tcp"` (spawn+connect after 500ms) |
| `command` | `String` | DAP server binary |
| `args` | `[String]` | Extra CLI args |
| `port-arg` | `Option<String>` | TCP format string with `{}` for port (e.g. `"-l 127.0.0.1:{}"`) |
| `templates` | `[DebugTemplate]` | Launch/attach configurations |
| `quirks` | `DebuggerQuirks` | Adapter workarounds |

### `DebugTemplate`

```toml
[[language.debugger.templates]]
name = "binary"
request = "launch"
completion = [
  { name = "binary", completion = "filename" },
  { name = "cwd", completion = "directory", default = "." }
]
args = { program = "{0}", cwd = "{1}" }
```

| Field | Type | Description |
|---|---|---|
| `name` | `String` | Template label shown to user |
| `request` | `String` | `"launch"` or `"attach"` |
| `completion` | `[DebugConfigCompletion]` | User prompts for parameters |
| `args` | `HashMap<String, Value>` | DAP request args; `{0}`, `{1}` etc. substituted from user input |

### `DebugConfigCompletion`

- **Plain string** (e.g. `"pid"`): prompts with that label, accepts free text
- **Table** `{ name, completion?, default? }`:
  - `completion = "filename"` — filesystem picker
  - `completion = "directory"` — directory picker
  - No completion — free text input
  - `default = "..."` — pre-filled default

### `DebuggerQuirks`

| Field | Type | Default | Description |
|---|---|---|---|
| `absolute-paths` | `bool` | `false` | Whether adapter uses absolute paths (vs relative) |

### Built-in examples

**lldb-dap (stdio):**
```toml
[language.debugger]
name = "lldb-dap"
transport = "stdio"
command = "lldb-dap"

[[language.debugger.templates]]
name = "binary"
request = "launch"
completion = [ { name = "binary", completion = "filename" } ]
args = { program = "{0}" }

[[language.debugger.templates]]
name = "attach"
request = "attach"
completion = [ "pid" ]
args = { pid = "{0}" }
```

**Delve for Go (TCP):**
```toml
[language.debugger]
name = "go"
transport = "tcp"
command = "dlv"
args = ["dap"]
port-arg = "-l 127.0.0.1:{}"

[[language.debugger.templates]]
name = "source"
request = "launch"
completion = [ { name = "entrypoint", completion = "filename", default = "." } ]
args = { mode = "debug", program = "{0}" }
```

### All debug keybindings

| Key | Command | Action |
|---|---|---|
| `space G l` | `dap_launch` | Launch/show template picker |
| `space G r` | `dap_restart` | Restart session |
| `space G b` | `dap_toggle_breakpoint` | Toggle breakpoint |
| `space G c` | `dap_continue` | Continue |
| `space G h` | `dap_pause` | Pause |
| `space G i` | `dap_step_in` | Step in |
| `space G n` | `dap_next` | Step over |
| `space G o` | `dap_step_out` | Step out |
| `space G v` | `dap_variables` | Show variables |
| `space G t` | `dap_terminate` | End session |
| `space G C-c` | `dap_edit_condition` | Edit breakpoint condition |
| `space G C-l` | `dap_edit_log` | Edit breakpoint log message |
| `space G e` | `dap_enable_exceptions` | Enable all exception breakpoints |
| `space G E` | `dap_disable_exceptions` | Disable exception breakpoints |
| `space G s t` | `dap_switch_thread` | Switch active thread |
| `space G s f` | `dap_switch_stack_frame` | Switch stack frame |
| `:debug-start` / `:dbg` | — | Start debug by name with args |
| `:debug-remote` / `:dbg-tcp` | — | Connect via TCP DAP server |
| `:debug-eval` | — | Evaluate expression in debug context |

### Debugging status

Gutter indicators: `●` verified breakpoint, `◯` unverified, `▶` current execution line. Gutter click toggles breakpoint. Theme scopes: `ui.debug.breakpoint`, `ui.debug.active`.

### Limitations

- DAP is **experimental** — many TODOs in source
- Single active debugger in UI (though registry supports multi-session)
- Variable expansion is one level only (no nested object expansion)
- `block_on()` used for async DAP calls — can hang UI on slow adapters
- Editing during debug is not officially supported
- `runInTerminal` requires `[terminal]` config in `config.toml`
- TCP debuggers have a hardcoded 500ms sleep before connecting
- Breakpoints are **not persisted** between sessions
- Line indexing: 0-based internally, sent as 1-based to DAP adapter
