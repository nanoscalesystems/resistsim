# Apply calibration Step 3

Stay on research/calibration-consistency with your virtual environment active.
This patch adds three files plus this guide; it replaces no existing source files.
Requires the Step 1 script/data and installed resistsim (editable recommended).

```bash
cd ~/work/resistsim
unzip ~/Downloads/resistsim-calibration-step3.zip -d ~/work/resistsim
python scripts/film_identifiability.py
python -m unittest discover -s tests -p test_film_identifiability.py -v
python -m pytest -q
```

`-d` selects the extraction destination; unittest's `-p` selects the new test file;
`-v` displays individual tests. pytest checks the whole repository.
Expected total is 63 if your previous 56 tests are unchanged.

Optional machine-readable report (refuses to overwrite):

```bash
python scripts/film_identifiability.py --output /tmp/resistsim-film-identifiability.json
```

After checking results, you can commit locally:

```bash
git add APPLY-CALIBRATION-STEP3.md scripts/film_identifiability.py tests/test_film_identifiability.py docs/film-identifiability.md
git commit -m "Add conditional film calibration identifiability diagnostic"
```

No push is required. The untracked APPLY-CALIBRATION-STEP1.md is an installation
guide, not an execution dependency; it may be committed separately if desired.
See docs/film-identifiability.md for equations, evidence limits and missing data.
