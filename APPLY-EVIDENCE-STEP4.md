# Experimental evidence layer — Step 4

This adds an offline, three-view evidence page plus two new datasets and a six-source
review. It does not change simulation defaults or your Astro site. Requires Steps
1 and 2 for regenerating the page. The packaged docs/evidence-preview.html is ready
to open and contains a snapshot of those records, with no server or Pyodide needed.

```bash
cd ~/work/resistsim
unzip ~/Downloads/resistsim-evidence-step4.zip -d ~/work/resistsim
python -m unittest discover -s tests -p test_evidence_view.py -v
python -m pytest -q
xdg-open docs/evidence-preview.html
```

The new suite has five tests. Expected full count: 68 if your previous 63 are unchanged.
Only the five new tests were run in the patch environment; run your full suite locally.
`xdg-open` opens the HTML in your default browser. You can also open it from the file
manager. All three views use local data; source DOI links open externally only if clicked.

To regenerate after changing evidence:

```bash
python scripts/build_evidence_view.py --output /tmp/resistsim-evidence.html
xdg-open /tmp/resistsim-evidence.html
```

The script reads all four evidence JSON files, escapes their contents into HTML,
and refuses to overwrite an existing output. Choose a fresh output name on reruns.
No Python library beyond the standard library is needed to build the viewer.

Files added:
- data/experiments/lu2025_fluorine_free_iline.json
- data/experiments/liu2025_nonpfas_euv_gen2.json
- scripts/build_evidence_view.py
- tests/test_evidence_view.py
- docs/evidence-preview.html
- docs/evidence-cache-review.md
- this guide

The viewer is a local review artifact before integration with the Astro website.
The automated checks cover evidence semantics, HTML escaping and generated view
structure. Browser rendering was not verified here because the headless browser
executable was unavailable. Please check all three view buttons and the horizontally
scrolling tables on mobile.

See docs/evidence-cache-review.md for the six-source triage, provisional uLER table
selection, missing measurements and the distinction between performance benchmarking
and kinetic calibration. Do not copy dose-to-size into the E0 calibration fitter.
