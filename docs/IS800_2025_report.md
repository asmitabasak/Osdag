# Report: `is800_2025.py` - Draft IS 800:2025 module for Osdag

**Author:** Asmita Basak  |  **Branch:** `feature/is800-2025-draft`  |  **Module:** `src/osdag/utils/common/is800_2025.py`  |  **Tests:** `tests/test_is800_2025.py` (18 passing)

## 1. Summary and scope

This work adds an `IS800_2025` class that mirrors the structure and style of the existing `is800_2007.py`: one class of static methods, `cl_<chapter>_<topic>` naming, Args/Returns/Note docstrings, and partial safety factors in a class-level dictionary. It covers 29 functions across tension, compression, bending and bolted/welded connections, organised by the draft's chapter layout.

**Main limitation (stated up front).** I could not read the draft's clause text: the shared Drive and BIS links were blocked in my working environment, and the public summaries name changed provisions but give no formulas or values. Therefore:

- The module's *structure* follows the draft (24 chapters).
- Where a draft change is publicly documented, it is reflected in structure or behaviour (e.g. working stress design now raises `NotImplementedError`).
- Where a numeric change could not be confirmed, the **IS 800:2007 value is used and the line is tagged `TODO(verify)`**, naming the draft chapter to check. **No draft-specific number was invented.** There are 28 such tags.

The code is therefore a tested, documented scaffold that is correct for the 2007 formulation and ready to take the draft's values, not a verified implementation of the draft.

## 2. Approach

1. Read `is800_2007.py` to extract conventions (class layout, docstring format, how clause numbers appear in names, the `gamma_*` table).
2. Collected publicly documented differences of the draft from public summaries (Section 4).
3. Mapped each 2007 section to its draft chapter and implemented a representative, self-contained set of functions per chapter.
4. Wrote hand-calculated pytest cases for every function, including error paths.
5. Marked every unconfirmed value `TODO(verify)` so no assumption is silent.

Chapter map used (draft chapter -> 2007 section): 9 Materials -> 2; 10 General design -> 3; 11 Analysis -> 4; 12 Limit state -> 5; 13 Tension -> 6; 14 Compression -> 7; 15 Bending -> 8; 17 Connections -> 10. Working stress design (2007 Sec. 11) has no counterpart.

## 3. Functions implemented

Units: N, mm, MPa. Symbols follow IS 800.

| Chapter | Function | Formula / rule | 2007 source |
|---|---|---|---|
| 9 | `E`, `MU` | E = 2.0e5 MPa, mu = 0.3 | Sec. 2 |
| 10 | `epsilon(f_y)` | sqrt(250 / f_y) | Table 2 |
| 10 | `cl_10_max_slenderness_ratio(Type)` | 180, 180, 250, 300, 350, 400 for types 1-6 | Table 3 |
| 10 | `Table2_outstand_flange` | b/t vs 9.4, 10.5, 15.7 e (rolled); 8.4, 9.4, 13.6 e (welded) | Table 2 |
| 10 | `Table2_web_bending` | d/t vs 84, 105, 126 e | Table 2 |
| 11 | `cl_11_7_second_order_amplification` | 1 / (1 - N/N_cr), placeholder | new in draft |
| 12 | `cl_12_Table_safety_factors` | gamma_m0 = 1.10, gamma_m1 = 1.25, gamma_mb/mf/mr = 1.25, gamma_mw = 1.25 (shop) / 1.50 (field) | Table 5 |
| 12 | `working_stress_design` | raises `NotImplementedError` | deleted |
| 13 | `cl_13_tension_yielding_strength` | T_dg = A_g f_y / gamma_m0 | 6.2 |
| 13 | `cl_13_tension_rupture_strength` | T_dn = 0.9 A_n f_u / gamma_m1 | 6.3.1 |
| 13 | `cl_13_block_shear_strength` | min of two paths (shear yield + tension rupture; shear rupture + tension yield) | 6.4.1 |
| 14 | `cl_14_imperfection_factor` | a, b, c, d -> 0.21, 0.34, 0.49, 0.76 | Table 7 |
| 14 | `cl_14_design_compressive_stress` | f_cc = pi^2 E/(KL/r)^2; lambda = sqrt(f_y/f_cc); phi = 0.5[1 + alpha(lambda - 0.2) + lambda^2]; chi = 1/(phi + sqrt(phi^2 - lambda^2)) <= 1; f_cd = chi f_y / gamma_m0 | 7.1.2.1 |
| 14 | `cl_14_design_compressive_strength` | P_d = A_e f_cd | 7.1.2 |
| 14 | `cl_14_effective_length_factor` | ideal-end K: 0.5, 0.7, 1.0, 2.0 | Table 11 |
| 14 | `cl_14_buckling_class` | rolled I, welded I, hollow; by h/b and t_f | Table 10 |
| 15 | `cl_15_design_shear_strength` | V_d = A_v f_y / (sqrt(3) gamma_m0) | 8.4 |
| 15 | `cl_15_design_moment_strength` | M_d = Z_p f_y / gamma_m0 <= 1.2 Z_e f_y / gamma_m0; semi-compact uses Z_e | 8.2.1.2 |
| 15 | `cl_15_ltb_design_bending_strength` | lambda_LT = sqrt(beta_b Z_p f_y / M_cr); chi_LT as above; M_d = beta_b Z_p f_bd | 8.2.2 |
| 17 | `cl_17_bolt_hole_size` | d + clearance (standard 1/2/3 mm; over-sized 3/4/6/8 mm) | Table 19 |
| 17 | `cl_17_min_pitch` | 2.5 d | 10.2.2 |
| 17 | `cl_17_min_edge_end_distance` | 1.7 d_0 (sheared/hand flame cut), 1.5 d_0 (rolled/machine cut) | 10.2.4.2 |
| 17 | `cl_17_bolt_shear_capacity` | V_dsb = f_ub/sqrt(3) (n_n A_nb + n_s A_sb) / gamma_mb | 10.3.3 |
| 17 | `cl_17_bolt_bearing_capacity` | V_dpb = 2.5 k_b d t f_u / gamma_mb; k_b = min(e/3d_0, p/3d_0 - 0.25, f_ub/f_u, 1) | 10.3.4 |
| 17 | `cl_17_bolt_tension_capacity` | T_db = min(0.9 f_ub A_n, f_yb A_sb gamma_mb/gamma_m0) / gamma_mb | 10.3.5 |
| 17 | `cl_17_bolt_combined_utilisation` | (V_sb/V_db)^2 + (T_b/T_db)^2 <= 1 | 10.3.6 |
| 17 | `cl_17_min_weld_size` | 3, 5, 6, 8 mm by thicker part | Table 21 |
| 17 | `cl_17_fillet_weld_effective_throat` | K s, K = 0.70 to 0.50 by fusion face angle (60-120 deg) | 10.5.3.2 |
| 17 | `cl_17_fillet_weld_design_stress` | f_wd = f_u / (sqrt(3) gamma_mw) | 10.5.7.1.1 |
| 17 | `cl_17_fillet_weld_strength` | f_wd t_t l_w | 10.5.7 |

