"""Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.

`from fastcore.editskill import *` loads the fastcore editing layer: the text primitives and file tools of `fastcore.tools`, and the notebook I/O and cell editors of `fastcore.nbio`. When installed, prefer `exhash` for hash-verified editing, `rgapi` for search, and `aidialog` or `dialoghelper` for dialogs.

## Places

The tools edit strings in memory, files, notebook cells, and notebooks. File tools take a path. Cell tools take `path, cell_id` and edit that cell's source. `Notebook` and `NbCell` hold notebooks and cells in memory.

A Solveit dialog is an `.ipynb` whose cells represent notes, runnable code, and prompt/reply pairs. Cell tools work with notebook structure, regardless of which application produced the file. `aidialog.dlgskill` and `dialoghelper` provide tools for reading and editing dialog messages.

`open_doc` (in exhash) parses a file (`fname=`, or a `Path` as `src`), URL (an `https?://` str), or text (any other str) into a `Section` tree, with sections taken from Markdown headings, tree-sitter definitions in code, or md-heading cells in a notebook. A section points at a span of lines in a file, or a run of cells in a notebook. To change what a section contains, edit those lines or cells with the file and cell tools.

## Naming

Function names follow these conventions:

- Operations on files, notebooks, cells, and messages use `verb_target`: `view_file`, `create_file`, `read_nb`, `write_nb`, `view_cell`, `validate_nb`, `view_msg`, and `view_dlg`. This includes `lnhashview_cell`. Names such as `find_msgs`, `add_msg`, `del_msgs`, and `find_cells` need no extra dialog or notebook prefix. `msg` identifies a dialog message and `cell` identifies a notebook cell. `summary_nb` returns rows for notebook cells.
- Text-editing primitives include `insert_line`, `del_lines`, `replace_lines`, and `str_replace`. File, cell, and message versions add a prefix, as in `file_del_lines`, `cell_del_lines`, and `msg_del_lines`. After their address arguments, these versions take the same arguments as the text primitive.

`str_replace` keeps the name and argument order established by Anthropic's text editor tool. `ast_replace` uses AST patterns to find edit targets. `exhash` takes commands containing hash-verified line addresses. These operations use the same file, cell, and message prefixes: `file_ast_replace`, `msg_ast_replace`, `file_exhash`, and `cell_exhash`.

Converters use `x2y` names, such as `nb2dict` and `cell2xml`. In aidialog, exactly one side is `dlg`. Converter methods use `to_y`, as in `nb.to_dict()`.

Plural names take multiple items: `view_cell` takes one cell, `lnhashview_cells` several, and `del_msgs` many.

## Parameters

One vocabulary, identical wherever it appears:

- The place's address comes first (`text`; `path`; `path, cell_id`; a message `id`), the new text next, and ambient context last as keyword-only (message tools name their dialog that way).
- `start_line`/`end_line`: 1-based, inclusive, `None` for first/last, negative counting from the end. `del_lines` accepts no defaults: state the range.
- `re_filter`/`invert_filter`: restrict an edit to lines matching (or not matching) a regex, like ex's `g//` and `g!//`; combines with the range.
- Searches read patterns as regex by default. Editors read them as literal text unless `use_regex=True`.
- `nums` and `lnhashs` on any view: line numbers, or `lineno|hash|` addresses. `maxlen` caps characters per summary line; `trunc_out`/`trunc_in` truncate outputs and sources in dialog views.
- Search tools share one filter vocabulary: `pattern` first, `root='.'`, and the same include/exclude/ext/hidden/ignore block across `fd`, `ls`, `rg`, and `nbrg`. Variants differ by defaults, not API: `ls` is `fd` with listing defaults. Boolean filters narrow as `only_*` and widen as `include_*`.
- `context=` counts whatever units the place has: lines (or blocks in summary mode) for files, cells for notebooks, messages for dialogs. Dialog search defaults to context 1 because the neighbouring note usually explains the match.
- Every editor returns a diff ("none: No changes." when nothing changed). The diff is the verification: read it instead of re-viewing the target.

## Functions and methods

Editing functions take a file path, save their changes, and return a diff. Editing methods change an object in memory. Save it explicitly to write the changes.

Methods omit the function's address arguments and the part of its name that identifies the object. For example, `cell_str_replace(path, cell_id, ...)` becomes `c.str_replace(...)` on an `NbCell`. `find_cells(path, pat)` becomes `nb.find_cells(pat)` on a `Notebook`.

Read functions return snapshot rows containing addresses, source, and metadata. Read methods return the objects themselves. Use one style at a time per file. Save before switching to file functions, then reopen the object before returning to methods.

## Addresses

Edits accept line numbers, lnhash addresses, or section tokens. Get addresses while reading the target. Views accept `nums=True` or `lnhashs=True`. Searches can include addresses with `rg(lnhashs=True)`.

Prefer lnhash addresses when `exhash` is installed. The editor checks the hash against current content and rejects stale addresses. Plain line numbers are unverified and can shift after an edit. Re-view after each plain-line-number edit and apply multiple edits from bottom to top. Read `exhash.skill` for address formats and verified editing.

Section tokens identify sections in document outlines. In `1.6.|12|Py|,45|HD|`, `1.6.` is the section number. The rest is the lnhash range for its first and last lines. `d.at(token)` returns the section after checking its hash. `d.view(tok1, tok2)` prints the rendered text of both sections. Use the boundary range to edit the section: `file_exhash(path, ('12|Py|,45|HD|', 'c', new_text))`.

Read `exhash.skill` before working through large Markdown, code, or notebook files, or documentation from a URL. It describes `open_doc` tree searches and link following, including the llms.txt workflow.

When you don't know where to edit, start with a summary. `rgapi`'s `rg(summary=True)` and `nbrg`, aidialog's `summary_dlg`, and exhash's `open_doc` outlines show rows for blocks, cells, messages, or sections. Each row includes its address.

For prose, config, and other text organized into paragraphs, block summaries show the whole matched paragraph and its boundary addresses. Line-mode results show fragments that can require another view for context.

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
