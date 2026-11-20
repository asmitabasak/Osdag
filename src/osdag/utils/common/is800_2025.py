"""Module for Indian Standard, IS 800 : 2025 (Draft, Fourth Revision, CED 07 (27869)WC)

Companion to ``is800_2007.py``. Follows the same conventions: one class of static
methods, ``cl_<chapter>_<topic>`` naming, Args/Returns/Note docstrings and a
partial-safety-factor table held as a class-level dict.

IMPORTANT - STATUS OF VALUES
    The draft text was not directly accessible while this module was written.
    Structural changes that are publicly documented (see ``DRAFT_CHANGES``) are
    reflected in the layout. Wherever the draft's numeric change could not be
    confirmed, the IS 800:2007 value is used and the line is marked
    ``TODO(verify)`` together with the draft chapter to check. No draft-specific
    number has been invented. Resolve every TODO(verify) against the draft before
    production use.

Chapter map (draft 2025 -> 2007 section):
    9  Materials                    -> 2
    10 General design requirements  -> 3
    11 Methods of structural analysis -> 4   (new cl. 11.7, second-order)
    12 Limit state design           -> 5   (WSD, 2007 Sec. 11, deleted)
    13 Tension members              -> 6
    14 Compression members          -> 7
    15 Members in bending           -> 8
    17 Connections                  -> 10
"""
import math

try:  # inside the Osdag package
    from ...Common import KEY_DP_FAB_SHOP, KEY_DP_FAB_FIELD
except ImportError:  # standalone use (e.g. unit tests loading this file directly)
    KEY_DP_FAB_SHOP = 'Shop Weld'
    KEY_DP_FAB_FIELD = 'Field weld'


# Documented draft-vs-2007 differences (public sources); used by the report.
DRAFT_CHANGES = {
    "working_stress_design": "Deleted. Only limit state design is retained (2007 Sec. 11 -> 'Deleted').",
    "structure": "24 chapters (2007: 17 sections).",
    "table_2": "Limiting width-to-thickness ratios revised (values not confirmed here).",
    "cl_11_7": "New dedicated second-order provisions (P-delta, P-small-delta).",
    "chapter_14": "Updated buckling-class table for compression members.",
    "chapter_15": "Revised width-to-thickness limits and an imperfection parameter for LTB.",
    "cl_10_3": "Separate fire-load provision.",
    "materials": "Tensile property table aligned to IS 2062 (Part 1):2025; new fire-, weather- and "
                 "seismic-resistant steels (IS 15103, IS 11587, IS 15962).",
    "annex_g": "Metal anchors in concrete (new); corrugated-web girders (Annex H).",
    "new_chapters": "Chapter 23 Sustainable steel construction.",
}


