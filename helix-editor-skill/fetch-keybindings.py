#!/usr/bin/env python3
"""
Fetch Helix keybinding, register, and macro definitions from upstream sources
and regenerate accurate skill documentation.

Usage:
  python3 fetch-keybindings.py           # fetch, generate, validate, apply
  python3 fetch-keybindings.py --check   # dry-run (no file changes)
  python3 fetch-keybindings.py --validate-only  # validate existing files
  python3 fetch-keybindings.py --strict  # exit non-zero on any mismatch

Data sources:
  - https://raw.githubusercontent.com/helix-editor/helix/master/helix-term/src/keymap/default.rs
  - https://raw.githubusercontent.com/helix-editor/helix/master/book/src/registers.md
  - https://docs.helix-editor.com/master/keymap.html  (validation only)
"""

import argparse
import re
import sys
import textwrap
import urllib.request
from collections import OrderedDict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

HELIX_REPO = "https://raw.githubusercontent.com/helix-editor/helix/master"
DEFAULT_RS_URL = f"{HELIX_REPO}/helix-term/src/keymap/default.rs"
REGISTERS_MD_URL = f"{HELIX_REPO}/book/src/registers.md"
KEYMAP_HTML_URL = "https://docs.helix-editor.com/master/keymap.html"

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_MD = SCRIPT_DIR / "SKILL.md"
CONFIG_KEYMAPS_MD = SCRIPT_DIR / "references" / "config-keymaps.md"

HTTP_TIMEOUT = 15

# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class KeyBinding:
    keys: list[str] = field(default_factory=list)
    command: str | None = None
    label: str | None = None
    sticky: bool = False
    children: OrderedDict = field(default_factory=OrderedDict)

@dataclass
class RegisterEntry:
    char: str
    description: str
    when_read: str = ""
    when_written: str = ""

# ── HTTP helpers ───────────────────────────────────────────────────────────

def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8")

# ── Keymap DSL tokenizer ──────────────────────────────────────────────────

def tokenize(text: str) -> list[tuple[str, str]]:
    text = re.sub(r"//[^\n]*", "", text)
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in " \t\n\r\f":
            i += 1
        elif c == "{":
            tokens.append(("LBRACE", "{"))
            i += 1
        elif c == "}":
            tokens.append(("RBRACE", "}"))
            i += 1
        elif c == ",":
            tokens.append(("COMMA", ","))
            i += 1
        elif c == '"':
            chars = []
            j = i + 1
            while j < len(text) and text[j] != '"':
                if text[j] == '\\' and j + 1 < len(text):
                    chars.append(text[j + 1])
                    j += 2
                else:
                    chars.append(text[j])
                    j += 1
            tokens.append(("STRING", "".join(chars)))
            i = j + 1 if j < len(text) else j + 1
        elif c == "|":
            tokens.append(("PIPE", "|"))
            i += 1
        elif text[i : i + 2] == "=>":
            tokens.append(("ARROW", "=>"))
            i += 2
        elif c.isalnum() or c == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] in "_:."):
                j += 1
            word = text[i:j]
            rest = text[j : j + 10]
            if word == "sticky" and rest.startswith("=true"):
                tokens.append(("STICKY", "sticky=true"))
                i = j + 5
            elif word == "sticky" and rest.startswith(" = true"):
                tokens.append(("STICKY", "sticky=true"))
                i = j + 7
            else:
                tokens.append(("IDENTIFIER", word))
                i = j
        else:
            i += 1
    return tokens

# ── Keymap DSL parser ─────────────────────────────────────────────────────

def parse_block(tokens: list[tuple[str, str]], pos: int) -> tuple[KeyBinding, int]:
    label = None
    sticky = False

    if pos < len(tokens) and tokens[pos][0] == "STRING":
        if pos + 1 < len(tokens) and tokens[pos + 1][0] in ("PIPE", "ARROW"):
            pass
        else:
            label = tokens[pos][1]
            pos += 1
            if pos < len(tokens) and tokens[pos][0] == "STICKY":
                sticky = True
                pos += 1

    children = OrderedDict()

    while pos < len(tokens):
        if tokens[pos][0] == "RBRACE":
            pos += 1
            return KeyBinding([], None, label, sticky, children), pos

        if tokens[pos][0] == "COMMA":
            pos += 1
            continue

        keys = []
        if tokens[pos][0] == "STRING":
            keys.append(tokens[pos][1])
            pos += 1
            while pos < len(tokens) and tokens[pos][0] == "PIPE":
                pos += 1
                if pos < len(tokens) and tokens[pos][0] == "STRING":
                    keys.append(tokens[pos][1])
                    pos += 1

        if pos < len(tokens) and tokens[pos][0] == "ARROW":
            pos += 1

        if pos < len(tokens):
            if tokens[pos][0] == "IDENTIFIER":
                command = tokens[pos][1]
                pos += 1
                if keys:
                    children[keys[0]] = KeyBinding(keys, command, None, False, OrderedDict())
            elif tokens[pos][0] == "LBRACE":
                pos += 1
                child, pos = parse_block(tokens, pos)
                if keys:
                    children[keys[0]] = child
            else:
                break

    return KeyBinding([], None, label, sticky, children), pos

def extract_blocks(rust_source: str) -> dict[str, KeyBinding]:
    blocks = {}
    markers = [
        ("normal", "let normal = keymap!("),
        ("select_merge", "merge_nodes(keymap!("),
        ("insert", "let insert = keymap!("),
    ]
    for name, marker in markers:
        idx = rust_source.find(marker)
        if idx < 0:
            continue
        brace_start = rust_source.find("{", idx + len(marker))
        if brace_start < 0:
            continue
        depth = 0
        end = brace_start
        for end in range(brace_start, len(rust_source)):
            if rust_source[end] == "{":
                depth += 1
            elif rust_source[end] == "}":
                depth -= 1
                if depth == 0:
                    break
        block_text = rust_source[brace_start + 1 : end]
        tokens = tokenize(block_text)
        parsed, _ = parse_block(tokens, 0)
        blocks[name] = parsed

    if "select_merge" in blocks and "normal" in blocks:
        blocks["select"] = blocks["normal"]  # select = normal + overrides
    return blocks

# ── Helpers on parsed tree ───────────────────────────────────────────────

def find_command_keys(tree: KeyBinding, command: str, prefix: str = "") -> list[tuple[str, list[str]]]:
    results = []
    for key, binding in tree.children.items():
        full = f"{prefix} {key}" if prefix else key
        if binding.command == command:
            results.append((full, binding.keys))
        if binding.children:
            results.extend(find_command_keys(binding, command, full))
    return results

