# `[keys.*]` Configuration Reference

Complete reference for keymap configuration, key event format, and all available commands.

---

## Key event format

```
[Modifier-]KeyCode
```

**Modifiers** (prefix, case-sensitive):
| Prefix | Key |
|---|---|
| `C-` | Ctrl |
| `A-` | Alt |
| `S-` | Shift |
| `Meta-` / `Cmd-` / `Win-` | Super/Command/Windows |

**Single characters** (e.g. `"w"`, `"g"`, `"a"`, `"$"`, `"+"`) resolve to `KeyCode::Char(c)`.

**Named key codes:**

| String | Key | String | Key |
|---|---|---|---|
| `esc` | Escape | `backspace` | Backspace |
| `ret` / `enter` | Enter | `tab` | Tab |
| `space` | Space | `del` | Delete |
| `ins` | Insert | `home` | Home |
| `end` | End | `pageup` | Page Up |
| `pagedown` | Page Down | `up` / `down` / `left` / `right` | Arrows |
| `minus` | `-` | `lt` | `<` |
| `gt` | `>` | `null` | Null |
| `capslock` | CapsLock | `scrolllock` | ScrollLock |
| `numlock` | NumLock | `printscreen` | PrintScreen |
| `pause` | Pause | `menu` | Menu |
| `keypadbegin` | KeypadBegin | | |
| `F1` .. `F24` | Function keys | | |

**Media keys:** `play`, `pausemedia`, `playpause`, `stop`, `reverse`, `fastforward`, `rewind`, `tracknext`, `trackprevious`, `record`, `lowervolume`, `raisevolume`, `mutevolume`

**Modifier keys (for mapping to):** `leftshift`, `leftcontrol`, `leftalt`, `leftsuper`, `lefthyper`, `leftmeta`, `rightshift`, `rightcontrol`, `rightalt`, `rightsuper`, `righthyper`, `rightmeta`, `isolevel3shift`, `isolevel5shift`

---

## Binding value types

```toml
[keys.normal]
# Single command
"j" = "move_visual_line_down"

# Command sequence (executed in order)
"+" = ["select_all", "shell_pipe", "format"]

# Sub-keymap node (nested bindings)
"g" = { "g" = "goto_file_start", "e" = "goto_last_line", "$" = "goto_line_end" }

# Override an existing sub-keymap entirely
"space" = "no_op"  # replaces whole picker menu
```

Modes: `[keys.normal]`, `[keys.select]`, `[keys.insert]`.

---

## Merge behavior

User keymaps merge into defaults with these rules:
- **Leaf replaces leaf** — user binds `"y"` to `"move_line_down"`, yank is replaced
- **Leaf replaces node** — user binds `"space"` to `"no_op"`, entire picker sub-keymap replaced
- **Node merges into node** — user defines `"g" = { "$" = "goto_line_end" }`, `$` is added to goto menu, existing `g` bindings preserved
- **New keys** — any key not in defaults is added

Default keymap source: `helix-term/src/keymap/default.rs`

---

## Static commands (223)

These are bound directly in keymaps by their name string.

