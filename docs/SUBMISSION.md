# Submission checklist - Draft IS 800:2025 screening task

## Deliverables
| Item | Location | Status |
|---|---|---|
| Python module | `src/osdag/utils/common/is800_2025.py` | Done (see caveat) |
| Report (Markdown) | `docs/IS800_2025_report.md` | Done |
| Unit tests | `tests/test_is800_2025.py` (18 tests) | Done, all passing |
| Demo video (3-10 min) | not recorded | **You must record and upload** |
| Submission form | link to repo/branch + video link | **You must submit** |

Note: the task text says `src/osdag_core/...`; on the repository's default branch the equivalent
folder is `src/osdag/utils/common/`. Mention this in the form if asked.

## Caveat to state honestly
The draft text was not readable while writing the code. Values not confirmed from the draft reuse
IS 800:2007 and are tagged `TODO(verify)`. Run `grep -n "TODO(verify)" src/osdag/utils/common/is800_2025.py`
to list them. Before the interview, try to read the draft chapters 10, 12, 14, 15, 17 and resolve as
many as you can; you must be able to explain every line.

## Run the tests
```
python -m pytest tests/test_is800_2025.py -v
```
(Python 3.10+ and pytest. The test loads the module by file path, so Qt and the rest of Osdag are not needed.)

## Push (needs your GitHub account)
```
git remote add myfork https://github.com/<you>/Osdag.git
git push -u myfork feature/is800-2025-draft
```
Then open a pull request or share the branch link.

## Demo video script (about 6 minutes, screen recording; voiceover optional)
1. (0:00) Show `is800_2007.py`: class of static methods, naming, Table 5 dict.
2. (0:45) Show `is800_2025.py` header docstring: chapter map and the status/caveat paragraph.
3. (1:30) Walk `DRAFT_CHANGES` and explain what was confirmed (WSD deleted, 24 chapters, new cl. 11.7, Table 2, Ch. 14/15 changes).
4. (2:30) Show one function end to end, e.g. `cl_14_design_compressive_stress` vs its test.
5. (3:30) Show a `TODO(verify)` and explain why 2007 values were kept.
6. (4:15) Run `python -m pytest tests/test_is800_2025.py -v` and show 18 passing.
7. (5:00) Open the report: comparison table, assumptions, challenges (mention the 2007 slenderness-table observation).
8. (5:45) State next steps. Upload as Unlisted on YouTube or a cloud drive and paste the link in the form.

## Interview prep: be ready to explain
- Derivation of chi from phi and lambda (Perry-Robertson form) and why f_cd is capped at f_y / gamma_m0.
- Why block shear takes the minimum of two failure paths.
- k_b in bolt bearing and why each term is there.
- Why the cl. 11.7 function is only a placeholder.