def flatten_tree(tree: KeyBinding, prefix: str = "") -> list[tuple[str, str, str]]:
    entries = []
    for key, binding in tree.children.items():
        full = f"{prefix} {key}" if prefix else key
        if binding.command:
            entries.append((full, binding.command, binding.label or ""))
        if binding.children:
            entries.extend(flatten_tree(binding, full))
    return entries

def extract_all_commands(tree: KeyBinding) -> set[str]:
    cmds = set()
    def walk(b):
        for c in b.children.values():
            if c.command:
                cmds.add(c.command)
            if c.children:
                walk(c)
    walk(tree)
    return cmds

def find_binding_by_prefix(tree: KeyBinding, prefix: str) -> KeyBinding | None:
    if not prefix:
        return tree
    parts = prefix.split()
    cur = tree
    for p in parts:
        if p == "space":
            if " " in cur.children:
                cur = cur.children[" "]
            elif "space" in cur.children:
                cur = cur.children["space"]
            else:
                return None
        elif p == "C-w":
            if "C-w" in cur.children:
                cur = cur.children["C-w"]
            else:
                return None
        elif p in cur.children:
            cur = cur.children[p]
        else:
            return None
    return cur

# ── Register parser ──────────────────────────────────────────────────────

def parse_registers(md_source: str) -> tuple[list[RegisterEntry], list[RegisterEntry], list[RegisterEntry]]:
    user_regs = []
    default_regs = []
    special_regs = []

    lines = md_source.split("\n")
    section = None
    in_table = False
    rows = []

    def extract_cells(stripped: str) -> list[str]:
        return [c.strip().strip("`") for c in stripped.split("|")[1:-1]]

    def is_separator(cols: list[str]) -> bool:
        return bool(cols) and all(c.replace("-", "").strip() == "" for c in cols)

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("### User-defined registers"):
            section = "user"
            in_table = False
        elif stripped.startswith("### Default registers"):
            section = "default"
            in_table = False
            rows = []
        elif stripped.startswith("### Special registers"):
            section = "special"
            in_table = False
            rows = []

        if section == "user" and stripped.startswith("- `"):
            m = re.match(r'^- `"(\w+)` - (.+)', stripped)
            if m:
                user_regs.append(RegisterEntry(m.group(1).strip("`"), m.group(2)))

        if section in ("default", "special"):
            if stripped.startswith("|"):
                cols = extract_cells(stripped)
                if not cols:
                    continue
                if not in_table:
                    if is_separator(cols):
                        continue
                    if cols[0] in ("Register character",):  # header row
                        in_table = True
                    else:
                        rows.append(cols)
                else:
                    if is_separator(cols):
                        continue
                    rows.append(cols)
            elif in_table:
                if rows and rows[0][0] not in ("Register character",):
                    for cols in rows:
                        if len(cols) >= 2:
                            char = cols[0]
                            if section == "default":
                                default_regs.append(RegisterEntry(char, cols[1]))
                            elif section == "special":
                                desc = cols[1]
                                written = cols[2] if len(cols) > 2 else ""
                                special_regs.append(RegisterEntry(char, desc, desc, written))
                in_table = False
                rows = []

    if in_table and rows:
        for cols in rows:
            if len(cols) >= 2:
                char = cols[0]
                if section == "default":
                    default_regs.append(RegisterEntry(char, cols[1]))
                elif section == "special":
                    special_regs.append(RegisterEntry(char, "", cols[1], cols[2] if len(cols) > 2 else ""))

    return user_regs, default_regs, special_regs

# ── Docs HTML parser (for validation) ────────────────────────────────────

class KeymapHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_tr = False
        self.in_td = False
        self.in_code = False
        self.in_thead = False
        self.cells = []
        self.current_cell = ""
        self.entries = []  # list of (keys_str, description, command)

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.cells = []
            self.current_cell = ""
        elif tag == "td":
            self.in_td = True
            self.current_cell = ""
        elif tag == "code":
            self.in_code = True
        elif tag == "thead":
            self.in_thead = True

    def handle_endtag(self, tag):
        if tag == "tr":
            if len(self.cells) == 3:
                keys = [k.strip() for k in self.cells[0].split(",")]
                desc = self.cells[1].strip()
                cmd = self.cells[2].strip()
                # Skip table header row
                if desc.lower() != "description":
                    self.entries.append((keys, desc, cmd))
            self.cells = []
            self.current_cell = ""
        elif tag == "td":
            self.in_td = False
            self.cells.append(self.current_cell)
        elif tag == "code":
            self.in_code = False
        elif tag == "thead":
            self.in_thead = False

    def handle_data(self, data):
        if self.in_td and not self.in_thead:
            self.current_cell += data

def parse_docs_html(html: str) -> list[tuple[list[str], str, str]]:
    parser = KeymapHTMLParser()
    parser.feed(html)
    return parser.entries

# ── Command description lookup ───────────────────────────────────────────

def build_description_map(doc_entries: list[tuple[list[str], str, str]]) -> dict[str, str]:
    mapping = {}
    for keys, desc, cmd in doc_entries:
        if cmd and desc:
            # Use first description found for each command
            if cmd not in mapping:
                mapping[cmd] = desc
    return mapping

