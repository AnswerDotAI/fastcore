# NB: this file is designed for an LLM reader, not a human. Add it to your LLM's context and ask it to explain.
"""Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.

- `import *`: fastcore.tools (text, file editors; `lnhash` addresses without exhash), fastcore.nbio (notebooks, cells; `Notebook`, `NbCell` session objects)
- notation: /why
- prefer, where installed: exhash.skill: verified edits; rgapi.skill: search; aidialog.dlgskill or dialoghelper: Solveit dialogs (.ipynb of notes, code, prompt/reply pairs); cell tools here still handle any notebook's structure, dialogs too
- remold: engine behind `ast_replace`
- `Notebook` `nb[k]`: k = position, cell id or unique id prefix; get cell, assign source, `del`

### Names, parameters: same across the toolkit

- text primitives (`str_replace`, `del_lines`, `ast_replace`, `exhash`, ...) act on a str; `file_`, `cell_`, `msg_` prefix: same op on that target, address args first
- other ops: verb_target (`view_file`, `read_nb`, `summary_nb`, `lnhashview_cell`); no extra dialog or notebook part: `find_msgs`, `add_msg`, `del_msgs`, `find_cells`
- msg: dialog message; cell: notebook cell; plural: several (`lnhashview_cells`); converter `x2y`, method `to_y`; `str_replace`: Anthropic text editor's name, argument order
- argument order: address (text; path; path, cell_id; message id), new text, keyword-only context (dialog)
- search patterns: regex by default; editors: literal unless `use_regex=True`
- `only_*` narrows, `incl_*` widens; `context=`: file lines (summary mode: blocks), cells or messages
- editors return a diff: read it, don't re-view

### Functions, methods

| |function|method
-|-|-
target|path|held object
saving|each call; returns diff|explicit `save()`
`NbCell`|`cell_str_replace(path, cell_id, ...)`|`c.str_replace(...)`
`Notebook`|`find_cells(path, pat)`|`nb.find_cells(pat)`
reads return|snapshot rows: addresses, source, metadata|objects

- method: the function's name and arguments, minus its target part and address
- one style per file: save before switching to functions; reopen before methods

### Addresses

- unsure where: summary first: `rg(summary=True)`, `nbrg`, `summary_dlg`, `open_doc` outline    /an addressed row per block, cell, message or section
- copy from a view (`nums=True`, `lnhashs=True`, `rg(lnhashs=True)`); prefer lnhash where exhash is installed    /stale ones rejected
- plain line numbers: unverified, shift: re-view after each edit; several: bottom-to-top

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
