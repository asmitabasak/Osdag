"""Unit tests for is800_2025.py.

Run from the repository root:
    python -m pytest tests/test_is800_2025.py -v

The module is loaded by file path so the heavy Osdag package (Qt, sqlite, etc.)
need not be importable. Expected values are hand-calculated from the formulas.
"""
import importlib.util
import math
import pathlib

import pytest

_PATH = pathlib.Path(__file__).resolve().parents[1] / "src" / "osdag" / "utils" / "common" / "is800_2025.py"
_spec = importlib.util.spec_from_file_location("is800_2025", _PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
C = _mod.IS800_2025


def test_epsilon():
    assert C.epsilon(250) == pytest.approx(1.0)
    assert C.epsilon(410) == pytest.approx(math.sqrt(250 / 410))
    with pytest.raises(ValueError):
        C.epsilon(0)


def test_max_slenderness():
    assert [C.cl_10_max_slenderness_ratio(i) for i in range(1, 7)] == [180, 180, 250, 300, 350, 400]
    with pytest.raises(ValueError):
        C.cl_10_max_slenderness_ratio(7)


def test_classification():
    assert C.Table2_outstand_flange(9.0, 1.0, 250) == 'Plastic'
    assert C.Table2_outstand_flange(10.0, 1.0, 250) == 'Compact'
    assert C.Table2_outstand_flange(12.0, 1.0, 250) == 'Semi-compact'
    assert C.Table2_outstand_flange(20.0, 1.0, 250) == 'Slender'
    assert C.Table2_outstand_flange(8.0, 1.0, 250, 'Welded') == 'Plastic'
    assert C.Table2_web_bending(80, 1, 250) == 'Plastic'
    assert C.Table2_web_bending(130, 1, 250) == 'Slender'
    with pytest.raises(ValueError):
        C.Table2_outstand_flange(9, 1, 250, 'Cast')


def test_second_order_amplification():
    assert C.cl_11_7_second_order_amplification(0, 1000) == pytest.approx(1.0)
    assert C.cl_11_7_second_order_amplification(500, 1000) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        C.cl_11_7_second_order_amplification(1000, 1000)


def test_wsd_deleted():
    with pytest.raises(NotImplementedError):
        C.working_stress_design()


def test_tension():
    assert C.cl_13_tension_yielding_strength(1000, 250) == pytest.approx(1000 * 250 / 1.10)
    assert C.cl_13_tension_rupture_strength(1000, 410) == pytest.approx(0.9 * 1000 * 410 / 1.25)


def test_block_shear_takes_minimum():
    args = dict(A_vg=2000, A_vn=1500, A_tg=800, A_tn=600, f_u=410, f_y=250)
    t1 = 2000 * 250 / (math.sqrt(3) * 1.10) + 0.9 * 600 * 410 / 1.25
    t2 = 0.9 * 1500 * 410 / (math.sqrt(3) * 1.25) + 800 * 250 / 1.10
    assert C.cl_13_block_shear_strength(**args) == pytest.approx(min(t1, t2))


def test_imperfection_factor():
    assert C.cl_14_imperfection_factor('a') == 0.21
    assert C.cl_14_imperfection_factor('d') == 0.76
    with pytest.raises(ValueError):
        C.cl_14_imperfection_factor('e')


def test_design_compressive_stress():
    r = C.cl_14_design_compressive_strength  # sanity: simple product
    assert r(100, 150) == 15000
    res = C.cl_14_design_compressive_stress(250, 100, 0.34)
    f_cc = math.pi ** 2 * 2e5 / 100 ** 2
    lam = math.sqrt(250 / f_cc)
    phi = 0.5 * (1 + 0.34 * (lam - 0.2) + lam ** 2)
    chi = 1 / (phi + math.sqrt(phi ** 2 - lam ** 2))
    assert res['f_cc'] == pytest.approx(f_cc)
    assert res['chi'] == pytest.approx(chi)
    assert res['f_cd'] == pytest.approx(chi * 250 / 1.10)
    assert res['f_cd'] <= 250 / 1.10


def test_very_stocky_column_capped_at_yield():
    res = C.cl_14_design_compressive_stress(250, 1, 0.34)
    assert res['chi'] == pytest.approx(1.0)
    assert res['f_cd'] == pytest.approx(250 / 1.10)


def test_effective_length_factor():
    assert C.cl_14_effective_length_factor('Fixed', 'Fixed') == 0.5
    assert C.cl_14_effective_length_factor('Pinned', 'Fixed') == 0.7
    assert C.cl_14_effective_length_factor('Pinned', 'Pinned') == 1.0
    assert C.cl_14_effective_length_factor('Free', 'Fixed') == 2.0
    with pytest.raises(ValueError):
        C.cl_14_effective_length_factor('Free', 'Free')


def test_buckling_class():
    assert C.cl_14_buckling_class(100, 200, 10) == {'z-z': 'a', 'y-y': 'b'}
    assert C.cl_14_buckling_class(100, 200, 60) == {'z-z': 'b', 'y-y': 'c'}
    assert C.cl_14_buckling_class(100, 110, 10) == {'z-z': 'b', 'y-y': 'c'}
    assert C.cl_14_buckling_class(100, 200, 10, 'Welded I-section') == {'z-z': 'b', 'y-y': 'c'}
    assert C.cl_14_buckling_class(100, 100, 10, 'Hollow Section') == {'z-z': 'a', 'y-y': 'a'}
    assert C.cl_14_buckling_class(100, 100, 10, 'Hollow Section', 'Cold formed') == {'z-z': 'b', 'y-y': 'b'}
    with pytest.raises(ValueError):
        C.cl_14_buckling_class(1, 1, 1, 'Angle')


def test_shear_and_moment_strength():
    assert C.cl_15_design_shear_strength(2000, 250) == pytest.approx(2000 * 250 / (math.sqrt(3) * 1.10))
    assert C.cl_15_design_moment_strength(1e6, 1.1e6, 250, 'Plastic') == pytest.approx(1.1e6 * 250 / 1.10)
    # plastic modulus capped at 1.2 Z_e
    assert C.cl_15_design_moment_strength(1e6, 1.5e6, 250, 'Compact') == pytest.approx(1.2 * 1e6 * 250 / 1.10)
    assert C.cl_15_design_moment_strength(1e6, 1.1e6, 250, 'Semi-compact') == pytest.approx(1e6 * 250 / 1.10)
    with pytest.raises(NotImplementedError):
        C.cl_15_design_moment_strength(1, 1, 250, 'Slender')


def test_ltb():
    res = C.cl_15_ltb_design_bending_strength(250, M_cr=5e8, Z_p=1.1e6, Z_e=1.0e6)
    lam = math.sqrt(1.1e6 * 250 / 5e8)
    assert res['lambda_LT'] == pytest.approx(lam)
    assert 0 < res['chi_LT'] <= 1
    assert res['M_d'] == pytest.approx(1.1e6 * res['f_bd'])
    # a very high M_cr approaches the full plastic moment
    stiff = C.cl_15_ltb_design_bending_strength(250, M_cr=1e12, Z_p=1.1e6, Z_e=1.0e6)
    assert stiff['chi_LT'] == pytest.approx(1.0, abs=1e-3)


def test_bolt_hole_size():
    assert C.cl_17_bolt_hole_size(12) == 13
    assert C.cl_17_bolt_hole_size(20) == 22
    assert C.cl_17_bolt_hole_size(30) == 33
    assert C.cl_17_bolt_hole_size(20, 'Over-sized') == 24
    assert C.cl_17_bolt_hole_size(24, 'Over-sized') == 30
    with pytest.raises(ValueError):
        C.cl_17_bolt_hole_size(20, 'Slotted')


def test_bolt_spacing():
    assert C.cl_17_min_pitch(20) == 50
    assert C.cl_17_min_edge_end_distance(20) == pytest.approx(1.7 * 22)
    assert C.cl_17_min_edge_end_distance(20, edge_type='Rolled') == pytest.approx(1.5 * 22)


def test_bolt_capacities():
    V = C.cl_17_bolt_shear_capacity(800, 245, 303, 1)
    assert V == pytest.approx(800 / math.sqrt(3) * 245 / 1.25)
    k_b = min(40 / 66, 50 / 66 - 0.25, 800 / 410, 1.0)
    assert C.cl_17_bolt_bearing_capacity(410, 800, 10, 20, 40, 50) == pytest.approx(2.5 * k_b * 20 * 10 * 410 / 1.25)
    T = C.cl_17_bolt_tension_capacity(800, 640, 314, 245)
    assert T == pytest.approx(min(0.9 * 800 * 245, 640 * 314 * 1.25 / 1.10) / 1.25)
    assert C.cl_17_bolt_combined_utilisation(30, 60, 40, 80) == pytest.approx(0.5)


def test_welds():
    assert [C.cl_17_min_weld_size(t, 5) for t in (8, 15, 25, 40)] == [3, 5, 6, 8]
    assert C.cl_17_fillet_weld_effective_throat(10) == pytest.approx(7.0)
    assert C.cl_17_fillet_weld_effective_throat(10, 110) == pytest.approx(5.5)
    with pytest.raises(ValueError):
        C.cl_17_fillet_weld_effective_throat(10, 130)
    f_wd = C.cl_17_fillet_weld_design_stress(410)
    assert f_wd == pytest.approx(410 / (math.sqrt(3) * 1.25))
    assert C.cl_17_fillet_weld_design_stress(410, 'Field weld') == pytest.approx(410 / (math.sqrt(3) * 1.5))
    assert C.cl_17_fillet_weld_strength(100, 7, f_wd) == pytest.approx(f_wd * 700)
