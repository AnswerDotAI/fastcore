"""Text, file, cell, and notebook editing from `fastcore.tools` and `fastcore.nbio`, plus the conventions the whole fastai editing toolkit follows. Read this before working with the editing tools in any package that shares them.

`from fastcore.editskill import *` loads the fastcore editing layer: the text primitives and file tools of `fastcore.tools`, and the notebook I/O and cell editors of `fastcore.nbio`. Sibling packages extend the same toolkit, and where they are installed prefer them as noted: `exhash` for hash-verified editing, `rgapi` for search, `llmsurgery`/`dialoghelper` for dialogs.

## Carriers

Each editing function works on one carrier: text (a str in memory), a file (a path on disk), a cell (one cell's source in an .ipynb file, addressed by `path, cell_id`), or a notebook (the parsed .ipynb; `Notebook` and `NbCell` are its held-object forms). These are the representation layer: an .ipynb is a file of cells, whatever produced it. The dialog layer above adds the msg and dlg carriers: a Solveit dialog is an .ipynb whose cells are messages (notes, runnable code, prompt/reply pairs), and `llmsurgery.dlgskill` and `dialoghelper` provide the message tools, following the conventions here with their own nouns. The word picks the layer: cell tools answer representation questions ("why does Jupyter reject this file?"), msg tools answer content questions ("what does this message say?").

## Naming

Two name shapes cover the toolkit, and the pivot is the verb's direct object:

- An operation on a whole carrier takes the carrier as its noun: verb_carrier. `view_file`, `create_file`, `read_nb`, `write_nb`, `view_cell`, `validate_nb`; in the dialog layer `view_msg` and `view_dlg`. Coined verbs follow the same shape: `lnhashview_cell` is "lnhashview this cell". When the verb's object is instead the medium's unit, and that unit names its carrier uniquely, no prefix is needed - the unit noun is the carrier signal: `find_msgs`, `add_msg`, `del_msgs` (msgs live only in dialogs), `find_cells`, `summary_nb`'s rows (cells live only in notebooks).
- An operation within a carrier already owns its noun (`insert_line`, `del_lines`, `replace_lines`, `str_replace`), so the carrier prefixes as a namespace and the op name survives intact: carrier_op, as in `file_del_lines`, `cell_del_lines`, `msg_del_lines`. The bare op names are the text-level primitives, and every carrier version keeps the identical signature after its address arguments, so each family is learned once and recognized everywhere.

The exceptions are deliberate and closed. `str_replace` keeps the name and argument order established by Anthropic's text editor tool. Instrument-named ops put the instrument first and elide their unit: `ast_replace` (the AST pattern is how the edit finds its target) and `exhash` (hash-verified line addresses travel inside its commands), carrier-prefixed like any other line-level op: `file_ast_replace`, `msg_ast_replace`, `file_exhash`, `cell_exhash`. Converters are named x2y (`nb2dict`, `cell2xml`; in llmsurgery, `dlg` on exactly one side of every converter), and on a held object the converter is a `to_y` method (`nb.to_dict()`). Plural marks arity: `view_cell` takes one cell, `lnhashview_cells` several, `del_msgs` many.

## Parameters

One vocabulary, identical wherever it appears:

- The carrier's address comes first (`text`; `path`; `path, cell_id`; a message `id`), the payload next, and ambient context last as keyword-only (message tools name their dialog that way).
- `start_line`/`end_line`: 1-based, inclusive, `None` for first/last, negative counting from the end. Destructive ops (`del_lines`) accept no defaults: state the range.
- `re_filter`/`invert_filter`: restrict an edit to lines matching (or not matching) a regex, like ex's `g//` and `g!//`; combines with the range.
- Searches read patterns as regex by default; editors read them as literal text until `use_regex=True`. Searching is read-only, so its default favors power; editing favors safety.
- `nums` and `lnhashs` on any view: line numbers, or `lineno|hash|` addresses. `maxlen` caps characters per summary line; `trunc_out`/`trunc_in` truncate outputs and sources in dialog views.
- Search tools share one filter vocabulary: `pattern` first, `root='.'`, and the same include/exclude/ext/hidden/ignore block across `fd`, `ls`, `rg`, and `nbrg`. Variants differ by defaults, not API: `ls` is `fd` with listing defaults. Boolean filters narrow as `only_*` and widen as `include_*`.
- `context=` counts the medium's own units: lines (or blocks in summary mode) for files, cells for notebooks, messages for dialogs. Dialog search defaults to context 1 because the neighbouring note usually explains the match: the why lives next to the what.
- Every editor returns a diff ("none: No changes." when nothing changed). The diff is the verification: read it instead of re-viewing the target.

## Functions and methods

Every operation has two shapes with one contract each. The function is a transaction: it addresses a file by path, applies the edit, writes, and returns a diff. The method is a session: it mutates the object in hand, and nothing reaches disk until an explicit save. The correspondence is mechanical - the method is the function minus its address arguments, keeping its name except that a carrier token which became `self` drops: `cell_str_replace(path, cell_id, ...)` is `c.str_replace(...)` on a held `NbCell`, `find_cells(path, pat)` is `nb.find_cells(pat)` on a held `Notebook`. Function-side reads return dead snapshot rows carrying addresses, source, and meta; session-side reads return the live objects. Use one shape at a time per file: save before switching to functions, reopen after.

## Addresses

Edits say where with line numbers or lnhash addresses. Take addresses from the read you were already doing instead of with a second look: views accept `nums=True` or `lnhashs=True`, and searches return addresses directly (`rg(lnhashs=True)`). Prefer lnhash addresses whenever `exhash` is installed: they are verified against current content at edit time, so a stale address fails loudly instead of editing nearby text, which is exactly what makes taking addresses early safe. Plain line numbers are unverified and shift as edits apply, so re-view after each edit and apply multi-edits bottom-to-top. `exhash.skill` owns the address format and the verified editor.

When you don't yet know where to edit, locate with a summary first: `rgapi`'s `rg(summary=True)` and `nbrg`, and llmsurgery's `summary_dlg`, each show one line per natural unit of their medium (block, cell, message), carrying the unit's address. Summaries locate, views read, addresses edit, diffs confirm.

## What's where

- `fastcore.tools`: text primitives, file tools, and `line_hash`/`lnhash`/`lnhash_at` for creating addresses without exhash installed.
- `fastcore.nbio`: notebook read/write/validate/repair, cell construction, cell editors, and the `Notebook`/`NbCell` session objects with their snapshot queries (`find_cells`, `summary_nb`).
- `exhash.skill`: hash-verified editing for files and cells; prefer it for edits where installed.
- `rgapi.skill`: `rg`/`fd`/`ls`/`nbrg` search with lnhash output.
- `remold`: structural search and rewrite for Python source (declarative ast-grep rules, LibCST matcher transforms, symbol queries); the engine behind `ast_replace`.
- `llmsurgery.dlgskill`, `dialoghelper`: the dialog layer, including its own theory of dialogs and projections.

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