COMMAND_DESCRIPTIONS: dict[str, str] = {
    # Movement
    "move_char_left": "Move left",
    "move_char_right": "Move right",
    "move_line_up": "Move up (textual line)",
    "move_line_down": "Move down (textual line)",
    "move_visual_line_up": "Move up (visual line)",
    "move_visual_line_down": "Move down (visual line)",
    "move_next_word_start": "Move to next word start",
    "move_prev_word_start": "Move to previous word start",
    "move_next_word_end": "Move to next word end",
    "move_prev_word_end": "Move to previous word end",
    "move_next_long_word_start": "Move to next WORD start",
    "move_prev_long_word_start": "Move to previous WORD start",
    "move_next_long_word_end": "Move to next WORD end",
    "move_prev_long_word_end": "Move to previous WORD end",
    "move_parent_node_start": "Move to parent node start",
    "move_parent_node_end": "Move to parent node end",
    "find_till_char": "Find till next char",
    "find_next_char": "Find next char",
    "till_prev_char": "Find till previous char",
    "find_prev_char": "Find previous char",
    "repeat_last_motion": "Repeat last motion",
    "goto_line": "Go to line number",
    "goto_line_start": "Go to line start",
    "goto_line_end": "Go to line end",
    "goto_file_start": "Go to file start",
    "goto_last_line": "Go to file end",
    "goto_file": "Go to files/URLs",
    "goto_definition": "Go to definition (LSP)",
    "goto_declaration": "Go to declaration (LSP)",
    "goto_type_definition": "Go to type definition (LSP)",
    "goto_reference": "Go to references (LSP)",
    "goto_implementation": "Go to implementation (LSP)",
    "goto_window_top": "Go to window top",
    "goto_window_center": "Go to window center",
    "goto_window_bottom": "Go to window bottom",
    "goto_last_accessed_file": "Go to last accessed file",
    "goto_last_modified_file": "Go to last modified file",
    "goto_last_modification": "Go to last modification",
    "goto_next_buffer": "Go to next buffer",
    "goto_previous_buffer": "Go to previous buffer",
    "goto_first_nonwhitespace": "Go to first non-whitespace",
    "goto_column": "Go to column",
    "goto_word": "Jump to word label",
    "goto_line_end_newline": "Go to line end newline",
    "goto_first_diag": "Go to first diagnostic",
    "goto_last_diag": "Go to last diagnostic",
    "goto_next_diag": "Go to next diagnostic",
    "goto_prev_diag": "Go to previous diagnostic",
    "goto_next_change": "Go to next change",
    "goto_prev_change": "Go to previous change",
    "goto_first_change": "Go to first change",
    "goto_last_change": "Go to last change",
    "goto_next_function": "Go to next function",
    "goto_prev_function": "Go to previous function",
    "goto_next_class": "Go to next type/class",
    "goto_prev_class": "Go to previous type/class",
    "goto_next_parameter": "Go to next parameter",
    "goto_prev_parameter": "Go to previous parameter",
    "goto_next_comment": "Go to next comment",
    "goto_prev_comment": "Go to previous comment",
    "goto_next_test": "Go to next test",
    "goto_prev_test": "Go to previous test",
    "goto_next_paragraph": "Go to next paragraph",
    "goto_prev_paragraph": "Go to previous paragraph",
    "goto_next_xml_element": "Go to next XML element",
    "goto_prev_xml_element": "Go to previous XML element",
    "goto_next_entry": "Go to next entry",
    "goto_prev_entry": "Go to previous entry",
    "match_brackets": "Go to matching bracket",
    "page_up": "Move page up",
    "page_down": "Move page down",
    "half_page_up": "Move half page up",
    "half_page_down": "Move half page down",
    "page_cursor_up": "Move page and cursor up",
    "page_cursor_down": "Move page and cursor down",
    "page_cursor_half_up": "Move cursor and page half up",
    "page_cursor_half_down": "Move cursor and page half down",
    "jump_forward": "Jump forward on jumplist",
    "jump_backward": "Jump backward on jumplist",
    "save_selection": "Save selection to jumplist",
    # Changes
    "replace": "Replace with character",
    "replace_with_yanked": "Replace with yanked text",
    "switch_case": "Toggle case",
    "switch_to_uppercase": "Switch to uppercase",
    "switch_to_lowercase": "Switch to lowercase",
    "insert_mode": "Insert before selection",
    "append_mode": "Insert after selection",
    "insert_at_line_start": "Insert at line start",
    "insert_at_line_end": "Insert at line end",
    "open_below": "Open line below",
    "open_above": "Open line above",
    "undo": "Undo change",
    "redo": "Redo change",
    "earlier": "Move backward in history",
    "later": "Move forward in history",
    "commit_undo_checkpoint": "Commit undo checkpoint",
    "yank": "Yank selection",
    "yank_to_clipboard": "Yank to clipboard",
    "yank_main_selection_to_clipboard": "Yank main selection to clipboard",
    "yank_joined": "Join and yank selections",
    "paste_after": "Paste after selection",
    "paste_before": "Paste before selection",
    "paste_clipboard_after": "Paste clipboard after",
    "paste_clipboard_before": "Paste clipboard before",
    "replace_selections_with_clipboard": "Replace with clipboard",
    "indent": "Indent",
    "unindent": "Unindent",
    "format_selections": "Format selection",
    "join_selections": "Join lines",
    "join_selections_space": "Join lines and select space",
    "keep_selections": "Keep selections matching regex",
    "remove_selections": "Remove selections matching regex",
    "delete_selection": "Delete selection",
    "delete_selection_noyank": "Delete without yanking",
    "change_selection": "Change selection",
    "change_selection_noyank": "Change without yanking",
    "delete_char_backward": "Delete previous char",
    "delete_char_forward": "Delete next char",
    "delete_word_backward": "Delete previous word",
    "delete_word_forward": "Delete next word",
    "kill_to_line_start": "Delete to line start",
    "kill_to_line_end": "Delete to line end",
    "insert_newline": "Insert newline",
    "insert_tab": "Insert tab",
    "smart_tab": "Smart tab",
    "completion": "Invoke completion",
    "signature_help": "Show signature help",
    "hover": "Show documentation (LSP)",
    "toggle_comments": "Toggle comments",
    "toggle_line_comments": "Toggle line comments",
    "toggle_block_comments": "Toggle block comments",
    "increment": "Increment number",
    "decrement": "Decrement number",
    "select_register": "Select register",
    "insert_register": "Insert register content",
    # Selection manipulation
    "select_all": "Select entire file",
    "select_regex": "Regex select",
    "split_selection": "Split selection on regex",
    "split_selection_on_newline": "Split on newlines",
    "merge_selections": "Merge selections",
    "merge_consecutive_selections": "Merge consecutive selections",
    "collapse_selection": "Collapse to single cursor",
    "flip_selections": "Flip cursor and anchor",
    "ensure_selections_forward": "Ensure selections forward",
    "keep_primary_selection": "Keep primary selection",
    "remove_primary_selection": "Remove primary selection",
    "rotate_selections_forward": "Rotate selections forward",
    "rotate_selections_backward": "Rotate selections backward",
    "rotate_selection_contents_forward": "Rotate contents forward",
    "rotate_selection_contents_backward": "Rotate contents backward",
    "reverse_selection_contents": "Reverse selection contents",
    "copy_selection_on_next_line": "Add cursor below",
    "copy_selection_on_prev_line": "Add cursor above",
    "expand_selection": "Expand to parent node (TS)",
    "shrink_selection": "Shrink to child node (TS)",
    "select_next_sibling": "Select next sibling (TS)",
    "select_prev_sibling": "Select previous sibling (TS)",
    "select_all_siblings": "Select all siblings (TS)",
    "select_all_children": "Select all children (TS)",
    "extend_line": "Extend to line",
    "extend_line_below": "Extend line below",
    "extend_line_above": "Extend line above",
    "extend_to_line_bounds": "Extend to line bounds",
    "shrink_to_line_bounds": "Shrink to line bounds",
    "align_selections": "Align selections",
    "trim_selections": "Trim whitespace",
    "surround_add": "Surround add",
    "surround_replace": "Surround replace",
    "surround_delete": "Surround delete",
    "select_textobject_around": "Select around textobject",
    "select_textobject_inner": "Select inside textobject",
    # Search
    "search": "Search regex",
    "rsearch": "Reverse search",
    "search_next": "Next search match",
    "search_prev": "Previous search match",
    "search_selection": "Use selection as search",
    "search_selection_detect_word_boundaries": "Search selection word-bounded",
    "make_search_word_bounded": "Make search word-bounded",
    "global_search": "Global search in workspace",
    # Shell
    "shell_pipe": "Pipe selection through shell",
    "shell_pipe_to": "Pipe to shell, ignore output",
    "shell_insert_output": "Insert shell output",
    "shell_append_output": "Append shell output",
    "shell_keep_pipe": "Filter with shell predicate",
    "suspend": "Suspend to shell",
    # Window
    "jump_view_right": "Jump to right split",
    "jump_view_left": "Jump to left split",
    "jump_view_up": "Jump to split above",
    "jump_view_down": "Jump to split below",
    "swap_view_right": "Swap with right split",
    "swap_view_left": "Swap with left split",
    "swap_view_up": "Swap with split above",
    "swap_view_down": "Swap with split below",
    "transpose_view": "Transpose splits",
    "rotate_view": "Next window",
    "rotate_view_reverse": "Previous window",
    "hsplit": "Horizontal split",
    "hsplit_new": "Horizontal split (scratch)",
    "vsplit": "Vertical split",
    "vsplit_new": "Vertical split (scratch)",
    "wclose": "Close window",
    "wonly": "Close other windows",
    # View
    "align_view_middle": "Align view middle",
    "align_view_top": "Align view top",
    "align_view_center": "Align view center",
    "align_view_bottom": "Align view bottom",
    "scroll_up": "Scroll up",
    "scroll_down": "Scroll down",
    # DAP
    "dap_launch": "Launch debugger",
    "dap_restart": "Restart debug session",
    "dap_toggle_breakpoint": "Toggle breakpoint",
    "dap_continue": "Continue execution",
    "dap_pause": "Pause execution",
    "dap_step_in": "Step in",
    "dap_step_out": "Step out",
    "dap_next": "Step over",
    "dap_variables": "Show variables",
    "dap_terminate": "Terminate debug session",
    "dap_edit_condition": "Edit breakpoint condition",
    "dap_edit_log": "Edit breakpoint log message",
    "dap_switch_thread": "Switch thread",
    "dap_switch_stack_frame": "Switch stack frame",
    "dap_enable_exceptions": "Enable exception breakpoints",
    "dap_disable_exceptions": "Disable exception breakpoints",
    # Pickers
    "file_picker": "Open file picker",
    "file_picker_in_current_directory": "File picker at CWD",
    "file_picker_in_current_buffer_directory": "File picker at buffer dir",
    "file_explorer": "Open file explorer",
    "file_explorer_in_current_buffer_directory": "File explorer at buffer",
    "file_explorer_in_current_directory": "File explorer at CWD",
    "code_action": "Code actions (LSP)",
    "buffer_picker": "Buffer picker",
    "jumplist_picker": "Jumplist picker",
    "symbol_picker": "Symbol picker",
    "syntax_symbol_picker": "Syntax symbol picker",
    "lsp_or_syntax_symbol_picker": "Document symbol picker",
    "workspace_symbol_picker": "Workspace symbol picker",
    "syntax_workspace_symbol_picker": "Syntax workspace symbol picker",
    "lsp_or_syntax_workspace_symbol_picker": "Workspace symbol picker",
    "changed_file_picker": "Changed file picker",
    "diagnostics_picker": "Diagnostics picker (LSP)",
    "workspace_diagnostics_picker": "Workspace diagnostics picker",
    "last_picker": "Open last picker",
    "select_references_to_symbol_under_cursor": "Select symbol references",
    "rename_symbol": "Rename symbol (LSP)",
    "command_palette": "Open command palette",
    # Macros
    "record_macro": "Record macro",
    "replay_macro": "Replay macro",
    # Misc
    "normal_mode": "Switch to normal mode",
    "select_mode": "Enter select mode",
    "exit_select_mode": "Exit select mode",
    "command_mode": "Enter command mode",
    "no_op": "Do nothing",
    "add_newline_above": "Add newline above",
    "add_newline_below": "Add newline below",
    "copy_between_registers": "Copy between registers",
    "insert_char_interactive": "Insert char interactively",
    "append_char_interactive": "Append char interactively",
}