| Name | Description |
|---|---|
| `add_newline_above` | Add newline above |
| `add_newline_below` | Add newline below |
| `align_selections` | Align selections |
| `align_view_bottom` | Align view bottom |
| `align_view_center` | Align view center |
| `align_view_middle` | Align view middle |
| `align_view_top` | Align view top |
| `append_mode` | Insert after selection |
| `buffer_picker` | Buffer picker |
| `change_selection` | Change selection |
| `change_selection_noyank` | Change without yanking |
| `changed_file_picker` | Changed file picker |
| `code_action` | Code actions (LSP) |
| `collapse_selection` | Collapse to single cursor |
| `command_mode` | Enter command mode |
| `command_palette` | Open command palette |
| `copy_selection_on_next_line` | Add cursor below |
| `copy_selection_on_prev_line` | Add cursor above |
| `dap_continue` | Continue execution |
| `dap_disable_exceptions` | Disable exception breakpoints |
| `dap_edit_condition` | Edit breakpoint condition |
| `dap_edit_log` | Edit breakpoint log message |
| `dap_enable_exceptions` | Enable exception breakpoints |
| `dap_launch` | Launch debugger |
| `dap_next` | Step over |
| `dap_pause` | Pause execution |
| `dap_restart` | Restart debug session |
| `dap_step_in` | Step in |
| `dap_step_out` | Step out |
| `dap_switch_stack_frame` | Switch stack frame |
| `dap_switch_thread` | Switch thread |
| `dap_terminate` | Terminate debug session |
| `dap_toggle_breakpoint` | Toggle breakpoint |
| `dap_variables` | Show variables |
| `decrement` | Decrement number |
| `delete_selection` | Delete selection |
| `delete_selection_noyank` | Delete without yanking |
| `diagnostics_picker` | Diagnostics picker (LSP) |
| `earlier` | Move backward in history |
| `ensure_selections_forward` | Ensure selections forward |
| `expand_selection` | Expand to parent node (TS) |
| `extend_line_below` | Extend line below |
| `extend_to_line_bounds` | Extend to line bounds |
| `file_explorer` | Open file explorer |
| `file_explorer_in_current_buffer_directory` | File explorer at buffer |
| `file_picker` | Open file picker |
| `file_picker_in_current_directory` | File picker at CWD |
| `find_next_char` | Find next char |
| `find_prev_char` | Find previous char |
| `find_till_char` | Find till next char |
| `flip_selections` | Flip cursor and anchor |
| `format_selections` | Format selection |
| `global_search` | Global search in workspace |
| `goto_column` | Go to column |
| `goto_declaration` | Go to declaration (LSP) |
| `goto_definition` | Go to definition (LSP) |
| `goto_file` | Go to files/URLs |
| `goto_file_hsplit` |  |
| `goto_file_start` | Go to file start |
| `goto_file_vsplit` |  |
| `goto_first_change` | Go to first change |
| `goto_first_diag` | Go to first diagnostic |
| `goto_first_nonwhitespace` | Go to first non-whitespace |
| `goto_implementation` | Go to implementation (LSP) |
| `goto_last_accessed_file` | Go to last accessed file |
| `goto_last_change` | Go to last change |
| `goto_last_diag` | Go to last diagnostic |
| `goto_last_line` | Go to file end |
| `goto_last_modification` | Go to last modification |
| `goto_last_modified_file` | Go to last modified file |
| `goto_line` | Go to line number |
| `goto_line_end` | Go to line end |
| `goto_line_start` | Go to line start |
| `goto_next_buffer` | Go to next buffer |
| `goto_next_change` | Go to next change |
| `goto_next_class` | Go to next type/class |
| `goto_next_comment` | Go to next comment |
| `goto_next_diag` | Go to next diagnostic |
| `goto_next_entry` | Go to next entry |
| `goto_next_function` | Go to next function |
| `goto_next_paragraph` | Go to next paragraph |
| `goto_next_parameter` | Go to next parameter |
| `goto_next_test` | Go to next test |
| `goto_next_xml_element` | Go to next XML element |
| `goto_prev_change` | Go to previous change |
| `goto_prev_class` | Go to previous type/class |
| `goto_prev_comment` | Go to previous comment |
| `goto_prev_diag` | Go to previous diagnostic |
| `goto_prev_entry` | Go to previous entry |
| `goto_prev_function` | Go to previous function |
| `goto_prev_paragraph` | Go to previous paragraph |
| `goto_prev_parameter` | Go to previous parameter |
| `goto_prev_test` | Go to previous test |
| `goto_prev_xml_element` | Go to previous XML element |
| `goto_previous_buffer` | Go to previous buffer |
| `goto_reference` | Go to references (LSP) |
| `goto_type_definition` | Go to type definition (LSP) |
| `goto_window_bottom` | Go to window bottom |
| `goto_window_center` | Go to window center |
| `goto_window_top` | Go to window top |
| `goto_word` | Jump to word label |
| `hover` | Show documentation (LSP) |
| `hsplit` | Horizontal split |
| `hsplit_new` | Horizontal split (scratch) |
| `increment` | Increment number |
| `indent` | Indent |
| `insert_at_line_end` | Insert at line end |
| `insert_at_line_start` | Insert at line start |
| `insert_mode` | Insert before selection |
| `join_selections` | Join lines |
| `join_selections_space` | Join lines and select space |
| `jump_backward` | Jump backward on jumplist |
| `jump_forward` | Jump forward on jumplist |
| `jump_view_down` | Jump to split below |
| `jump_view_left` | Jump to left split |
| `jump_view_right` | Jump to right split |
| `jump_view_up` | Jump to split above |
| `jumplist_picker` | Jumplist picker |
| `keep_primary_selection` | Keep primary selection |
| `keep_selections` | Keep selections matching regex |
| `last_picker` | Open last picker |
| `later` | Move forward in history |
| `lsp_or_syntax_symbol_picker` | Document symbol picker |
| `lsp_or_syntax_workspace_symbol_picker` | Workspace symbol picker |
| `match_brackets` | Go to matching bracket |
| `merge_consecutive_selections` | Merge consecutive selections |
| `merge_selections` | Merge selections |
| `move_char_left` | Move left |
| `move_char_right` | Move right |
| `move_line_down` | Move down (textual line) |
| `move_line_up` | Move up (textual line) |
| `move_next_long_word_end` | Move to next WORD end |
| `move_next_long_word_start` | Move to next WORD start |
| `move_next_word_end` | Move to next word end |
| `move_next_word_start` | Move to next word start |
| `move_parent_node_end` | Move to parent node end |
| `move_parent_node_start` | Move to parent node start |
| `move_prev_long_word_start` | Move to previous WORD start |
| `move_prev_word_start` | Move to previous word start |
| `move_visual_line_down` | Move down (visual line) |
| `move_visual_line_up` | Move up (visual line) |
| `normal_mode` | Switch to normal mode |
| `open_above` | Open line above |
| `open_below` | Open line below |
| `page_cursor_half_down` | Move cursor and page half down |
| `page_cursor_half_up` | Move cursor and page half up |
| `page_down` | Move page down |
| `page_up` | Move page up |
| `paste_after` | Paste after selection |
| `paste_before` | Paste before selection |
| `paste_clipboard_after` | Paste clipboard after |
| `paste_clipboard_before` | Paste clipboard before |
| `record_macro` | Record macro |
| `redo` | Redo change |
| `remove_primary_selection` | Remove primary selection |
| `remove_selections` | Remove selections matching regex |
| `rename_symbol` | Rename symbol (LSP) |
| `repeat_last_motion` | Repeat last motion |
| `replace` | Replace with character |
| `replace_selections_with_clipboard` | Replace with clipboard |
| `replace_with_yanked` | Replace with yanked text |
| `replay_macro` | Replay macro |
| `rotate_selection_contents_backward` | Rotate contents backward |
| `rotate_selection_contents_forward` | Rotate contents forward |
| `rotate_selections_backward` | Rotate selections backward |
| `rotate_selections_forward` | Rotate selections forward |
| `rotate_view` | Next window |
| `rsearch` | Reverse search |
| `save_selection` | Save selection to jumplist |
| `scroll_down` | Scroll down |
| `scroll_up` | Scroll up |
| `search` | Search regex |
| `search_next` | Next search match |
| `search_prev` | Previous search match |
| `search_selection` | Use selection as search |
| `search_selection_detect_word_boundaries` | Search selection word-bounded |
| `select_all` | Select entire file |
| `select_all_children` | Select all children (TS) |
| `select_all_siblings` | Select all siblings (TS) |
| `select_mode` | Enter select mode |
| `select_next_sibling` | Select next sibling (TS) |
| `select_prev_sibling` | Select previous sibling (TS) |
| `select_references_to_symbol_under_cursor` | Select symbol references |
| `select_regex` | Regex select |
| `select_register` | Select register |
| `select_textobject_around` | Select around textobject |
| `select_textobject_inner` | Select inside textobject |
| `shell_append_output` | Append shell output |
| `shell_insert_output` | Insert shell output |
| `shell_keep_pipe` | Filter with shell predicate |
| `shell_pipe` | Pipe selection through shell |
| `shell_pipe_to` | Pipe to shell, ignore output |
| `shrink_selection` | Shrink to child node (TS) |
| `shrink_to_line_bounds` | Shrink to line bounds |
| `split_selection` | Split selection on regex |
| `split_selection_on_newline` | Split on newlines |
| `surround_add` | Surround add |
| `surround_delete` | Surround delete |
| `surround_replace` | Surround replace |
| `suspend` | Suspend to shell |
| `swap_view_down` | Swap with split below |
| `swap_view_left` | Swap with left split |
| `swap_view_right` | Swap with right split |
| `swap_view_up` | Swap with split above |
| `switch_case` | Toggle case |
| `switch_to_lowercase` | Switch to lowercase |
| `switch_to_uppercase` | Switch to uppercase |
| `till_prev_char` | Find till previous char |
| `toggle_block_comments` | Toggle block comments |
| `toggle_comments` | Toggle comments |
| `toggle_line_comments` | Toggle line comments |
| `transpose_view` | Transpose splits |
| `trim_selections` | Trim whitespace |
| `undo` | Undo change |
| `unindent` | Unindent |
| `vsplit` | Vertical split |
| `vsplit_new` | Vertical split (scratch) |
| `wclose` | Close window |
| `wonly` | Close other windows |
| `workspace_diagnostics_picker` | Workspace diagnostics picker |
| `yank` | Yank selection |
| `yank_main_selection_to_clipboard` | Yank main selection to clipboard |
| `yank_to_clipboard` | Yank to clipboard |

