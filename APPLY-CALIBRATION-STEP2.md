# Apply step 2 after the tested step 1 patch

Adds three files and documentation; no existing model code or README replacement.

```bash
cd ~/work/resistsim
git status --short --branch
unzip ~/Downloads/resistsim-calibration-step2.zip -d ~/work/resistsim
python scripts/solution_kinetics.py
python -m unittest discover -s tests -p test_solution_kinetics.py -v
python -m pytest -q
```

Six new tests passed during preparation. Run the full suite locally; with the previous 50 tests and no other changes, expect 56. No new dependencies beyond NumPy. Keep working on research/calibration-consistency.

Optional report: `python scripts/solution_kinetics.py --output /tmp/resistsim-solution-kinetics.json` (choose another filename if it already exists).

After reviewing results:

```bash
git add data/experiments/liu2026_solution_kinetics.json scripts/solution_kinetics.py tests/test_solution_kinetics.py docs/solution-kinetics.md
git diff --cached
git commit -m "Add sourced solution kinetics and Arrhenius reconstruction"
```

Check for previously staged changes before committing. This saves locally; no push or deployment required. Installation guide can remain untracked. README from step 1 stays intact; docs/solution-kinetics.md documents this new diagnostic.