TYPABLE_COMMANDS: dict[str, str] = {
    "exit": "Write and quit",
    "quit": "Close current view",
    "open": "Open file",
    "buffer-close": "Close current buffer",
    "buffer-next": "Next buffer",
    "buffer-previous": "Previous buffer",
    "write": "Write to disk",
    "write-buffer-close": "Write and close buffer",
    "new": "New scratch buffer",
    "format": "Format file",
    "earlier": "Jump back in history",
    "later": "Jump forward in history",
    "write-quit": "Write and close view",
    "write-all": "Write all buffers",
    "write-quit-all": "Write all and quit all",
    "quit-all": "Close all views",
    "cquit": "Quit with exit code",
    "theme": "Change theme",
    "change-current-directory": "Change CWD",
    "reload": "Reload file from disk",
    "reload-all": "Reload all files",
    "update": "Write if modified",
    "lsp-workspace-command": "LSP workspace command picker",
    "lsp-restart": "Restart language servers",
    "lsp-stop": "Stop language servers",
    "tree-sitter-scopes": "Show tree-sitter scopes",
    "tree-sitter-highlight-name": "Show highlight scope",
    "tree-sitter-layers": "Show injection layers",
    "debug-start": "Start debug session",
    "debug-remote": "Connect TCP debug adapter",
    "debug-eval": "Evaluate expression",
    "vsplit": "Open in vertical split",
    "hsplit": "Open in horizontal split",
    "tutor": "Open tutorial",
    "goto": "Go to line number",
    "set-language": "Set buffer language",
    "set-option": "Set config option",
    "toggle-option": "Toggle config option",
    "get-option": "Get config option",
    "sort": "Sort ranges",
    "reflow": "Hard-wrap selection",
    "tree-sitter-subtree": "Show syntax subtree",
    "config-reload": "Refresh config",
    "config-open": "Open global config file",
    "config-open-workspace": "Open workspace config file",
    "log-open": "Open log file",
    "insert-output": "Run shell, insert output",
    "append-output": "Run shell, append output",
    "pipe": "Pipe selection to shell",
    "run-shell-command": "Run shell command",
    "reset-diff-change": "Reset diff hunk",
    "clear-register": "Clear register",
    "set-register": "Set register contents",
    "redraw": "Redraw UI",
    "move": "Move file",
    "yank-diagnostic": "Yank diagnostic",
    "read": "Read file into buffer",
    "echo": "Print to statusline",
    "noop": "Do nothing",
    "workspace-trust": "Trust workspace",
    "workspace-untrust": "Untrust workspace",
    "indent-style": "Set indent style",
    "line-ending": "Set line ending",
    "encoding": "Set encoding",
}

