"""Run some cells of a notebook from the terminal, and save their outputs in the notebook.

Cells are found by CONTENT (the first line of the cell), not by position: cells get added,
positions change, first lines don't. Only the chosen cells run, in the order given, in a
fresh kernel of THIS Python (so run it with the repo's .venv).

Usage (from the repo root):
    .venv/bin/python tools/run_cells.py <notebook.ipynb> "<first line of cell 1>" ["<first line of cell 2>" ...]

Example: re-measure probe 1.10 on the saved runs (free: no model calls)
    .venv/bin/python tools/run_cells.py my-agents/First_agent_template/First_agent_template.ipynb \
        "# --- Probe 1.10: parameters ---" "# --- Probe 1.10: measure"
"""
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

# --- 1. Arguments: the notebook, then one marker per cell ---
if len(sys.argv) < 3:
    sys.exit(__doc__)
path, markers = Path(sys.argv[1]), sys.argv[2:]

# --- 2. A kernel of this same Python (a throwaway kernelspec, so no global Jupyter setting matters) ---
# Set before importing nbclient: Jupyter reads JUPYTER_PATH when it looks for kernels.
spec_root = tempfile.mkdtemp()
spec_dir = Path(spec_root) / "kernels" / "this-python"
spec_dir.mkdir(parents=True)
(spec_dir / "kernel.json").write_text(json.dumps({
    "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
    "display_name": "this python", "language": "python"}))
os.environ["JUPYTER_PATH"] = spec_root

import nbformat                      # noqa: E402  (after JUPYTER_PATH, on purpose)
from nbclient import NotebookClient  # noqa: E402

# --- 3. Find the cells: each marker must match the start of exactly one code cell ---
nb = nbformat.read(path, as_version=4)
picked = []
for m in markers:
    hits = [i for i, c in enumerate(nb.cells) if c.cell_type == "code" and c.source.startswith(m)]
    assert len(hits) == 1, f"{len(hits)} code cells start with {m!r} (need exactly 1)"
    picked += hits

# --- 4. Run them in a copy that holds only those cells (working directory = the notebook's folder) ---
tmp = copy.deepcopy(nb)
tmp.cells = [copy.deepcopy(nb.cells[i]) for i in picked]
NotebookClient(tmp, kernel_name="this-python", timeout=3600,
               resources={"metadata": {"path": str(path.parent)}}).execute()

# --- 5. Copy the outputs back into the real notebook, and print them ---
for n, i in enumerate(picked):
    nb.cells[i].outputs = tmp.cells[n].outputs
    nb.cells[i].execution_count = tmp.cells[n].execution_count
nbformat.write(nb, path)
for c in tmp.cells:
    for o in c.outputs:
        print(o.get("text", "") or o.get("evalue", ""), end="")
