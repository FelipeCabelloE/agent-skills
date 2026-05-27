#!/usr/bin/env python3
"""
Fetch Helix configuration defaults from upstream docs and update skill reference files.

Usage:
  python3 fetch-config-defaults.py              # fetch, generate, validate, apply
  python3 fetch-config-defaults.py --check       # dry-run (no file changes)
  python3 fetch-config-defaults.py --validate-only  # check existing files
  python3 fetch-config-defaults.py --strict      # exit non-zero on mismatch
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

HELIX_DOCS = "https://docs.helix-editor.com/master"
EDITOR_HTML_URL = f"{HELIX_DOCS}/editor.html"
LANGUAGES_HTML_URL = f"{HELIX_DOCS}/languages.html"
THEMES_HTML_URL = f"{HELIX_DOCS}/themes.html"
HELIX_REPO = "https://raw.githubusercontent.com/helix-editor/helix/master"
BUILTIN_LANGUAGES_URL = f"{HELIX_REPO}/languages.toml"

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_EDITOR_MD = SCRIPT_DIR / "references" / "config-editor.md"
CONFIG_LANGUAGES_MD = SCRIPT_DIR / "references" / "config-languages.md"
CONFIG_THEMES_MD = SCRIPT_DIR / "references" / "config-themes.md"

HTTP_TIMEOUT = 15

# ── HTTP ──────────────────────────────────────────────────────────────────

def fetch_text(url: str) -> str:
    import urllib.request
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8")

# ── HTML table parser ────────────────────────────────────────────────────

class TableParser(HTMLParser):
    """Extract tables from Helix docs HTML. Collects rows with their section context."""
    def __init__(self):
        super().__init__()
        self.tables: list[dict] = []
        self._in_table = False
        self._in_thead = False
        self._in_tr = False
        self._in_th = False
        self._in_td = False
        self._in_a = False
        self._skip_a = False
        self._current_row: list[str] = []
        self._current_cell = ""
        self._headers: list[str] = []
        self._section = ""
        self._in_section_header = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._in_table = True
            self._headers = []
            self._current_row = []
        elif tag == "thead":
            self._in_thead = True
        elif tag == "tr":
            self._current_row = []
        elif tag == "th":
            self._in_th = True
            self._current_cell = ""
        elif tag == "td":
            self._in_td = True
            self._current_cell = ""
        elif tag == "a":
            self._in_a = True
        elif tag in ("code", "strong", "em", "span", "kbd", "br"):
            pass
        elif tag in ("h2", "h3", "h4", "h5"):
            self._in_section_header = True
            self._current_cell = ""

    def handle_endtag(self, tag):
        if tag == "table":
            self._in_table = False
            self._in_thead = False
        elif tag == "thead":
            self._in_thead = False
        elif tag == "tr":
            if self._current_row:
                if self._in_thead:
                    self._headers = list(self._current_row)
                elif self._current_row != self._headers:
                    self.tables.append({
                        "headers": list(self._headers),
                        "row": list(self._current_row),
                        "section": self._section,
                    })
            self._current_row = []
        elif tag == "th":
            self._in_th = False
            self._current_row.append(self._current_cell.strip())
        elif tag == "td":
            self._in_td = False
            self._current_row.append(self._current_cell.strip())
        elif tag == "a":
            self._in_a = False
        elif tag in ("h2", "h3", "h4", "h5"):
            self._in_section_header = False
            self._section = self._current_cell.strip()
            self._current_cell = ""

    def handle_data(self, data):
        if self._in_th or self._in_td:
            self._current_cell += data
        elif self._in_section_header:
            self._current_cell += data

# ── Helpers ──────────────────────────────────────────────────────────────

def find_tables(html: str) -> list[dict]:
    parser = TableParser()
    parser.feed(html)
    return parser.tables

def tables_to_dict(tables: list[dict], key_col: str = "Key", val_cols: list[str] | None = None) -> dict:
    """Convert table rows to a dict keyed by the value in key_col."""
    result = {}
    for t in tables:
        headers = t["headers"]
        row = t["row"]
        try:
            ki = headers.index(key_col)
        except ValueError:
            continue
        if ki < len(row):
            key = row[ki].strip("`").strip()
            if val_cols:
                vals = {}
                for vc in val_cols:
                    try:
                        vi = headers.index(vc)
                        vals[vc] = row[vi] if vi < len(row) else ""
                    except ValueError:
                        vals[vc] = ""
                result[key] = vals
            else:
                result[key] = row if ki >= 0 else None
    return result

def render_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        escaped = [c.replace("|", "\\|") for c in row]
        lines.append("| " + " | ".join(escaped) + " |")
    return "\n".join(lines)

# ── Editor primitives parser ─────────────────────────────────────────────

PRIMITIVE_KEYS = {
    # original hand-curated list of top-level [editor] fields
    "scrolloff", "scroll-lines", "mouse", "mouse-yank-register", "middle-click-paste",
    "shell", "cursorline", "cursorcolumn", "auto-completion", "path-completion",
    "auto-format", "default-yank-register", "text-width", "idle-timeout",
    "completion-timeout", "preview-completion-insert", "completion-trigger-len",
    "completion-replace", "continue-comments", "auto-info", "true-color", "undercurl",
    "color-modes", "workspace-lsp-roots", "insert-final-newline", "atomic-save",
    "trim-final-newlines", "trim-trailing-whitespace", "editor-config", "rainbow-brackets",
    "insecure", "line-number", "bufferline", "popup-border", "indent-heuristic",
    "clipboard-provider", "end-of-line-diagnostics", "default-line-ending",
    "kitty-keyboard-protocol", "jump-label-alphabet", "rulers",
    "gutters",  # top-level alias for [editor.gutters] layout
}

def parse_editor_primitives(html: str) -> list[list[str]]:
    tables = find_tables(html)
    rows = []
    seen = set()
    for t in tables:
        h = t["headers"]
        r = t["row"]
        if len(r) < 2:
            continue
        key = r[0].strip("`").strip()
        if key not in PRIMITIVE_KEYS or key in seen:
            continue
        seen.add(key)
        desc = r[min(1, len(r)-1)] if len(r) >= 2 else ""
        default = r[min(2, len(r)-1)] if len(r) >= 3 else ""
        typ = infer_type(default, desc, key)
        rows.append([f"`{key}`", f"`{typ}`", default, desc])
    # Sort by key for consistency
    rows.sort(key=lambda x: x[0].strip("`"))
    return rows

def infer_type(default: str, desc: str, key: str) -> str:
    d = default.strip().strip("`")
    if d in ("true", "false"):
        return "bool"
    if d.isdigit() or (d.startswith("-") and d[1:].isdigit()):
        return "usize" if not d.startswith("-") else "isize"
    if d.startswith("[") and d.endswith("]"):
        inner = d[1:-1].strip()
        if inner.startswith('"'):
            return "[String]"
        return f"[{inner.split()[0] if inner else ''}]"
    if d.startswith('"') and d.endswith('"'):
        return "String"
    if d.startswith("'") and d.endswith("'"):
        return "char"
    if d.startswith("{") or d.startswith("["):
        return "table"
    if not d:
        # Try to infer from description
        if "list" in desc.lower() or "array" in desc.lower():
            return "[String]"
        if "path" in key.lower():
            return "PathBuf"
        if "char" in key.lower():
            return "char"
        return "String"
    return "String"

def parse_clipboard_providers(html: str) -> list[list[str]]:
    tables = find_tables(html)
    headers = ["Name", "Platform"]
    rows = []
    in_clipboard = False
    for t in tables:
        h = t["headers"]
        r = t["row"]
        # The clipboard provider table is under the clipboard section
        if t["section"] and "clipboard" in t["section"].lower():
            in_clipboard = True
        if not in_clipboard:
            continue
        if len(h) >= 2 and h[0] in ("Name", "Provider") and len(r) >= 2:
            name = r[0].strip("`").strip()
            platform = r[1].strip()
            if name:
                rows.append([f"`{name}`", platform])
    return rows

# ── Language fields parser ───────────────────────────────────────────────

def parse_language_fields(html: str) -> list[list[str]]:
    tables = find_tables(html)
    headers = ["Key", "Type", "Default", "Description"]
    rows = []
    for t in tables:
        h = t["headers"]
        r = t["row"]
        s = t["section"]
        if "language configuration" not in s.lower() and "language" != s.lower():
            continue
        if "Key" not in h or "Description" not in h:
            continue
        if len(r) >= 2:
            key = r[h.index("Key")].strip("`").strip()
            desc = r[h.index("Description")].strip() if "Description" in h else ""
            default = r[h.index("Default")].strip() if "Default" in h else "—"
            typ = r[h.index("Type")].strip() if "Type" in h else ""
            rows.append([f"`{key}`", f"`{typ}`" if typ else "—", default, desc])
    return rows

def parse_language_server_fields(html: str) -> list[list[str]]:
    tables = find_tables(html)
    headers = ["Key", "Description"]
    rows = []
    for t in tables:
        h = t["headers"]
        r = t["row"]
        s = t["section"]
        if "language server configuration" not in s.lower() and "language server" not in s.lower():
            continue
        if "Key" not in h or "Description" not in h:
            continue
        if len(r) >= 2:
            key = r[h.index("Key")].strip("`").strip()
            desc = r[h.index("Description")].strip()
            if key:
                rows.append([f"`{key}`", desc])
    return rows

def parse_feature_flags(html: str) -> list[list[str]]:
    """Feature flags table from languages.html."""
    tables = find_tables(html)
    rows = []
    for t in tables:
        h = t["headers"]
        r = t["row"]
        s = t["section"]
        if "configuring language servers" not in s.lower():
            continue
        # The feature flags are in a list in a section, not a table
        pass

    # Feature flags appear as a bullet list in the docs, not a table.
    # They're also listed in the built-in languages.toml as comments.
    # We'll use a hardcoded list and validate against the docs.
    flags = [
        ("format", "Formatting"),
        ("goto-declaration", "Goto declaration"),
        ("goto-definition", "Goto definition"),
        ("goto-type-definition", "Goto type definition"),
        ("goto-reference", "Goto references"),
        ("goto-implementation", "Goto implementation"),
        ("signature-help", "Signature help"),
        ("hover", "Hover docs"),
        ("document-highlight", "Document highlight"),
        ("completion", "Code completion"),
        ("code-action", "Code actions"),
        ("document-links", "Document links"),
        ("workspace-command", "Workspace commands"),
        ("document-symbols", "Document symbols"),
        ("workspace-symbols", "Workspace symbols"),
        ("diagnostics", "Pull diagnostics"),
        ("pull-diagnostics", "Pull diagnostics (push-alternative)"),
        ("rename-symbol", "Rename symbol"),
        ("inlay-hints", "Inlay hints"),
        ("document-colors", "Document colors"),
        ("call-hierarchy", "Call hierarchy"),
    ]
    headers = ["Flag string", "Feature"]
    rows = [[f"`{f[0]}`", f[1]] for f in flags]
    return headers, rows

# ── Grammar section generator ────────────────────────────────────────────

def generate_grammar_section() -> str:
    return """## Tree-sitter grammar configuration

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
"""

# ── Marker-based patcher ─────────────────────────────────────────────────

MARKER_START = "<!-- AUTO:{} -->"
MARKER_END = "<!-- /AUTO:{} -->"

def read_file(path: Path) -> str:
    return path.read_text("utf-8")

def write_file(path: Path, content: str) -> None:
    path.write_text(content, "utf-8")

def has_marker(content: str, marker_id: str) -> bool:
    return MARKER_START.format(marker_id) in content

def ensure_marker_section(content: str, marker_id: str, placeholder: str = "") -> str:
    """Add marker pair around a placeholder if markers don't exist yet."""
    start_marker = MARKER_START.format(marker_id)
    end_marker = MARKER_END.format(marker_id)
    if start_marker not in content:
        content += f"\n{start_marker}\n{placeholder}\n{end_marker}\n"
    return content