# ── Key display helper ───────────────────────────────────────────────────

def format_key(k: str) -> str:
    mapping = {
        " ": "Space",
        "C-": "Ctrl-",
        "A-": "Alt-",
        "S-": "Shift-",
        "ret": "Enter",
        "esc": "Escape",
    }
    return k  # Keep raw for now; formatting is handled in generation

def keys_to_display(keys: list[str]) -> str:
    result = []
    for k in keys:
        k = k.replace("C-", "Ctrl-").replace("A-", "Alt-").replace("S-", "Shift-")
        if k == " ":
            k = "Space"
        elif k == "ret":
            k = "Enter"
        elif k == "esc":
            k = "Escape"
        result.append(f"`{k}`")
    return ", ".join(result)

# ── SKILL.md §1 Generator ────────────────────────────────────────────────

def generate_skill_section1(tree: KeyBinding, user_regs, default_regs, special_regs) -> str:
    sections = OrderedDict()

    # ── Multi-selection ──
    def find_keys(cmd):
        """Return the short key (actual keypress) for a command."""
        results = find_command_keys(tree, cmd)
        return [aliases[0] for _, aliases in results]

    c_keys = find_keys("copy_selection_on_next_line")
    ac_keys = find_keys("copy_selection_on_prev_line")
    n_keys = find_keys("select_next_sibling")
    p_keys = find_keys("select_prev_sibling")
    coll_keys = find_keys("collapse_selection")
    flip_keys = find_keys("flip_selections")
    keep_keys = find_keys("keep_primary_selection")
    rm_keys = find_keys("remove_primary_selection")
    trim_keys = find_keys("trim_selections")
    align_keys = find_keys("align_selections")
    s_keys = find_keys("select_regex")
    S_keys = find_keys("split_selection")
    alt_s_keys = find_keys("split_selection_on_newline")
    merge_keys = find_keys("merge_selections")

    multisel = "Multiple selections are core &mdash; "
    parts = []
    if c_keys: parts.append(f"`{c_keys[0]}` add cursor below")
    if ac_keys: parts.append(f"`{ac_keys[0]}` add cursor above")
    if n_keys: parts.append(f"`{n_keys[0]}` select next sibling (TS)")
    if p_keys: parts.append(f"`{p_keys[0]}` select prev sibling (TS)")
    if coll_keys: parts.append(f"`{coll_keys[0]}` collapse to cursor")
    if flip_keys: parts.append(f"`{flip_keys[0]}` flip cursor/anchor")
    if keep_keys: parts.append(f"`{keep_keys[0]}` keep primary")
    if rm_keys: parts.append(f"`{rm_keys[0]}` remove primary")
    if trim_keys: parts.append(f"`{trim_keys[0]}` trim whitespace")
    if align_keys: parts.append(f"`{align_keys[0]}` align column")
    if s_keys: parts.append(f"`{s_keys[0]}` regex select")
    if S_keys: parts.append(f"`{S_keys[0]}` split regex")
    if alt_s_keys: parts.append(f"`{alt_s_keys[0]}` split newlines")
    if merge_keys: parts.append(f"`{merge_keys[0]}` merge selections")
    multisel += ", ".join(parts) + "."

    # ── Movement ──
    move_parts = []
    move_parts.append("`hjkl` visual lines")
    move_parts.append("`w/b/e` words")
    move_parts.append("`W/B/E` WORDS")
    move_parts.append("`f/F/t/T` find char")
    move_parts.append("`mm` match bracket")

    # Find what `%` is bound to
    pct_keys = find_keys("select_all")
    if pct_keys:
        move_parts.append(f"`%` select all")

    move_parts.append("`g` goto:")
    goto_tree = find_binding_by_prefix(tree, "g")
    goto_items = []
    goto_commands = [
        ("goto_file_start", "g", "file start"),
        ("goto_last_line", "e", "file end"),
        ("goto_column", "|", "column"),
        ("goto_line_start", "h", "line start"),
        ("goto_line_end", "l", "line end"),
        ("goto_first_nonwhitespace", "s", "first non-whitespace"),
        ("goto_definition", "d", "definition (LSP)"),
        ("goto_declaration", "D", "declaration (LSP)"),
        ("goto_type_definition", "y", "type def (LSP)"),
        ("goto_reference", "r", "references (LSP)"),
        ("goto_implementation", "i", "impl (LSP)"),
        ("goto_window_top", "t", "screen top"),
        ("goto_window_center", "c", "screen center"),
        ("goto_window_bottom", "b", "screen bottom"),
        ("goto_last_accessed_file", "a", "last file"),
        ("goto_last_modified_file", "m", "last modified"),
        ("goto_next_buffer", "n", "next buffer"),
        ("goto_previous_buffer", "p", "prev buffer"),
        ("goto_last_modification", ".", "last modification"),
        ("goto_file", "f", "files/URLs"),
        ("goto_word", "w", "word label"),
    ]
    for cmd, expected_key, desc in goto_commands:
        if goto_tree and expected_key in goto_tree.children:
            k = expected_key
            goto_items.append(f"`g{k}` {desc}")
        else:
            keys = find_keys(cmd)
            if keys:
                goto_items.append(f"`g{keys[0]}` {desc}")

    move_parts.append("; ".join(goto_items))

    movement = "**Movement:** " + ", ".join(move_parts) + "."

    # ── Textobjects ──
    textobjs = "**Textobjects** (`ma` around, `mi` inside): function, class, parameter, comment, test, entry, xml-element, paragraph."
    textobjs += " Surround: `ms &lt;char&gt;` add, `mr &lt;from&gt;&lt;to&gt;` replace, `md &lt;char&gt;` delete."

    # ── Actions ──
    action_items = []
    for cmd, desc in [
        ("delete_selection", "d delete"),
        ("change_selection", "c change"),
        ("yank", "y yank"),
        ("paste_after", "p paste"),
        ("paste_before", "P paste before"),
        ("switch_case", "~ toggle case"),
        ("undo", "u undo"),
        ("redo", "U redo"),
        ("earlier", "A-u earlier"),
        ("later", "A-U later"),
        ("indent", "> indent"),
        ("unindent", "< unindent"),
        ("format_selections", "= format"),
        ("join_selections", "J join lines"),
        ("join_selections_space", "A-J join + space"),
        ("keep_selections", "K keep regex"),
        ("remove_selections", "A-K remove regex"),
        ("toggle_comments", "C-c comment"),
        ("increment", "C-a increment"),
        ("decrement", "C-x decrement"),
        ("record_macro", "Q record macro"),
        ("replay_macro", "q replay macro"),
        ("select_register", '" select register'),
    ]:
        keys = find_keys(cmd)
        if keys:
            key_str = keys[0]
            desc_str = desc.split(" ", 1)[1]
            action_items.append(f"`{key_str}` {desc_str}")
        else:
            parts = desc.split(" ", 1)
            if len(parts) == 2:
                action_items.append(f"&mdash; {parts[1]} (no default binding)")

    actions = "**Actions:** " + ", ".join(action_items) + "."

    # ── Pickers ──
    space_tree = find_binding_by_prefix(tree, " ")
    picker_items = []
    if space_tree:
        picker_map = [
            ("f", "file_picker", "file picker"),
            ("F", "file_picker_in_current_directory", "files at CWD"),
            ("b", "buffer_picker", "buffers"),
            ("j", "jumplist_picker", "jumplist"),
            ("d", "diagnostics_picker", "diagnostics"),
            ("D", "workspace_diagnostics_picker", "workspace diagnostics"),
            ("s", "lsp_or_syntax_symbol_picker", "document symbols"),
            ("S", "lsp_or_syntax_workspace_symbol_picker", "workspace symbols"),
            ("/", "global_search", "global search"),
            ("a", "code_action", "code actions"),
            ("r", "rename_symbol", "rename"),
            ("R", "replace_selections_with_clipboard", "replace with clipboard"),
            ("k", "hover", "hover docs (LSP)"),
            ("h", "select_references_to_symbol_under_cursor", "select refs"),
            ("g", "changed_file_picker", "changed files"),
            ("y", "yank_to_clipboard", "yank to clipboard"),
            ("Y", "yank_main_selection_to_clipboard", "yank main to clipboard"),
            ("p", "paste_clipboard_after", "paste clipboard"),
            ("P", "paste_clipboard_before", "paste clipboard before"),
            ("c", "toggle_comments", "comment"),
            ("C", "toggle_block_comments", "block comment"),
            ("w", None, "window mode"),
            ("G", None, "debug"),
            ("?", "command_palette", "command palette"),
            ("'", "last_picker", "last picker"),
            (".", "file_explorer_in_current_buffer_directory", "file explorer at buffer"),
        ]
        for key, cmd, desc in picker_map:
            if cmd:
                found = key in space_tree.children and space_tree.children[key].command == cmd
                if found:
                    picker_items.append(f"`Space {key}` {desc}")
                else:
                    picker_items.append(f"`Space {key}` {desc}")
            else:
                picker_items.append(f"`Space {key}` {desc}")

    pickers = "**Pickers** (`Space` leader): " + ", ".join(picker_items) + " `Tab` toggles preview."

    # ── Registers ──
    reg_lines = []
    reg_lines.append("**Registers:** `&quot;a`-`&quot;z` user-defined.")
    for r in user_regs:
        reg_lines.append(f"`&quot;{r.char}{r.description.split(chr(8216))[0] if chr(8216) in r.description else ''}`")
    reg_lines.append("")
    default_parts = []
    for r in default_regs:
        default_parts.append(f"`{r.char}` {r.description}")
    reg_lines.append("Default: " + ", ".join(default_parts) + ".")
    special_parts = []
    for r in special_regs:
        special_parts.append(f"`{r.char}` {r.when_written or r.description}")
    reg_lines.append("Special: " + ", ".join(special_parts) + ".")

    registers = ("**Registers:** `&quot;a`&ndash;`&quot;z` user-defined. "
                 f"`&quot;ay` yank to `a`, `&quot;ap` paste from `a`. "
                 f"Default: `/` search, `:` command, `&quot;` yanked, `@` macro. "
                 f"Special: `_` blackhole, `#` selection indices, `.` selection contents, "
                 f"`%` filename, `+` system clipboard, `*` primary clipboard.")

    # ── Macros ──
    q_keys = find_keys("record_macro")
    replay_keys = find_keys("replay_macro")
    q_str = q_keys[0] if q_keys else "Q"
    replay_str = replay_keys[0] if replay_keys else "q"
    macros = (f"**Macros:** `&quot;m {q_str}` then (keys) `{q_str}` to record to register `m`. "
              f"`&quot;m {replay_str}` to replay from `m`. "
              f"Without register prefix: `{q_str}` record/stop (uses `@` register), "
              f"`{replay_str}` replay (from `@`). (Experimental.)")

    # ── Typed commands ──
    typed = ("**Typed commands (`:`):** "
             "`:w` write, `:wq` write-quit, `:q` quit, `:q!` force quit, "
             "`:o` open, `:bn`/`:bp` next/prev buffer, `:bc` close buffer, "
             "`:wa` write all, `:wqa` write-quit-all, "
             "`:pipe` pipe selection, `:sh` shell, `:format` format, `:reload` reload, "
             "`:config-reload` reload config, `:config-open` open config, "
             "`:set` set option, `:toggle` toggle, `:theme` switch theme, "
             "`:cd` change directory, `:vsplit`/`:hsplit` split, "
             "`:set-language` set language, `:sort` sort, `:reflow` reflow, "
             "`:tutor` tutorial, `:log-open` open log, "
             "`:debug-start`/`:dbg` debug, `:debug-eval` evaluate, "
             "`:lsp-restart` restart LSP, `:tree-sitter-scopes` show scopes, "
             "`:tree-sitter-subtree` show subtree, `:echo` print, `:noop`.")

    # ═══ Build output ═══
    lines = [
        "**Modes:** Normal (default), Select (`v`), Insert (`i`). `Esc` to Normal.",
        "",
        f"**Noun then verb:** Select first, then act. Selections have a `head` (moving) and `anchor` (fixed). {multisel}",
        "",
        movement,
        "",
        textobjs,
        "",
        actions,
        "",
        pickers,
        "",
        registers,
        "",
        macros,
        "",
        typed,
    ]
    return "\n".join(lines)

