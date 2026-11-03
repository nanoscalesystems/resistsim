# Apply calibration evidence step 1

Prepared against public commit 2c55989673b46051b878b9acb185d78d0cb84adc and your matching resistsim(1).zip. Apply in the original Python repo, on research/calibration-consistency. No model source, dependencies, wheel, website or default parameters change.

Files added:
- data/experiments/liu2026_265nm_e0.json
- scripts/calibration_consistency.py
- tests/test_calibration_evidence.py
- docs/calibration-evidence.md

File updated: README.md. This installation note is also included.

Before extracting:

```bash
cd ~/work/resistsim
git status --short --branch
```

If you have edited README.md since the supplied snapshot, save/compare those edits before replacing it. Extraction is an overlay, not an automatic three-way merge.

```bash
unzip ~/Downloads/resistsim-calibration-step1.zip -d ~/work/resistsim
python scripts/calibration_consistency.py
python -m unittest discover -s tests -p test_calibration_evidence.py -v
python -m pytest -q
git diff -- README.md
git status --short
```

The first two Python checks passed during preparation (8 new tests). The existing full pytest suite must be run locally; pytest was unavailable in the preparation environment. New tests also work under pytest. No extra packages are needed beyond the existing project environment.

Optional JSON export:

```bash
python scripts/calibration_consistency.py --output /tmp/resistsim-calibration-report.json
```

The script refuses to overwrite an existing report; choose another name for another run. JSON preserves observed values, assumptions, fitted values, predictions and source hashes. Unreachable model clearing doses use null plus a status, not Infinity. The data check detects disagreements between the dataset and the installed registry. Run `python -c "import resistsim; print(resistsim.__file__)"` if it reports a mismatch.

After reviewing the changes and test results, a local commit can be made with:

```bash
git add README.md data/experiments/liu2026_265nm_e0.json scripts/calibration_consistency.py tests/test_calibration_evidence.py docs/calibration-evidence.md
git diff --cached
git commit -m "Add sourced 265 nm calibration evidence and consistency diagnostic"
```

Check for any previously staged unrelated edits before committing. No push is needed for the next research step. You may keep this installation note outside the repository or leave it untracked. Source PDFs are not included in the patch.
