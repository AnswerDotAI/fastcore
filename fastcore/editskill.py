"""Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.

`from fastcore.editskill import *` loads `fastcore.tools` and `fastcore.nbio`.

## Targets and tools

Targets: in-memory strings, file paths, notebook cell sources (`path, cell_id`), and held `Notebook`/`NbCell` objects.

- `fastcore.tools`: text primitives, file tools, and `line_hash`/`lnhash`/`lnhash_at` address creation without exhash installed.
- `fastcore.nbio`: notebook read/write/validate/repair, cell construction/editing, and `Notebook`/`NbCell` session objects with snapshot queries (`find_cells`, `summary_nb`).
- `exhash.skill`: preferred hash-verified file/cell editing where installed; covers address forms and the verified edit loop.
- `rgapi.skill`: preferred search where installed: `rg`/`fd`/`ls`/`nbrg` with lnhash output, `rgstr` for text already held.
- `remold`: structural Python search/rewrite with declarative ast-grep rules, LibCST matcher transforms and symbol queries; the engine behind `ast_replace`.
- `aidialog.dlgskill`, `dialoghelper`: preferred dialog layer where installed, including its own theory of dialogs and projections. A Solveit dialog is an `.ipynb` with notes, runnable code and prompt/reply pairs. Cell tools handle notebook structure regardless of origin; this layer reads/edits dialog messages.

Open/save: `Notebook.open(path)`, `nb.save()`. Index by position or cell id (exact/unique prefix): `nb[k]` returns a cell, `nb[k] = src` sets its source, `del nb[k]` removes it. `nb.add(src, cell_type)`/`nb.md(src)` insert at `idx`, `after` or `before` a cell id; `nb.move(ids, after=, before=)` reorders cells.

## Naming

- File/notebook/cell/message operations: `verb_target` (`view_file`, `create_file`, `read_nb`, `write_nb`, `view_cell`, `validate_nb`, `view_msg`, `view_dlg`, `lnhashview_cell`). `find_msgs`, `add_msg`, `del_msgs`, `find_cells` need no extra dialog/notebook prefix. `msg` = dialog message; `cell` = notebook cell; `summary_nb` returns notebook-cell rows.
- Text primitives (`insert_line`, `del_lines`, `replace_lines`, `str_replace`) gain `file_`/`cell_`/`msg_` prefixes (`file_del_lines`, `cell_del_lines`, `msg_del_lines`); address arguments precede the primitive's arguments. `str_replace` retains Anthropic's text editor name/argument order. `ast_replace` (AST patterns) and `exhash` (hash-verified line addresses) use these prefixes too: `file_ast_replace`, `msg_ast_replace`, `file_exhash`, `cell_exhash`.
- Converters: `x2y` (`nb2dict`, `cell2xml`); methods: `to_y` (`nb.to_dict()`).
- Plurals accept several items: `view_cell` one cell, `lnhashview_cells` several, `del_msgs` many.

## Parameters: shared vocabulary

- Order: address (`text`; `path`; `path, cell_id`; message `id`), new text, then keyword-only ambient context (message tools' dialog).
- `start_line`/`end_line`: 1-based, inclusive; `None` = first/last line; negative `end_line` counts from the end. `del_lines` has no defaults: state the range.
- `re_filter`/`invert_filter`: lines (not) matching a regex, like ex `g//`/`g!//`; combines with the range.
- Search patterns default to regex; editors default to literal unless `use_regex=True`.
- Views: `nums` line numbers; `lnhashs` `lineno|hash|` addresses; `maxlen` caps summary lines; `trunc_out`/`trunc_in` truncate dialog outputs/sources.
- `fd`/`ls`/`rg`/`nbrg` share one include/exclude/ext/hidden/ignore block. `fd`/`rg`/`nbrg`: `pattern` first, `root='.'` second. `ls` is `fd` with listing defaults, but `root` first, like shell `ls DIR`.
- Filters narrow with `only_*` (`only_err`, `only_exp`, `only_errors`), widen with `incl_*` (`incl_out`).
- `context=` units: file lines (blocks in summary mode), notebook cells, dialog messages.
- Editors return a diff: read it as verification rather than re-viewing. No change: fastcore editors and exhash return `none: No changes.`

## Functions and methods

Functions take a path, save and return a diff; methods change held objects, saved explicitly. Methods drop address arguments and the object's part of the name: `cell_str_replace(path, cell_id, ...)` -> `c.str_replace(...)` on `NbCell`; `find_cells(path, pat)` -> `nb.find_cells(pat)` on `Notebook`. Read functions return snapshot rows (addresses, source, metadata); read methods return objects. One style per file: save before switching to functions; reopen before returning to methods.

## Navigation and addresses

When unsure where to edit, start with summaries: rgapi's `rg(summary=True)`/`nbrg`, aidialog's `summary_dlg`, exhash's `open_doc` outlines. They give one addressed row per block/cell/message/section. `open_doc` outlines Markdown, code and notebooks; `doc(open_doc)` covers inputs, navigation and llms.txt. A section is a span of lines or a run of cells, edited through file/cell tools. Token `1.6.|12|Py|,45|HD|` combines section number and first/last-line lnhash range; the range is an exhash address.

Edits take plain line numbers or lnhash addresses obtained while reading: `nums=True`/`lnhashs=True` views, `rg(lnhashs=True)`. Prefer lnhash addresses where exhash is installed; stale ones are rejected. Plain numbers are unverified and shift: re-view after each such edit; apply several bottom-to-top.

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
