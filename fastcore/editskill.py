"""Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.

`from fastcore.editskill import *` loads `fastcore.tools` (text primitives, file tools) and `fastcore.nbio` (notebook I/O, cell editors). Where installed, prefer `exhash` for hash-verified editing, `rgapi` for search, and `aidialog`/`dialoghelper` for dialogs.

## Places

Targets: strings in memory, files (a path), notebook cells (`path, cell_id`; edits that cell's source), and in-memory `Notebook`/`NbCell`. A Solveit dialog is an `.ipynb` whose cells are notes, runnable code, and prompt/reply pairs; cell tools work with notebook structure whatever produced the file, while `aidialog.dlgskill`/`dialoghelper` read and edit dialog messages. exhash's `open_doc` outlines Markdown, code, and notebooks (`doc(open_doc)`: inputs, navigation, llms.txt workflow); a section is a span of lines or a run of cells, changed with the file and cell tools.

Open a `Notebook` with `Notebook.open(path)` and save it with `nb.save()`. Index it by position or cell id (exact or unique prefix): `nb[k]` returns a cell, `nb[k] = src` sets its source, and `del nb[k]` removes it. `nb.add(src, cell_type)` and `nb.md(src)` insert a cell at `idx`, or `after` or `before` a cell id. `nb.move(ids, after=, before=)` reorders cells.

## Naming

- Operations on files, notebooks, cells, and messages: `verb_target` (`view_file`, `create_file`, `read_nb`, `write_nb`, `view_cell`, `validate_nb`, `view_msg`, `view_dlg`, `lnhashview_cell`). `find_msgs`, `add_msg`, `del_msgs`, `find_cells` need no extra dialog/notebook prefix. `msg` = dialog message; `cell` = notebook cell. `summary_nb` returns rows for notebook cells.
- Text primitives (`insert_line`, `del_lines`, `replace_lines`, `str_replace`) get `file_`/`cell_`/`msg_` versions (`file_del_lines`, `cell_del_lines`, `msg_del_lines`) that take the primitive's arguments after their address arguments. `str_replace` keeps the name and argument order of Anthropic's text editor tool. `ast_replace` (AST patterns) and `exhash` (hash-verified line addresses) use the same prefixes: `file_ast_replace`, `msg_ast_replace`, `file_exhash`, `cell_exhash`.
- Converters: `x2y` (`nb2dict`, `cell2xml`, aidialog's `dlg2md`); converter methods: `to_y` (`nb.to_dict()`).
- Plural names take several items: `view_cell` one cell, `lnhashview_cells` several, `del_msgs` many.

## Parameters (one vocabulary wherever it appears)

- Order: the place's address (`text`; `path`; `path, cell_id`; a message `id`), then the new text, then ambient context as keyword-only (how message tools name their dialog).
- `start_line`/`end_line`: 1-based, inclusive, `None` = first/last line; a negative `end_line` counts from the end. `del_lines` has no defaults: state the range.
- `re_filter`/`invert_filter`: restrict an edit to lines (not) matching a regex, like ex `g//`/`g!//`; combines with the range.
- Searches read patterns as regex by default; editors read them as literal text unless `use_regex=True`.
- Views: `nums` (line numbers), `lnhashs` (`lineno|hash|` addresses); `maxlen` caps summary lines; `trunc_out`/`trunc_in` truncate outputs/sources in dialog views.
- Search tools (`fd`, `ls`, `rg`, `nbrg`): `pattern` first, `root='.'`, one include/exclude/ext/hidden/ignore block; variants differ by defaults, not API (`ls` is `fd` with listing defaults).
- Boolean filters narrow as `only_*` (`only_err`, `only_exp`, `only_errors`) and widen as `incl_*` (`incl_out`).
- `context=` counts the place's units: lines (blocks in summary mode) for files, cells for notebooks, messages for dialogs.
- Editors return a diff, which is the verification: read it rather than re-viewing. No change: fastcore editors and exhash return `none: No changes.`

## Functions and methods

Functions take a path, save, and return a diff; methods change an object in memory, saved explicitly. Methods drop the address arguments and the object's part of the name: `cell_str_replace(path, cell_id, ...)` -> `c.str_replace(...)` on an `NbCell`; `find_cells(path, pat)` -> `nb.find_cells(pat)` on a `Notebook`. Read functions return snapshot rows (addresses, source, metadata); read methods return the objects. One style per file at a time: save before switching to functions, reopen before returning to methods.

## Addresses

Edits take plain line numbers or lnhash addresses, got while reading: `nums=True`/`lnhashs=True` views, `rg(lnhashs=True)`. Prefer lnhash addresses where exhash is installed; stale ones are rejected. Plain line numbers are unverified and shift, so re-view after each such edit and apply several bottom-to-top. `exhash.skill` covers address forms and the verified edit loop.

Not sure where to edit? Start with a summary: rgapi's `rg(summary=True)` and `nbrg`, aidialog's `summary_dlg`, and exhash's `open_doc` outlines give one addressed row per block, cell, message, or section. A section token such as `1.6.|12|Py|,45|HD|` is the section number plus the lnhash range of the section's first and last lines; that range works as an exhash address.

## What's where

- `fastcore.tools`: text primitives, file tools, and `line_hash`/`lnhash`/`lnhash_at` for creating addresses without exhash installed.
- `fastcore.nbio`: notebook read/write/validate/repair, cell construction, cell editors, and the `Notebook`/`NbCell` session objects with their snapshot queries (`find_cells`, `summary_nb`).
- `exhash.skill`: hash-verified editing for files and cells, plus `open_doc` section outlines for Markdown, code, and notebooks; prefer it for edits where installed.
- `rgapi.skill`: `rg`/`fd`/`ls`/`nbrg` search with lnhash output, and `rgstr` to search text already in hand.
- `remold`: structural search and rewrite for Python source (declarative ast-grep rules, LibCST matcher transforms, symbol queries); the engine behind `ast_replace`.
- `aidialog.dlgskill`, `dialoghelper`: the dialog layer, including its own theory of dialogs and projections.

Docs: https://fastcore.fast.ai/tools.html.md and https://fastcore.fast.ai/nbio.html.md
"""