class IS800_2025(object):
    """Perform calculations on steel design as per Draft IS 800:2025

    Units: N, mm, MPa (N/mm^2) unless stated otherwise.
    """

    # ==========================================================================
    """    CHAPTER 9     MATERIALS   """
    # ==========================================================================

    # Modulus of elasticity, MPa. TODO(verify): Chapter 9
    E = 2.0e5
    # Poisson's ratio, elastic range. TODO(verify): Chapter 9
    MU = 0.3

    # ==========================================================================
    """    CHAPTER 10     GENERAL DESIGN REQUIREMENTS   """
    # ==========================================================================

    @staticmethod
    def epsilon(f_y):
        """Calculate the stress ratio epsilon = sqrt(250 / f_y) used in classification.

        Args:
            f_y: Yield stress in MPa (float)

        Returns:
            epsilon (float)

        Note:
            Reference: IS 800:2007 Table 2. TODO(verify): same definition in draft Table 2.
        """
        if f_y <= 0:
            raise ValueError("f_y must be positive")
        return math.sqrt(250.0 / f_y)

    # Limiting slenderness ratios (2007 Table 3). TODO(verify): draft Chapter 10 table.
    # Types follow is800_2007.cl_3_8_max_slenderness_ratio.
    cl_10_max_slenderness_table = {1: 180, 2: 180, 3: 250, 4: 300, 5: 350, 6: 400}

    @staticmethod
    def cl_10_max_slenderness_ratio(Type=1):
        """Maximum effective slenderness ratio of a member.

        Args:
            Type: 1) compression member from dead + imposed loads,
                  2) tension member with reversal of direct stress (not wind/seismic),
                  3) compression only from wind/earthquake combinations,
                  4) compression flange of a beam against LTB,
                  5) tie in roof truss/bracing possibly reversing into compression under wind/EQ,
                  6) member always in tension (other than pre-tensioned) (int)

        Returns:
            Limiting slenderness ratio (int)

        Note:
            Values are those of IS 800:2007 Table 3 (cl. 3.8). The Osdag 2007 module
            returns 180 for every type; this implementation follows the printed table.
            TODO(verify): draft Chapter 10.
        """
        try:
            return IS800_2025.cl_10_max_slenderness_table[Type]
        except KeyError:
            raise ValueError("Type must be an integer from 1 to 6")

    @staticmethod
    def Table2_outstand_flange(width, thickness, f_y, section_type='Rolled'):
        """Classify an outstand element of a compression flange (I/H/channel).

        Args:
            width: Outstand width b (or b/2 convention, as per draft figure) in mm (float)
            thickness: Flange thickness in mm (float)
            f_y: Yield stress in MPa (float)
            section_type: 'Rolled' or 'Welded' (str)

        Returns:
            Section class: 'Plastic', 'Compact', 'Semi-compact' or 'Slender' (str)

        Note:
            Limits are the IS 800:2007 Table 2 values (rolled 9.4/10.5/15.7, welded 8.4/9.4/13.6
            times epsilon). The draft revises Table 2. TODO(verify): replace _LIMITS.
        """
        limits = {'Rolled': (9.4, 10.5, 15.7), 'Welded': (8.4, 9.4, 13.6)}
        if section_type not in limits:
            raise ValueError("section_type must be 'Rolled' or 'Welded'")
        return IS800_2025._classify(width / thickness, limits[section_type], f_y)

    @staticmethod
    def Table2_web_bending(depth, thickness, f_y):
        """Classify the web of an I/H section in pure bending (neutral axis at mid-depth).

        Note:
            2007 Table 2 limits: 84/105/126 times epsilon. TODO(verify) against the draft.
        """
        return IS800_2025._classify(depth / thickness, (84.0, 105.0, 126.0), f_y)

    @staticmethod
    def _classify(ratio, limits, f_y):
        eps = IS800_2025.epsilon(f_y)
        plastic, compact, semi = limits
        if ratio <= plastic * eps:
            return 'Plastic'
        if ratio <= compact * eps:
            return 'Compact'
        if ratio <= semi * eps:
            return 'Semi-compact'
        return 'Slender'

    # ==========================================================================
    """    CHAPTER 11     METHODS OF STRUCTURAL ANALYSIS   """
    # ==========================================================================

    @staticmethod
    def cl_11_7_second_order_amplification(N, N_cr):
        """Classical amplification factor for first-order moments.

        Args:
            N: Design axial compression in N (float)
            N_cr: Elastic critical buckling load in N (float)

        Returns:
            Amplification factor, 1 / (1 - N / N_cr), at least 1.0 (float)

        Note:
            ASSUMPTION: the draft's new cl. 11.7 formulas were not accessible. This is the
            textbook amplifier, provided as a placeholder. TODO(verify): replace with the
            draft's P-delta / P-small-delta expressions and neglect criteria.
        """
        if N_cr <= 0:
            raise ValueError("N_cr must be positive")
        if N >= N_cr:
            raise ValueError("N must be less than N_cr (member is unstable)")
        return max(1.0, 1.0 / (1.0 - N / N_cr))

    # ==========================================================================
    """    CHAPTER 12     LIMIT STATE DESIGN   """
    # ==========================================================================

    # Partial safety factors for materials. WSD removed in the draft; limit state only.
    # Values = 2007 Table 5. TODO(verify): draft Chapter 12 table.
    cl_12_Table_safety_factors = {
        "gamma_m0": {'yielding': 1.10, 'buckling': 1.10},
        "gamma_m1": {'ultimate_stress': 1.25},
        "gamma_mf": {KEY_DP_FAB_SHOP: 1.25, KEY_DP_FAB_FIELD: 1.25},
        "gamma_mb": {KEY_DP_FAB_SHOP: 1.25, KEY_DP_FAB_FIELD: 1.25},
        "gamma_mr": {KEY_DP_FAB_SHOP: 1.25, KEY_DP_FAB_FIELD: 1.25},
        "gamma_mw": {KEY_DP_FAB_SHOP: 1.25, KEY_DP_FAB_FIELD: 1.50},
    }

    @staticmethod
    def working_stress_design(*args, **kwargs):
        """Working stress design was deleted in the draft IS 800:2025."""
        raise NotImplementedError("Working Stress Design is discontinued in draft IS 800:2025")

    # ==========================================================================
    """    CHAPTER 13     DESIGN OF TENSION MEMBERS   """
    # ==========================================================================

    @staticmethod
    def cl_13_tension_yielding_strength(A_g, f_y):
        """Design strength of a tension member governed by yielding of the gross section.

        Args:
            A_g: Gross area in mm^2 (float)
            f_y: Yield stress in MPa (float)

        Returns:
            T_dg in N (float)

        Note:
            2007 reference: cl. 6.2, T_dg = A_g f_y / gamma_m0. TODO(verify): draft clause no.
        """
        gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['yielding']
        return A_g * f_y / gamma_m0

    @staticmethod
    def cl_13_tension_rupture_strength(A_n, f_u):
        """Design strength of a plate governed by rupture of the net section.

        Args:
            A_n: Net area in mm^2 (float)
            f_u: Ultimate stress in MPa (float)

        Returns:
            T_dn in N (float)

        Note:
            2007 reference: cl. 6.3.1, T_dn = 0.9 A_n f_u / gamma_m1. TODO(verify): draft.
        """
        gamma_m1 = IS800_2025.cl_12_Table_safety_factors["gamma_m1"]['ultimate_stress']
        return 0.9 * A_n * f_u / gamma_m1

    @staticmethod
    def cl_13_block_shear_strength(A_vg, A_vn, A_tg, A_tn, f_u, f_y):
        """Block shear strength of a bolted connection.

        Args:
            A_vg, A_vn: Gross / net area in shear along the bolt line, mm^2 (float)
            A_tg, A_tn: Gross / net area in tension perpendicular to the load, mm^2 (float)
            f_u, f_y: Ultimate / yield stress in MPa (float)

        Returns:
            Block shear strength in N, the lesser of the two failure paths (float)

        Note:
            2007 reference: cl. 6.4.1. TODO(verify): draft.
        """
        gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['yielding']
        gamma_m1 = IS800_2025.cl_12_Table_safety_factors["gamma_m1"]['ultimate_stress']
        T_db1 = A_vg * f_y / (math.sqrt(3) * gamma_m0) + 0.9 * A_tn * f_u / gamma_m1
        T_db2 = 0.9 * A_vn * f_u / (math.sqrt(3) * gamma_m1) + A_tg * f_y / gamma_m0
        return min(T_db1, T_db2)

    # ==========================================================================
    """    CHAPTER 14     DESIGN OF COMPRESSION MEMBERS   """
    # ==========================================================================

    # Imperfection factors for buckling classes a-d (2007 Table 7). TODO(verify): draft.
    cl_14_imperfection_factors = {'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}

    @staticmethod
    def cl_14_imperfection_factor(buckling_class):
        """Imperfection factor alpha for a buckling class ('a', 'b', 'c' or 'd')."""
        try:
            return IS800_2025.cl_14_imperfection_factors[buckling_class]
        except KeyError:
            raise ValueError("buckling_class must be one of 'a', 'b', 'c', 'd'")

    @staticmethod
    def cl_14_design_compressive_stress(f_y, effective_slenderness_ratio, imperfection_factor,
                                        modulus_of_elasticity=None, gamma_m0=None):
        """Design compressive stress f_cd for flexural buckling.

        Args:
            f_y: Yield stress in MPa (float)
            effective_slenderness_ratio: KL/r (float)
            imperfection_factor: alpha (float)
            modulus_of_elasticity: E in MPa, default 2e5 (float)
            gamma_m0: partial safety factor, default from the safety-factor table (float)

        Returns:
            dict with f_cc (Euler stress), lambda (non-dimensional slenderness), phi,
            chi (stress reduction factor), f_cd (design stress, capped at f_y / gamma_m0)

        Note:
            Same formulation as 2007 cl. 7.1.2.1: f_cd = chi f_y / gamma_m0 <= f_y / gamma_m0.
            TODO(verify): draft Chapter 14 (the buckling-class table is updated).
        """
        E = IS800_2025.E if modulus_of_elasticity is None else modulus_of_elasticity
        if gamma_m0 is None:
            gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['buckling']
        if effective_slenderness_ratio <= 0:
            raise ValueError("effective_slenderness_ratio must be positive")
        f_cc = math.pi ** 2 * E / effective_slenderness_ratio ** 2
        lam = math.sqrt(f_y / f_cc)
        phi = 0.5 * (1 + imperfection_factor * (lam - 0.2) + lam ** 2)
        chi = min(1.0, 1.0 / (phi + math.sqrt(phi ** 2 - lam ** 2)))
        f_cd = chi * f_y / gamma_m0
        return {'f_cc': f_cc, 'lambda': lam, 'phi': phi, 'chi': chi, 'f_cd': f_cd}

    @staticmethod
    def cl_14_design_compressive_strength(A_e, f_cd):
        """Design compressive strength P_d = A_e * f_cd in N."""
        return A_e * f_cd

    @staticmethod
    def cl_14_effective_length_factor(end_1='Fixed', end_2='Fixed'):
        """Effective length factor K for prismatic members (2007 Table 11, idealised ends).

        Args:
            end_1, end_2: 'Fixed', 'Pinned' or 'Free' (str)

        Returns:
            K, so that KL = K * unsupported length (float)

        Note:
            Ideal end conditions only (theoretical values 0.5, 0.7, 0.8, 1.0, 2.0);
            the code's recommended design values are higher. TODO(verify): draft Annex D.
        """
        ends = tuple(sorted((end_1, end_2)))
        table = {('Fixed', 'Fixed'): 0.5, ('Fixed', 'Pinned'): 0.7,
                 ('Pinned', 'Pinned'): 1.0, ('Fixed', 'Free'): 2.0}
        try:
            return table[ends]
        except KeyError:
            raise ValueError("Unsupported combination of end conditions: %s" % (ends,))

    @staticmethod
    def cl_14_buckling_class(b, h, t_f, cross_section='Rolled I-sections', section_type='Hot rolled'):
        """Buckling class about z-z and y-y.

        Note:
            2007 Table 10 logic. The draft updates this table, so TODO(verify) every branch.
            For t_f > 100 mm (rolled) class d is assumed, as in the Osdag 2007 module.
        """
        if cross_section == 'Rolled I-sections':
            if h / b > 1.2:
                if t_f <= 40:
                    return {'z-z': 'a', 'y-y': 'b'}
                if t_f <= 100:
                    return {'z-z': 'b', 'y-y': 'c'}
                return {'z-z': 'd', 'y-y': 'd'}
            if t_f <= 100:
                return {'z-z': 'b', 'y-y': 'c'}
            return {'z-z': 'd', 'y-y': 'd'}
        if cross_section == 'Welded I-section':
            if t_f <= 40:
                return {'z-z': 'b', 'y-y': 'c'}
            return {'z-z': 'c', 'y-y': 'd'}
        if cross_section == 'Hollow Section':
            cls = 'a' if section_type == 'Hot rolled' else 'b'
            return {'z-z': cls, 'y-y': cls}
        raise ValueError("Unknown cross_section: %s" % cross_section)

    # ==========================================================================
    """    CHAPTER 15     DESIGN OF MEMBERS SUBJECTED TO BENDING   """
    # ==========================================================================

    @staticmethod
    def cl_15_design_shear_strength(A_v, f_y):
        """Design shear strength V_d = A_v f_y / (sqrt(3) gamma_m0) in N (2007 cl. 8.4)."""
        gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['yielding']
        return A_v * f_y / (math.sqrt(3) * gamma_m0)

    @staticmethod
    def cl_15_design_moment_strength(Z_e, Z_p, f_y, section_class='Plastic'):
        """Design bending strength of a laterally supported section.

        Args:
            Z_e, Z_p: Elastic / plastic section modulus in mm^3 (float)
            f_y: Yield stress in MPa (float)
            section_class: 'Plastic', 'Compact' or 'Semi-compact' (str)

        Returns:
            M_d in N-mm (float)

        Note:
            2007 cl. 8.2.1.2: M_d = beta_b Z_p f_y / gamma_m0 capped at 1.2 Z_e f_y / gamma_m0
            (1.5 for cantilever/simply supported is not modelled here). Slender sections are
            not handled. TODO(verify): draft Chapter 15 limits and shear interaction.
        """
        gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['yielding']
        if section_class == 'Slender':
            raise NotImplementedError("Slender sections need effective-section properties")
        if section_class == 'Semi-compact':
            return Z_e * f_y / gamma_m0
        return min(Z_p * f_y / gamma_m0, 1.2 * Z_e * f_y / gamma_m0)

    @staticmethod
    def cl_15_ltb_design_bending_strength(f_y, M_cr, Z_p, Z_e, section_class='Plastic',
                                          alpha_LT=0.21, gamma_m0=None):
        """Design bending strength of a laterally unsupported beam.

        Args:
            f_y: Yield stress in MPa (float)
            M_cr: Elastic critical moment in N-mm (float)
            Z_p, Z_e: Plastic / elastic section moduli in mm^3 (float)
            section_class: 'Plastic'/'Compact' use Z_p, 'Semi-compact' uses Z_e (str)
            alpha_LT: imperfection parameter (0.21 rolled, 0.49 welded in 2007) (float)

        Returns:
            dict with lambda_LT, phi_LT, chi_LT, f_bd (MPa), M_d (N-mm)

        Note:
            2007 cl. 8.2.2. The draft introduces a revised LTB imperfection parameter;
            TODO(verify) alpha_LT values and the elastic buckling annex (Annex E).
        """
        if gamma_m0 is None:
            gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['buckling']
        beta_b = 1.0 if section_class in ('Plastic', 'Compact') else Z_e / Z_p
        lam = math.sqrt(beta_b * Z_p * f_y / M_cr)
        phi = 0.5 * (1 + alpha_LT * (lam - 0.2) + lam ** 2)
        chi = min(1.0, 1.0 / (phi + math.sqrt(phi ** 2 - lam ** 2)))
        f_bd = chi * f_y / gamma_m0
        M_d = beta_b * Z_p * f_bd
        return {'lambda_LT': lam, 'phi_LT': phi, 'chi_LT': chi, 'f_bd': f_bd, 'M_d': M_d}

    # ==========================================================================
    """    CHAPTER 17     CONNECTIONS   """
    # ==========================================================================

    @staticmethod
    def cl_17_bolt_hole_size(d, bolt_hole_type='Standard'):
        """Bolt hole diameter in mm (2007 Table 19; TODO(verify): draft Chapter 17).

        Standard clearance: 1 mm for d <= 14, 2 mm for 16 <= d <= 24, 3 mm above 24.
        Over-sized clearance: 3 mm (d <= 14), 4 mm (16-22), 6 mm (24), 8 mm above 24.
        """
        if d <= 0:
            raise ValueError("d must be positive")
        if bolt_hole_type == 'Standard':
            clearance = 1.0 if d <= 14 else (2.0 if d <= 24 else 3.0)
        elif bolt_hole_type == 'Over-sized':
            clearance = 3.0 if d <= 14 else (4.0 if d <= 22 else (6.0 if d <= 24 else 8.0))
        else:
            raise ValueError("bolt_hole_type must be 'Standard' or 'Over-sized'")
        return d + clearance

    @staticmethod
    def cl_17_min_pitch(d):
        """Minimum pitch/gauge = 2.5 d (2007 cl. 10.2.2). TODO(verify): draft."""
        return 2.5 * d

    @staticmethod
    def cl_17_min_edge_end_distance(d, bolt_hole_type='Standard', edge_type='Sheared or hand flame cut'):
        """Minimum edge/end distance (2007 cl. 10.2.4.2): 1.7 d_0 sheared/hand flame cut,
        1.5 d_0 rolled/machine-flame cut/sawn/planed. TODO(verify): draft."""
        d_0 = IS800_2025.cl_17_bolt_hole_size(d, bolt_hole_type)
        if edge_type == 'Sheared or hand flame cut':
            return 1.7 * d_0
        return 1.5 * d_0

    @staticmethod
    def cl_17_bolt_shear_capacity(f_ub, A_nb, A_sb, n_n, n_s=0, gamma_mb=None):
        """Design shear capacity of a bearing bolt, V_dsb (2007 cl. 10.3.3).

        V_nsb = f_ub / sqrt(3) * (n_n A_nb + n_s A_sb); V_dsb = V_nsb / gamma_mb.
        TODO(verify): draft (may change factors for long joints / large grip).
        """
        if gamma_mb is None:
            gamma_mb = IS800_2025.cl_12_Table_safety_factors["gamma_mb"][KEY_DP_FAB_SHOP]
        return f_ub / math.sqrt(3) * (n_n * A_nb + n_s * A_sb) / gamma_mb

    @staticmethod
    def cl_17_bolt_bearing_capacity(f_u, f_ub, t, d, e, p, bolt_hole_type='Standard', gamma_mb=None):
        """Design bearing capacity of a bearing bolt, V_dpb (2007 cl. 10.3.4).

        V_npb = 2.5 k_b d t f_u, with
        k_b = min(e/(3 d_0), p/(3 d_0) - 0.25, f_ub/f_u, 1.0).
        TODO(verify): draft.
        """
        if gamma_mb is None:
            gamma_mb = IS800_2025.cl_12_Table_safety_factors["gamma_mb"][KEY_DP_FAB_SHOP]
        d_0 = IS800_2025.cl_17_bolt_hole_size(d, bolt_hole_type)
        k_b = min(e / (3 * d_0), p / (3 * d_0) - 0.25, f_ub / f_u, 1.0)
        return 2.5 * k_b * d * t * f_u / gamma_mb

    @staticmethod
    def cl_17_bolt_tension_capacity(f_ub, f_yb, A_sb, A_n, gamma_mb=None, gamma_m0=None):
        """Design tension capacity of a bearing bolt, T_db (2007 cl. 10.3.5).

        T_nb = min(0.9 f_ub A_n, f_yb A_sb gamma_mb / gamma_m0); T_db = T_nb / gamma_mb.
        TODO(verify): draft.
        """
        if gamma_mb is None:
            gamma_mb = IS800_2025.cl_12_Table_safety_factors["gamma_mb"][KEY_DP_FAB_SHOP]
        if gamma_m0 is None:
            gamma_m0 = IS800_2025.cl_12_Table_safety_factors["gamma_m0"]['yielding']
        T_nb = min(0.9 * f_ub * A_n, f_yb * A_sb * gamma_mb / gamma_m0)
        return T_nb / gamma_mb

    @staticmethod
    def cl_17_bolt_combined_utilisation(V_sb, V_db, T_b, T_db):
        """Interaction ratio (V_sb/V_db)^2 + (T_b/T_db)^2; must be <= 1.0 (2007 cl. 10.3.6)."""
        return (V_sb / V_db) ** 2 + (T_b / T_db) ** 2

    @staticmethod
    def cl_17_min_weld_size(part1_thickness, part2_thickness):
        """Minimum fillet weld size in mm from the thicker part (2007 Table 21).

        <=10: 3, 10-20: 5, 20-32: 6, 32-50: 8 (first run) / 10. TODO(verify): draft.
        """
        t = max(part1_thickness, part2_thickness)
        if t <= 10:
            return 3
        if t <= 20:
            return 5
        if t <= 32:
            return 6
        return 8

    @staticmethod
    def cl_17_fillet_weld_effective_throat(fillet_size, fusion_face_angle=90):
        """Effective throat thickness t_t = K * s, K by fusion face angle (2007 cl. 10.5.3.2).

        K: 60-90 -> 0.7, 91-100 -> 0.65, 101-106 -> 0.6, 107-113 -> 0.55, 114-120 -> 0.5.
        TODO(verify): draft.
        """
        a = fusion_face_angle
        if 60 <= a <= 90:
            K = 0.70
        elif a <= 100:
            K = 0.65
        elif a <= 106:
            K = 0.60
        elif a <= 113:
            K = 0.55
        elif a <= 120:
            K = 0.50
        else:
            raise ValueError("Fusion face angle must be between 60 and 120 degrees")
        return K * fillet_size

    @staticmethod
    def cl_17_fillet_weld_design_stress(f_u, fabrication=KEY_DP_FAB_SHOP):
        """Design stress of a fillet weld f_wd = f_u / (sqrt(3) gamma_mw), MPa (2007 cl. 10.5.7.1.1)."""
        gamma_mw = IS800_2025.cl_12_Table_safety_factors["gamma_mw"][fabrication]
        return f_u / (math.sqrt(3) * gamma_mw)

    @staticmethod
    def cl_17_fillet_weld_strength(effective_length, throat_thickness, f_wd):
        """Design strength of a fillet weld, N = f_wd * t_t * l_w."""
        return f_wd * throat_thickness * effective_length
