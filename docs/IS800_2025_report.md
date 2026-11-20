# Report: `is800_2025.py` - Draft IS 800:2025 module for Osdag

## 1. Summary and important caveat

`src/osdag/utils/common/is800_2025.py` adds an `IS800_2025` class that mirrors the style of
`is800_2007.py` (static methods, `cl_<chapter>_<topic>` names, Args/Returns/Note docstrings,
partial safety factors in a class-level dict).

**I could not read the draft's text.** The Drive and BIS links were blocked in my environment and
the public summaries name changed clauses but give no formulas or values. So:

- The module's *structure* follows the draft's chapter layout (24 chapters).
- Where the draft's numeric change could not be confirmed, the **IS 800:2007 value is used and the
  line is tagged `TODO(verify)`** with the chapter to check. No draft-specific number was invented.
- Clause numbers inside the draft below chapter level are unknown to me, so functions are named by
  chapter (e.g. `cl_13_...`) and each docstring cites the 2007 clause it derives from.

Before any real use, every `TODO(verify)` must be checked against the draft PDF. This is the main
limitation of the submission.

## 2. Implemented functions

| Draft chapter | Functions | 2007 source |
|---|---|---|
| 9 Materials | `E`, `MU` constants | Sec. 2 |
| 10 General | `epsilon`, `cl_10_max_slenderness_ratio`, `Table2_outstand_flange`, `Table2_web_bending` | cl. 3.7, 3.8, Tables 2-3 |
| 11 Analysis | `cl_11_7_second_order_amplification` (placeholder) | new in draft |
| 12 Limit state | `cl_12_Table_safety_factors`, `working_stress_design` (raises) | Table 5 |
| 13 Tension | yielding, rupture, block shear | cl. 6.2, 6.3.1, 6.4.1 |
| 14 Compression | imperfection factor, `f_cd`, strength, effective length factor, buckling class | cl. 7.1, 7.2, Tables 7, 10 |
| 15 Bending | shear strength, moment strength, LTB strength | cl. 8.2, 8.4 |
| 17 Connections | hole size, pitch, edge/end distance, bolt shear/bearing/tension/combined, weld size, throat, design stress, strength | cl. 10.2-10.5 |

## 3. Comparison, 2007 vs draft (implemented provisions)

Confirmed from public summaries of the draft (values not available to me):

| Area | IS 800:2007 | Draft IS 800:2025 | Handling in code |
|---|---|---|---|
| Design philosophy | Limit state and working stress | Working stress deleted | `working_stress_design` raises `NotImplementedError` |
| Organisation | 17 sections | 24 chapters | Functions grouped and named by draft chapter |
| Table 2 | Width-to-thickness limits (e.g. 9.4/10.5/15.7 e rolled outstand) | Limits revised | 2007 limits used, `TODO(verify)` |
| Second order | General P-delta / P-small-delta checks | Dedicated cl. 11.7 | Classical amplifier as a labelled placeholder |
| Compression | Table 10 buckling classes | Updated buckling-class table | 2007 table used, `TODO(verify)` |
| LTB | alpha_LT 0.21 / 0.49 | Revised imperfection parameter for LTB | 2007 values, `alpha_LT` is an argument |
| Materials | IS 2062:1992 table | Aligned to IS 2062 (Part 1):2025; new fire/weather/seismic steels | Not implemented (data table only) |
| Anchors, corrugated webs | Not present | New annexes | Not implemented |

Unchanged-or-unknown items (safety factors, bolt and weld rules) are carried over from 2007 and flagged.

## 4. Assumptions and interpretations

1. Units are N, mm, MPa.
2. Where the draft change is unknown, 2007 values are used (flagged).
3. `cl_10_max_slenderness_ratio` returns 180/180/250/300/350/400 (2007 Table 3). The existing Osdag
   2007 function returns 180 for all six types, which looks like a bug; worth confirming separately.
4. `cl_11_7_second_order_amplification` uses 1/(1 - N/N_cr). This is my assumption, not the draft formula.
5. Effective length factors are the theoretical ideal-end values, not the code's recommended design values.
6. Slender sections raise `NotImplementedError` in bending (no effective-section model).
7. Moment strength caps at 1.2 Z_e f_y / gamma_m0 (simply supported case); the cantilever/other case is not modelled.

## 5. Challenges

- Draft PDF inaccessible from the working environment, so no clause-level reading was possible.
- The task text refers to `src/osdag_core/...`, but the default branch of the repository has
  `src/osdag/utils/common/`; the file was placed in the latter.
- The `Common` module pulls in heavy dependencies, so the `KEY_DP_FAB_*` import is guarded and tests
  load the module by path.

## 6. Tests

`tests/test_is800_2025.py` (18 tests, hand-calculated expectations, error cases included).

```
python -m pytest tests/test_is800_2025.py -v
```

## 7. Suggested next steps

1. Read the draft chapters 10, 12, 14, 15, 17 and resolve each `TODO(verify)`.
2. Replace the cl. 11.7 placeholder with the draft's expressions.
3. Extend to chapters 9 (material table), 16 (combined forces), 17 slip-critical bolts and prying.