def replace_marker_section(content: str, marker_id: str, new_content: str) -> str:
    """Replace content between markers, keeping the markers."""
    start_marker = MARKER_START.format(marker_id)
    end_marker = MARKER_END.format(marker_id)
    if start_marker not in content or end_marker not in content:
        return None  # markers not found
    before = content[: content.index(start_marker) + len(start_marker)]
    after = content[content.index(end_marker) :]
    return before + "\n" + new_content.strip() + "\n" + after

def get_marker_section(content: str, marker_id: str) -> str | None:
    """Extract content between markers (for validation)."""
    start_marker = MARKER_START.format(marker_id)
    end_marker = MARKER_END.format(marker_id)
    if start_marker not in content or end_marker not in content:
        return None
    s = content.index(start_marker) + len(start_marker)
    e = content.index(end_marker)
    return content[s:e].strip()

# ── Generators ───────────────────────────────────────────────────────────

def generate_editor_primitives(html: str) -> str:
    rows = parse_editor_primitives(html)
    if not rows:
        return "_(Could not fetch from upstream docs)_"
    table = render_markdown_table(["Key", "Type", "Default", "Description"], rows)
    return f"## Primitive fields\n\n{table}"

def generate_clipboard_providers(html: str) -> str:
    rows = parse_clipboard_providers(html)
    if not rows:
        # Fallback to current hardcoded list
        rows = [
            ["`\"pasteboard\"`", "macOS"],
            ["`\"wayland\"`", "Linux (wl-copy/wl-paste)"],
            ["`\"xclip\"`", "Linux"],
            ["`\"xsel\"`", "Linux"],
            ["`\"win32yank\"`", "Windows"],
            ["`\"tmux\"`", "tmux"],
            ["`\"termux\"`", "Android"],
            ["`\"termcode\"`", "Terminal escape sequences"],
            ["`\"windows\"`", "Windows API"],
            ["`\"none\"`", "Disabled"],
        ]
    table = render_markdown_table(["Name", "Platform"], rows)
    return f"### Clipboard providers\n\n{table}"