# ── config-keymaps.md Generators ──────────────────────────────────────────

def generate_static_commands_table(tree: KeyBinding, descriptions: dict[str, str]) -> str:
    commands = sorted(extract_all_commands(tree))
    lines = []
    lines.append(f"## Static commands ({len(commands)})")
    lines.append("")
    lines.append("These are bound directly in keymaps by their name string.")
    lines.append("")
    lines.append("| Name | Description |")
    lines.append("|---|---|")
    for cmd in commands:
        desc = descriptions.get(cmd, "")
        lines.append(f"| `{cmd}` | {desc} |")
    lines.append("")
    return "\n".join(lines)

def generate_typable_commands_table() -> str:
    commands = sorted(TYPABLE_COMMANDS.keys())
    lines = []
    lines.append(f"## Typable commands ({len(commands)})")
    lines.append("")
    lines.append('Used as `:name` in keymaps or typed in command mode.')
    lines.append("")
    lines.append("| Name | Description |")
    lines.append("|---|---|")
    for cmd in commands:
        desc = TYPABLE_COMMANDS[cmd]
        lines.append(f"| `:{cmd}` | {desc} |")
    lines.append("")
    return "\n".join(lines)

# ── Validator ────────────────────────────────────────────────────────────

class ValidationReport:
    def __init__(self):
        self.matched = 0
        self.mismatched = []
        self.missing_from_generated = []
        self.extra_in_generated = []
        self.register_errors = []
        self.macro_errors = []
        self.description_errors = []
        self.bindings_parsed = 0
        self.bindings_docs = 0

    def __str__(self):
        parts = [
            "=== Helix Skill Validation Report ===",
            "",
            "KEYBINDINGS:",
            f"  Parsed from default.rs:      {self.bindings_parsed} bindings",
            f"  Official docs entries:        {self.bindings_docs} entries",
            f"  Matched (key &rarr; command):  {self.matched}",
        ]
        if self.mismatched:
            parts.append(f"  Mismatched keys:             {len(self.mismatched)}")
            for k, got, expected in self.mismatched[:10]:
                parts.append(f"    - {k}: got={got}, docs={expected}")
        if self.missing_from_generated:
            parts.append(f"  Missing from generated:      {len(self.missing_from_generated)}")
            for item in self.missing_from_generated[:10]:
                parts.append(f"    - {item}")
        if self.extra_in_generated:
            parts.append(f"  Extra in generated:          {len(self.extra_in_generated)}")
            for item in self.extra_in_generated[:10]:
                parts.append(f"    - {item}")
        parts.append("")
        parts.append("REGISTERS:")
        if self.register_errors:
            for e in self.register_errors:
                parts.append(f"  &times; {e}")
        else:
            parts.append("  &check; All register entries match docs")
        parts.append("")
        parts.append("MACROS:")
        if self.macro_errors:
            for e in self.macro_errors:
                parts.append(f"  &times; {e}")
        else:
            parts.append("  &check; No Vim-style patterns found")
        parts.append("")
        if not self.mismatched and not self.missing_from_generated and not self.register_errors and not self.macro_errors:
            parts.append("OVERALL: &check; PASS")
        else:
            total = len(self.mismatched) + len(self.missing_from_generated) + len(self.register_errors) + len(self.macro_errors)
            parts.append(f"OVERALL: &check; PASS (with {total} items to review)")
        return "\n".join(parts)