## 4. Comparison: IS 800:2007 vs Draft IS 800:2025

Differences below are those reported in public summaries of the draft. "Confirmed" means the *existence* of the change is reported; the numeric effect was not readable, so the code keeps the 2007 value where marked.

| Area | IS 800:2007 | Draft IS 800:2025 | Status | Handling in code |
|---|---|---|---|---|
| Design philosophy | Limit state and working stress | Working stress design deleted | Confirmed | `working_stress_design` raises `NotImplementedError` |
| Organisation | 17 sections | 24 chapters | Confirmed | Functions named and grouped by draft chapter |
| Width-to-thickness limits | Table 2 as in Section 3 | Table 2 revised | Change confirmed, values unknown | 2007 limits, `TODO(verify)` |
| Second-order effects | General P-delta guidance in Sec. 4 | New dedicated cl. 11.7 | Confirmed | Textbook amplifier as a labelled placeholder |
| Compression members | Table 10 buckling classes | Updated buckling-class table | Change confirmed, values unknown | 2007 table, `TODO(verify)` |
| Lateral-torsional buckling | alpha_LT 0.21 (rolled) / 0.49 (welded) | Revised imperfection parameter | Change confirmed, value unknown | 2007 values; `alpha_LT` is a parameter |
| Materials | IS 2062:1992-based table | Aligned to IS 2062 (Part 1):2025; adds fire-, weather- and seismic-resistant steels | Confirmed | Not implemented (data table only) |
| Fire | Referenced generally | Separate fire-load provision (cl. 10.3) | Confirmed | Not implemented |
| New content | - | Metal anchors (Annex G), corrugated-web girders (Annex H), sustainable steel construction (Ch. 23) | Confirmed | Not implemented |
| Partial safety factors, bolts, welds | Table 5, Sec. 10 | Not confirmed either way | Unknown | 2007 values, `TODO(verify)` |

**Modified:** Table 2, buckling classes, LTB parameter, materials table. **New:** cl. 11.7, fire provision, anchors, corrugated webs, Ch. 23. **Deleted:** working stress design.

## 5. Worked examples (generated by running the module)