from fastcore.tools import (insert_line, str_replace, strs_replace, replace_lines, del_lines, ast_replace,
    file_insert_line, file_str_replace, file_strs_replace, file_replace_lines, file_del_lines, file_ast_replace,
    view_file, create_file, line_hash, lnhash, lnhash_at)
from fastcore.nbio import (read_nb, write_nb, new_nb, mk_cell, validate_nb, validate_cell, repair_nb, repair_cell,
    view_cell, cell_insert_line, cell_str_replace, cell_strs_replace, cell_replace_lines, cell_del_lines, cell_ast_replace, Notebook, NbCell, find_cells, summary_nb)

__all__ = ['insert_line', 'str_replace', 'strs_replace', 'replace_lines', 'del_lines', 'ast_replace',
    'file_insert_line', 'file_str_replace', 'file_strs_replace', 'file_replace_lines', 'file_del_lines', 'file_ast_replace',
    'view_file', 'create_file', 'line_hash', 'lnhash', 'lnhash_at',
    'read_nb', 'write_nb', 'new_nb', 'mk_cell', 'validate_nb', 'validate_cell', 'repair_nb', 'repair_cell',
    'view_cell', 'cell_insert_line', 'cell_str_replace', 'cell_strs_replace', 'cell_replace_lines', 'cell_del_lines', 'cell_ast_replace', 'Notebook', 'NbCell', 'find_cells', 'summary_nb']

__pyskill_params__ = {'replace_params': ('start_line', 'end_line', 'n_matches', 're_filter', 'invert_filter', 'use_regex')}