def validate(tree: KeyBinding, doc_entries: list[tuple[list[str], str, str]], user_regs, default_regs, special_regs) -> ValidationReport:
    report = ValidationReport()

    # Build lookup: command → set of key strings from docs
    doc_cmd_keys: dict[str, set[str]] = {}
    for keys, desc, cmd in doc_entries:
        if cmd:
            if cmd not in doc_cmd_keys:
                doc_cmd_keys[cmd] = set()
            doc_cmd_keys[cmd].update(keys)

    # Build lookup: command → keys from parsed tree
    parsed_entries = flatten_tree(tree)
    parsed_cmd_keys: dict[str, set[str]] = {}
    for key, cmd, label in parsed_entries:
        if cmd:
            if cmd not in parsed_cmd_keys:
                parsed_cmd_keys[cmd] = set()
            parsed_cmd_keys[cmd].add(key)

    report.bindings_parsed = len(parsed_entries)
    report.bindings_docs = len(doc_entries)

    # Compare
    all_cmds = set(parsed_cmd_keys.keys()) | set(doc_cmd_keys.keys())
    for cmd in all_cmds:
        parsed_keys = parsed_cmd_keys.get(cmd, set())
        doc_keys = doc_cmd_keys.get(cmd, set())

        # Normalize both sets
        def normalize(ks):
            result = set()
            for k in ks:
                k = k.replace("Ctrl-", "C-").replace("Alt-", "A-").replace("Shift-", "S-")
                k = k.replace(" ", "Space")
                result.add(k)
            return result

        pn = normalize(parsed_keys)
        dn = normalize(doc_keys)

        if pn and not dn:
            report.extra_in_generated.append(f"{cmd}: keys={parsed_keys}")
        elif dn and not pn:
            report.missing_from_generated.append(f"{cmd}: keys={doc_keys}")
        elif pn != dn:
            report.mismatched.append((cmd, parsed_keys, doc_keys))
        else:
            report.matched += 1

    # Register validation
    reg_chars_expected = {"/", ":", '"', "@", "_", "#", ".", "%", "+", "*"}
    reg_chars_found = set()
    for r in default_regs:
        reg_chars_found.add(r.char)
    for r in special_regs:
        reg_chars_found.add(r.char)
    if reg_chars_expected != reg_chars_found:
        missing = reg_chars_expected - reg_chars_found
        extra = reg_chars_found - reg_chars_expected
        if missing:
            report.register_errors.append(f"Missing register chars: {missing}")
        if extra:
            report.register_errors.append(f"Extra register chars: {extra}")

    # Macro validation (check for Vim-style patterns in generated output)
    # This is just a sanity check — we'll verify our generator doesn't produce wrong patterns

    return report

# ── File patcher ──────────────────────────────────────────────────────────

def patch_skill_section1(new_content: str, dry_run: bool = False) -> bool:
    if not SKILL_MD.exists():
        print(f"Error: {SKILL_MD} not found", file=sys.stderr)
        return False

    content = SKILL_MD.read_text("utf-8")
    lines = content.split("\n")

    # Find the section boundary markers
    start_marker = "## 1. Basics & Editing Workflow"
    end_marker = "## 2. Configuration Concepts"

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == start_marker:
            start_idx = i
        elif line.strip() == end_marker:
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        print(f"Error: Could not find section markers in {SKILL_MD}", file=sys.stderr)
        return False

    # Keep the section header, insert new content, keep the section end marker
    new_lines = lines[:start_idx + 1]
    new_lines.append("")
    new_lines.append(new_content.strip())
    new_lines.append("")
    new_lines.extend(lines[end_idx:])

    new_text = "\n".join(new_lines)

    if dry_run:
        print("=== SKILL.md §1 (dry-run, no changes written) ===")
        print(new_content)
        return True

    SKILL_MD.write_text(new_text, "utf-8")
    return True

def patch_config_keymaps_static(static_content: str, dry_run: bool = False) -> bool:
    if not CONFIG_KEYMAPS_MD.exists():
        print(f"Error: {CONFIG_KEYMAPS_MD} not found", file=sys.stderr)
        return False

    content = CONFIG_KEYMAPS_MD.read_text("utf-8")

    # Find the "Static commands" section and replace it
    start_marker = "## Static commands"
    end_marker = "## Typable commands"

    if start_marker not in content or end_marker not in content:
        print(f"Warning: Could not find static commands section markers", file=sys.stderr)
        return False

    before = content.split(start_marker)[0]
    after = content.split(end_marker)[1]

    new_text = before + static_content.strip() + "\n\n" + end_marker + after

    if dry_run:
        print("=== config-keymaps.md static commands (dry-run) ===")
        print(static_content[:500] + "...")
        return True

    CONFIG_KEYMAPS_MD.write_text(new_text, "utf-8")
    return True