| Case | Inputs | Result |
|---|---|---|
| Tension yielding | A_g = 3000 mm^2, f_y = 250 MPa | T_dg = 681.8 kN |
| Tension rupture | A_n = 2400 mm^2, f_u = 410 MPa | T_dn = 708.5 kN |
| Column, buckling class b | f_y = 250, KL/r = 100, alpha = 0.34 | f_cc = 197.4 MPa, lambda = 1.125, phi = 1.291, chi = 0.520, f_cd = 118.2 MPa; with A_e = 5000 mm^2, P_d = 591.2 kN |
| Classification | flange b/t = 7.5; web d/t = 100 (f_y = 250) | Plastic; Compact |
| Shear | A_v = 2000 mm^2, f_y = 250 | V_d = 262.4 kN |
| Laterally supported bending | Z_e = 1.0e6, Z_p = 1.1e6 mm^3, f_y = 250 | M_d = 250.0 kN-m (Z_p f_y / gamma_m0 governs; the 1.2 Z_e cap would allow 272.7 kN-m) |
| LTB | M_cr = 5e8 N-mm, same section | lambda_LT = 0.742, chi_LT = 0.827, f_bd = 188.0 MPa, M_d = 206.8 kN-m |
| Bolt M20 (8.8) | f_ub = 800, f_u = 410, e = 40, p = 50, t = 10 | hole 22 mm; V_dsb = 90.5 kN (A_nb = 314 mm^2); V_dpb = 83.2 kN; T_db = 141.1 kN |
| Fillet weld | s = 6 mm, f_u = 410, shop, l_w = 100 mm | t_t = 4.2 mm; f_wd = 189.4 MPa; strength = 79.5 kN |

The unit tests check the same formulas against independently hand-calculated expressions; they do not hard-code these exact figures.

## 6. Assumptions and interpretations

1. Units are N, mm and MPa throughout.
2. Where the draft change is unknown, 2007 values are used and flagged (Section 7).
3. `cl_10_max_slenderness_ratio` returns the printed Table 3 values (180/180/250/300/350/400). The existing Osdag 2007 function appears to return 180 for every type; this looks unintended and is worth confirming separately.
4. `cl_11_7_second_order_amplification` uses 1/(1 - N/N_cr). This is my assumption and is **not** the draft's expression.
5. Effective length factors are the theoretical ideal-end values, not the code's recommended design values.
6. Slender sections raise `NotImplementedError` in bending, since no effective-section model is implemented.
7. Moment strength caps at 1.2 Z_e f_y / gamma_m0 (simply supported case); the cantilever case is not modelled and shear interaction is not applied.
8. In a bearing-bolt hole, over-sized clearance is 3/4/6/8 mm for d <= 14, 16-22, 24 and > 24 mm respectively.
9. The `KEY_DP_FAB_*` constants are imported from `Common` when run inside Osdag; a fallback keeps the module importable standalone.

## 7. Open items to verify against the draft

| Draft chapter | Items to check | Where in code |
|---|---|---|
| 9 | E, mu, material property table | `E`, `MU` |
| 10 | Table 2 limits (flange and web); Table 3 slenderness limits; epsilon definition | `Table2_*`, `cl_10_*` |
| 11 | Clause 11.7 expressions and neglect criteria | `cl_11_7_*` |
| 12 | Partial safety factor table | `cl_12_Table_safety_factors` |
| 13 | Clause numbers and any change to yielding, rupture, block shear | `cl_13_*` |
| 14 | Imperfection factors, buckling-class table, effective length factors | `cl_14_*` |
| 15 | Moment limits, shear interaction, alpha_LT, elastic critical moment annex | `cl_15_*` |
| 17 | Hole sizes, spacing limits, bolt capacities, weld size and throat | `cl_17_*` |

Running `grep -n "TODO(verify)" src/osdag/utils/common/is800_2025.py` lists all 28 locations.

## 8. Design decisions

- **Static methods on one class**, matching `is800_2007.py`, so call sites can switch codes with minimal change.
- **Failure over guessing:** invalid inputs raise `ValueError`, and unsupported cases (slender sections, WSD) raise `NotImplementedError` rather than returning a plausible number.
- **Results as dicts where several intermediates matter** (`f_cc`, `lambda`, `phi`, `chi`, `f_cd`), because Osdag reports these in design output.
- **Parameters over hard-coding** for values the draft is reported to change (e.g. `alpha_LT`, `gamma_m0`), so updating them does not require editing formulas.

## 9. Testing

`tests/test_is800_2025.py` has 18 tests with hand-calculated expectations, covering every function, boundary cases (class limits, `chi` capped at 1, over-sized holes) and error paths. The module is loaded by file path, so Qt and the rest of Osdag are not needed.

```
python -m pytest tests/test_is800_2025.py -v
```

## 10. Challenges

- The draft was inaccessible from the working environment, so no clause-level reading was possible. This is the largest limitation.
- The task refers to `src/osdag_core/...`, but the repository's default branch uses `src/osdag/utils/common/`; the file was placed in the latter.
- Importing `Common` pulls in heavy dependencies, so the import is guarded and tests load the module by path.
- With draft clause numbers unknown, naming by chapter (rather than by clause) was the only honest option.

## 11. Next steps

1. Read draft chapters 10, 12, 14, 15 and 17 and resolve every `TODO(verify)`, updating tests to the draft's numbers.
2. Replace the cl. 11.7 placeholder with the draft's expressions.
3. Add the material table, combined-force checks, slip-critical bolts and prying action.
4. Rename functions to the draft's exact clause numbers once known.

## References

- IS 800:2007, *General Construction in Steel - Code of Practice* (reference implementation: `is800_2007.py`).
- Draft IS 800:2025, CED 07, BIS (public summaries only; full text not read).
- Osdag repository: https://github.com/osdag-admin/Osdag