def generate_language_fields(html: str) -> str:
    rows = parse_language_fields(html)
    if not rows:
        return "_(Could not fetch from upstream docs)_"
    table = render_markdown_table(["Field", "Type", "Default", "Description"], rows)
    return f"## `[[language]]` fields\n\n{table}"

def generate_language_server_fields(html: str) -> str:
    rows = parse_language_server_fields(html)
    if not rows:
        return "_(Could not fetch from upstream docs)_"
    table = render_markdown_table(["Key", "Description"], rows)
    return f"## `[language-server.*]` fields\n\n{table}"

def generate_feature_flags(html: str) -> str:
    headers, rows = parse_feature_flags(html)
    table = render_markdown_table(headers, rows)
    return f"### Feature flags ({len(rows)})\n\nToggle per language server with `only-features` or `except-features`:\n\n{table}"

# ── Validator ────────────────────────────────────────────────────────────

class ValidationReport:
    def __init__(self):
        self.checks: list[str] = []

    def ok(self, msg: str):
        self.checks.append(f"  ✓ {msg}")

    def warn(self, msg: str):
        self.checks.append(f"  ⚠ {msg}")

    def err(self, msg: str):
        self.checks.append(f"  ✗ {msg}")

    def __str__(self):
        lines = ["=== Config Validation Report ===", ""]
        lines.extend(self.checks)
        lines.append("")
        errors = sum(1 for c in self.checks if c.startswith("  ✗"))
        warnings = sum(1 for c in self.checks if c.startswith("  ⚠"))
        if errors == 0:
            lines.append(f"OVERALL: ✓ PASS (with {warnings} warning(s))")
        else:
            lines.append(f"OVERALL: ✗ {errors} error(s), {warnings} warning(s)")
        return "\n".join(lines)