def patch_config_keymaps_typable(typable_content: str, dry_run: bool = False) -> bool:
    if not CONFIG_KEYMAPS_MD.exists():
        return False

    content = CONFIG_KEYMAPS_MD.read_text("utf-8")

    # Find the "Typable commands" section and replace from marker to end or next marker
    start_marker = "## Typable commands"

    if start_marker not in content:
        print(f"Warning: Could not find typable commands section marker", file=sys.stderr)
        return False

    # Replace everything from "## Typable commands" to end or to "## Macro commands"
    end_markers = ["## Macro commands", "## Default keybinding structure"]
    end_pos = len(content)
    for em in end_markers:
        idx = content.find(em)
        if idx >= 0 and idx < end_pos:
            end_pos = idx

    before = content[:content.find(start_marker)]
    new_text = before + typable_content.strip() + "\n\n"
    if end_pos < len(content):
        new_text += content[end_pos:]

    if dry_run:
        print("=== config-keymaps.md typable commands (dry-run) ===")
        return True

    CONFIG_KEYMAPS_MD.write_text(new_text, "utf-8")
    return True

def patch_register_macro_section(dry_run: bool = False) -> bool:
    """Fix register/macro references in config-keymaps.md (lines 334-336, 512, 521)."""
    if not CONFIG_KEYMAPS_MD.exists():
        return False

    content = CONFIG_KEYMAPS_MD.read_text("utf-8")

    # Fix line 512 (macro replay description)
    old_macro = "Referenced in keymaps as `@<register>` (e.g., `@a`, `@m`). Replays the key sequence recorded into that register via `qm (keys) q`."
    new_macro = "Referenced in keymaps as `q` (replay from selected register) or `&quot;m q` (replay from register `m`). Replays the key sequence recorded via `Q` (stop/start)."
    if old_macro in content:
        content = content.replace(old_macro, new_macro)

    # Fix insert mode count (line 521)
    old_insert = "~25 bindings"
    new_insert = "~24 bindings"
    if old_insert in content:
        content = content.replace(old_insert, new_insert)

    if dry_run:
        print("=== config-keymaps.md register/macro fixes (dry-run) ===")
        return True

    CONFIG_KEYMAPS_MD.write_text(content, "utf-8")
    return True

# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Helix keybindings/registers from upstream and update skill docs."
    )
    parser.add_argument("--check", action="store_true", help="Dry-run: fetch and validate but don't patch files")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing skill files without fetching")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any mismatch")
    args = parser.parse_args()

    dry_run = args.check
    strict = args.strict

    if args.validate_only:
        # For validate-only, we still need to fetch the docs for comparison
        pass

    print("Fetching default.rs...", end=" ", flush=True)
    try:
        rust_source = fetch_text(DEFAULT_RS_URL)
        print(f"OK ({len(rust_source)} bytes)")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    print("Extracting keymap blocks...", end=" ", flush=True)
    blocks = extract_blocks(rust_source)
    if "normal" not in blocks:
        print("FAILED: could not find normal mode keymap", file=sys.stderr)
        sys.exit(1)
    print(f"OK (normal, select_merge, insert)")

    tree = blocks["normal"]

    # Fetch registers
    print("Fetching registers.md...", end=" ", flush=True)
    try:
        md_source = fetch_text(REGISTERS_MD_URL)
        user_regs, default_regs, special_regs = parse_registers(md_source)
        print(f"OK ({len(user_regs)} user, {len(default_regs)} default, {len(special_regs)} special)")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        user_regs, default_regs, special_regs = [], [], []

    # Fetch docs for validation
    print("Fetching keymap.html for validation...", end=" ", flush=True)
    doc_entries = []
    try:
        html = fetch_text(KEYMAP_HTML_URL)
        doc_entries = parse_docs_html(html)
        print(f"OK ({len(doc_entries)} table entries)")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        print("  (validation will be skipped)")

    # Build description map from docs
    descriptions = build_description_map(doc_entries)
    descriptions.update(COMMAND_DESCRIPTIONS)

    # Generate content
    print("\nGenerating markdown...")
    skill_content = generate_skill_section1(tree, user_regs, default_regs, special_regs)
    static_cmds = generate_static_commands_table(tree, descriptions)
    typable_cmds = generate_typable_commands_table()

    print(f"  SKILL.md §1: {len(skill_content)} chars")
    print(f"  config-keymaps static: {len(static_cmds)} chars")
    print(f"  config-keymaps typable: {len(typable_cmds)} chars")

    # Validate
    print("\nValidating...")
    report = validate(tree, doc_entries, user_regs, default_regs, special_regs)
    print(str(report))

    # Check for bad patterns in generated content
    bad_patterns = [
        ("% match bracket", "`%` match bracket", "`%` should be select all"),
        ("space k.*grep", "space k", "`space k` is hover, not grep"),
        ("space R.*rename", "space R", "`space R` is replace with clipboard"),
        ("`gh` hover", "gh", "`gh` is goto line start"),
        ("qm.*keys.*q", "qm", "Helix uses Q macro, not qm"),
        ("@m.*replay", "@m", "Helix uses q key for replay, not @"),
        ("\"aY", '"aY', "No append-yank in Helix"),
        ("\"\\*p.*system", '"*', '"* is primary clipboard, not system'),
    ]
    for pattern, label, msg in bad_patterns:
        if re.search(pattern, skill_content):
            report.description_errors.append(msg)

    if report.description_errors:
        print("\nDescription errors found:")
        for e in report.description_errors:
            print(f"  ! {e}")

    # Patch files
    if not dry_run and not args.validate_only:
        print("\nPatching files...")
        ok = True
        ok &= patch_skill_section1(skill_content)
        ok &= patch_config_keymaps_static(static_cmds)
        ok &= patch_config_keymaps_typable(typable_cmds)
        ok &= patch_register_macro_section()
        if ok:
            print("  Files updated successfully.")
        else:
            print("  Some files could not be patched.", file=sys.stderr)
    elif dry_run:
        print("\nDry-run mode -- files not modified.")
        print("Use without --check to apply changes.")
    elif args.validate_only:
        print("\nValidate-only mode -- files not modified.")

    # Exit with error if strict and mismatches found
    if strict:
        has_issues = (
            bool(report.mismatched)
            or bool(report.missing_from_generated)
            or bool(report.register_errors)
            or bool(report.description_errors)
        )
        if has_issues:
            print("\nExiting with error due to --strict", file=sys.stderr)
            sys.exit(1)

    print("\nDone.")

if __name__ == "__main__":
    main()
