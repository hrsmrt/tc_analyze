#!/usr/bin/env python3
"""
Update analyze.sh with new directory structure paths
"""
import re

# Path mapping: (old_pattern, calc_replacement, plot_replacement, sh_replacement)
PATH_MAPPINGS = [
    # 3d
    (r'\$\{TC_ANALYZE\}/3d/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/spatial/3d/calc/\1'),
    (r'\$\{TC_ANALYZE\}/3d/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/spatial/3d/plot/\1'),
    (r'\$\{TC_ANALYZE\}/3d/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/spatial/3d/\1'),

    # 2d
    (r'\$\{TC_ANALYZE\}/2d/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/spatial/2d/calc/\1'),
    (r'\$\{TC_ANALYZE\}/2d/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/spatial/2d/plot/\1'),
    (r'\$\{TC_ANALYZE\}/2d/(whole_domain|vortex_region|y_ave|slp_tppn|ss_wind10m_abs[^/]+)\.py',
     r'${TC_ANALYZE}/analysis/spatial/2d/plot/\1.py'),
    (r'\$\{TC_ANALYZE\}/2d/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/spatial/2d/\1'),

    # azim_mean basic (direct children)
    (r'\$\{TC_ANALYZE\}/azim_mean/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/basic/calc/\1'),
    (r'\$\{TC_ANALYZE\}/azim_mean/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/basic/plot/\1'),
    (r'\$\{TC_ANALYZE\}/azim_mean/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/azimuthal/basic/\1'),

    # azim_mean/eliassen
    (r'\$\{TC_ANALYZE\}/azim_mean/eliassen/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/\1'),
    (r'\$\{TC_ANALYZE\}/azim_mean/eliassen/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/\1'),

    # azim_mean/eq_momentum_u
    (r'\$\{TC_ANALYZE\}/azim_mean/eq_momentum_u/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/\1'),
    (r'\$\{TC_ANALYZE\}/azim_mean/eq_momentum_u/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/\1'),

    # azim_mean/eq_momentum_w
    (r'\$\{TC_ANALYZE\}/azim_mean/eq_momentum_w/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/momentum/w/calc/\1'),
    (r'\$\{TC_ANALYZE\}/azim_mean/eq_momentum_w/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/momentum/w/plot/\1'),

    # azim_q8
    (r'\$\{TC_ANALYZE\}/azim_q8/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/q8/calc/\1'),
    (r'\$\{TC_ANALYZE\}/azim_q8/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/azimuthal/q8/plot/\1'),
    (r'\$\{TC_ANALYZE\}/azim_q8/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/azimuthal/q8/\1'),

    # z_profile
    (r'\$\{TC_ANALYZE\}/z_profile/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/vertical/profile/calc/\1'),
    (r'\$\{TC_ANALYZE\}/z_profile/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/vertical/profile/plot/\1'),
    (r'\$\{TC_ANALYZE\}/z_profile/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/vertical/profile/\1'),

    # z_profile_q4
    (r'\$\{TC_ANALYZE\}/z_profile_q4/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/vertical/q4/calc/\1'),
    (r'\$\{TC_ANALYZE\}/z_profile_q4/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/vertical/q4/plot/\1'),

    # center - calc/plot files
    (r'\$\{TC_ANALYZE\}/center/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/center/calc/\1'),
    (r'\$\{TC_ANALYZE\}/center/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/center/plot/\1'),
    # center - other files
    (r'\$\{TC_ANALYZE\}/center/(mass[^/]*|find_lows|track_low|ss_slp_center_velocity)\.py',
     r'${TC_ANALYZE}/analysis/center/\1.py'),

    # sums
    (r'\$\{TC_ANALYZE\}/sums/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/diagnostics/sums/calc/\1'),
    (r'\$\{TC_ANALYZE\}/sums/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/diagnostics/sums/plot/\1'),
    (r'\$\{TC_ANALYZE\}/sums/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/diagnostics/sums/\1'),

    # symmetrisity
    (r'\$\{TC_ANALYZE\}/symmetrisity/([^/]+_calc\.py)',
     r'${TC_ANALYZE}/analysis/diagnostics/symmetrisity/calc/\1'),
    (r'\$\{TC_ANALYZE\}/symmetrisity/([^/]+_plot\.py)',
     r'${TC_ANALYZE}/analysis/diagnostics/symmetrisity/plot/\1'),
    (r'\$\{TC_ANALYZE\}/symmetrisity/([^/]+\.sh)',
     r'${TC_ANALYZE}/analysis/diagnostics/symmetrisity/\1'),
]

def update_analyze_sh(filepath):
    """Update analyze.sh with new paths"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Apply all path mappings
    for pattern, replacement in PATH_MAPPINGS:
        content = re.sub(pattern, replacement, content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    # Count changes
    changes = sum(1 for i, (old, new) in enumerate(zip(original_content.split('\n'),
                                                         content.split('\n'))) if old != new)

    print(f"Updated {filepath}")
    print(f"  Changed {changes} lines")
    return changes

if __name__ == "__main__":
    filepath = "/Users/hiroshimurata/tc_analyze/run/analyze.sh"
    changes = update_analyze_sh(filepath)
    print(f"\nTotal: {changes} lines modified")