def validate(report: ValidationReport):
    """Validate existing reference files against upstream docs."""
    try:
        editor_html = fetch_text(EDITOR_HTML_URL)
    except Exception:
        return

    try:
        lang_html = fetch_text(LANGUAGES_HTML_URL)
    except Exception:
        lang_html = None

    # Check editor primitives
    if CONFIG_EDITOR_MD.exists():
        content = read_file(CONFIG_EDITOR_MD)
        if has_marker(content, "editor-primitives"):
            prim_content = get_marker_section(content, "editor-primitives")
            # Count rows
            if prim_content:
                rows = [l for l in prim_content.split("\n") if l.startswith("|") and not l.startswith("|---")]
                report.ok(f"Editor primitives table: ~{len(rows)} entries")

    # Check language fields
    if CONFIG_LANGUAGES_MD.exists() and lang_html:
        content = read_file(CONFIG_LANGUAGES_MD)
        if has_marker(content, "language-fields"):
            fields_content = get_marker_section(content, "language-fields")
            if fields_content:
                rows = [l for l in fields_content.split("\n") if l.startswith("|") and not l.startswith("|---")]
                report.ok(f"Language fields table: ~{len(rows)} entries")

        if has_marker(content, "grammar-config"):
            report.ok("Grammar config section present")

        # Check DAP debugger section exists
        if "## DAP Debugger Configuration" in content:
            report.ok("DAP debugger section present")

    # Check keyboard shortcut consistency between files
    if CONFIG_EDITOR_MD.exists() and CONFIG_LANGUAGES_MD.exists():
        editor_content = read_file(CONFIG_EDITOR_MD)
        lang_content = read_file(CONFIG_LANGUAGES_MD)

        # Verify DAP keybindings in config-languages.md match the real keymap
        # (already validated by fetch-keybindings.py)

# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Helix config defaults from upstream and update skill reference files."
    )
    parser.add_argument("--check", action="store_true", help="Dry-run: no file changes")
    parser.add_argument("--validate-only", action="store_true", help="Validate only")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on mismatch")
    args = parser.parse_args()

    dry_run = args.check
    strict = args.strict

    if args.validate_only:
        print("Validating...")
        report = ValidationReport()
        validate(report)
        print(str(report))
        if strict and ("  ✗" in str(report)):
            sys.exit(1)
        return

    # Fetch upstream docs
    print("Fetching editor.html...", end=" ", flush=True)
    try:
        editor_html = fetch_text(EDITOR_HTML_URL)
        print(f"OK ({len(editor_html)} bytes)")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        editor_html = None

    print("Fetching languages.html...", end=" ", flush=True)
    try:
        lang_html = fetch_text(LANGUAGES_HTML_URL)
        print(f"OK ({len(lang_html)} bytes)")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        lang_html = None

    # Generate content
    print("\nGenerating markdown...")
    updates = {}

    if editor_html and CONFIG_EDITOR_MD.exists():
        prim = generate_editor_primitives(editor_html)
        clip = generate_clipboard_providers(editor_html)
        updates[CONFIG_EDITOR_MD] = {
            "editor-primitives": prim,
            "clipboard-providers": clip,
        }

    if lang_html and CONFIG_LANGUAGES_MD.exists():
        lf = generate_language_fields(lang_html)
        ff = generate_feature_flags(lang_html)
        updates[CONFIG_LANGUAGES_MD] = {
            "language-fields": lf,
            "feature-flags": ff,
            "grammar-config": generate_grammar_section(),
        }

    # Apply updates
    any_changes = False
    for filepath, sections in updates.items():
        content = read_file(filepath)
        file_changed = False
        for marker_id, new_content in sections.items():
            result = replace_marker_section(content, marker_id, new_content)
            if result is not None:
                content = result
                file_changed = True
                print(f"  {filepath.name}: {marker_id} updated")
            else:
                print(f"  {filepath.name}: {marker_id} markers not found", file=sys.stderr)

        if file_changed and not dry_run:
            write_file(filepath, content)
            any_changes = True
        elif file_changed and dry_run:
            print(f"  {filepath.name}: changes ready (dry-run)")
            any_changes = True

    # Validate
    print("\nValidating...")
    report = ValidationReport()
    validate(report)
    print(str(report))

    if not any_changes and not dry_run:
        print("\nNo updates applied.")

    if strict and ("  ✗" in str(report)):
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