## Typable commands (64)

Used as `:name` in keymaps or typed in command mode.

| Name | Description |
|---|---|
| `:append-output` | Run shell, append output |
| `:buffer-close` | Close current buffer |
| `:buffer-next` | Next buffer |
| `:buffer-previous` | Previous buffer |
| `:change-current-directory` | Change CWD |
| `:clear-register` | Clear register |
| `:config-open` | Open global config file |
| `:config-open-workspace` | Open workspace config file |
| `:config-reload` | Refresh config |
| `:cquit` | Quit with exit code |
| `:debug-eval` | Evaluate expression |
| `:debug-remote` | Connect TCP debug adapter |
| `:debug-start` | Start debug session |
| `:earlier` | Jump back in history |
| `:echo` | Print to statusline |
| `:encoding` | Set encoding |
| `:exit` | Write and quit |
| `:format` | Format file |
| `:get-option` | Get config option |
| `:goto` | Go to line number |
| `:hsplit` | Open in horizontal split |
| `:indent-style` | Set indent style |
| `:insert-output` | Run shell, insert output |
| `:later` | Jump forward in history |
| `:line-ending` | Set line ending |
| `:log-open` | Open log file |
| `:lsp-restart` | Restart language servers |
| `:lsp-stop` | Stop language servers |
| `:lsp-workspace-command` | LSP workspace command picker |
| `:move` | Move file |
| `:new` | New scratch buffer |
| `:noop` | Do nothing |
| `:open` | Open file |
| `:pipe` | Pipe selection to shell |
| `:quit` | Close current view |
| `:quit-all` | Close all views |
| `:read` | Read file into buffer |
| `:redraw` | Redraw UI |
| `:reflow` | Hard-wrap selection |
| `:reload` | Reload file from disk |
| `:reload-all` | Reload all files |
| `:reset-diff-change` | Reset diff hunk |
| `:run-shell-command` | Run shell command |
| `:set-language` | Set buffer language |
| `:set-option` | Set config option |
| `:set-register` | Set register contents |
| `:sort` | Sort ranges |
| `:theme` | Change theme |
| `:toggle-option` | Toggle config option |
| `:tree-sitter-highlight-name` | Show highlight scope |
| `:tree-sitter-layers` | Show injection layers |
| `:tree-sitter-scopes` | Show tree-sitter scopes |
| `:tree-sitter-subtree` | Show syntax subtree |
| `:tutor` | Open tutorial |
| `:update` | Write if modified |
| `:vsplit` | Open in vertical split |
| `:workspace-trust` | Trust workspace |
| `:workspace-untrust` | Untrust workspace |
| `:write` | Write to disk |
| `:write-all` | Write all buffers |
| `:write-buffer-close` | Write and close buffer |
| `:write-quit` | Write and close view |
| `:write-quit-all` | Write all and quit all |
| `:yank-diagnostic` | Yank diagnostic |

## Macro commands

Referenced in keymaps as `q` (replay from selected register) or `&quot;m q` (replay from register `m`). Replays the key sequence recorded via `Q` (stop/start).

---

## Default keybinding structure

Default keymap defined in `helix-term/src/keymap/default.rs`:
- **Normal mode:** ~340 bindings across `hjkl`, `wbe`, `fFtT`, `dcyp`, `/?nN`, `g`, `C-w`/`space w`, `z`/`Z`, `m`, `[]`, `space` pickers, etc.
- **Select mode:** Cloned from normal with `extend_*` overrides for movement
- **Insert mode:** ~24 bindings (`esc` to normal, completion, register insert)
