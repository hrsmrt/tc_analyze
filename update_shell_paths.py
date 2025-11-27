#!/usr/bin/env python3
"""
Update paths in all .sh files to reflect new directory structure
"""
import os
import re
from pathlib import Path

# Path mappings: (old_path_pattern, new_path_template)
# new_path_template uses {type} which will be "calc" or "plot"
PATH_MAPPINGS = [
    # 2d/
    (r'\$\{?WORK\}?/tc_analyze/2d/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/spatial/2d/{type}/\1.py'),
    (r'\$WORK/tc_analyze/2d/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/spatial/2d/{type}/\1.py'),

    # 3d/
    (r'\$\{?WORK\}?/tc_analyze/3d/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/spatial/3d/{type}/\1.py'),
    (r'\$WORK/tc_analyze/3d/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/spatial/3d/{type}/\1.py'),

    # azim_mean/ (direct children -> basic/)
    (r'\$\{?WORK\}?/tc_analyze/azim_mean/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/azimuthal/basic/{type}/\1.py'),
    (r'\$WORK/tc_analyze/azim_mean/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/azimuthal/basic/{type}/\1.py'),

    # azim_mean/eliassen/
    (r'\$\{?WORK\}?/tc_analyze/azim_mean/eliassen/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/azimuthal/eliassen/{type}/\1.py'),
    (r'\$WORK/tc_analyze/azim_mean/eliassen/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/azimuthal/eliassen/{type}/\1.py'),

    # azim_mean/eq_momentum_u/
    (r'\$\{?WORK\}?/tc_analyze/azim_mean/eq_momentum_u/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/azimuthal/momentum/u/{type}/\1.py'),
    (r'\$WORK/tc_analyze/azim_mean/eq_momentum_u/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/azimuthal/momentum/u/{type}/\1.py'),

    # azim_mean/eq_momentum_w/
    (r'\$\{?WORK\}?/tc_analyze/azim_mean/eq_momentum_w/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/azimuthal/momentum/w/{type}/\1.py'),
    (r'\$WORK/tc_analyze/azim_mean/eq_momentum_w/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/azimuthal/momentum/w/{type}/\1.py'),

    # azim_q8/
    (r'\$\{?WORK\}?/tc_analyze/azim_q8/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/azimuthal/q8/{type}/\1.py'),
    (r'\$WORK/tc_analyze/azim_q8/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/azimuthal/q8/{type}/\1.py'),

    # z_profile/
    (r'\$\{?WORK\}?/tc_analyze/z_profile/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/vertical/profile/{type}/\1.py'),
    (r'\$WORK/tc_analyze/z_profile/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/vertical/profile/{type}/\1.py'),

    # z_profile_q4/
    (r'\$\{?WORK\}?/tc_analyze/z_profile_q4/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/vertical/q4/{type}/\1.py'),
    (r'\$WORK/tc_analyze/z_profile_q4/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/vertical/q4/{type}/\1.py'),

    # center/
    (r'\$\{?WORK\}?/tc_analyze/center/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/center/{type}/\1.py'),
    (r'\$WORK/tc_analyze/center/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/center/{type}/\1.py'),

    # sums/
    (r'\$\{?WORK\}?/tc_analyze/sums/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/diagnostics/sums/{type}/\1.py'),
    (r'\$WORK/tc_analyze/sums/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/diagnostics/sums/{type}/\1.py'),

    # symmetrisity/
    (r'\$\{?WORK\}?/tc_analyze/symmetrisity/([^/]+)\.py',
     r'${WORK}/tc_analyze/analysis/diagnostics/symmetrisity/{type}/\1.py'),
    (r'\$WORK/tc_analyze/symmetrisity/([^/]+)\.py',
     r'$WORK/tc_analyze/analysis/diagnostics/symmetrisity/{type}/\1.py'),
]

# Comment path mappings (for comments in .sh files)
COMMENT_MAPPINGS = [
    (r'tc_analyze/2d/', r'tc_analyze/analysis/spatial/2d/'),
    (r'tc_analyze/3d/', r'tc_analyze/analysis/spatial/3d/'),
    (r'tc_analyze/azim_mean/', r'tc_analyze/analysis/azimuthal/basic/'),
    (r'tc_analyze/azim_q8/', r'tc_analyze/analysis/azimuthal/q8/'),
    (r'tc_analyze/z_profile/', r'tc_analyze/analysis/vertical/profile/'),
    (r'tc_analyze/z_profile_q4/', r'tc_analyze/analysis/vertical/q4/'),
    (r'tc_analyze/center/', r'tc_analyze/analysis/center/'),
    (r'tc_analyze/sums/', r'tc_analyze/analysis/diagnostics/sums/'),
    (r'tc_analyze/symmetrisity/', r'tc_analyze/analysis/diagnostics/symmetrisity/'),
]

def determine_file_type(filename):
    """Determine if file is calc or plot based on filename"""
    if '_calc' in filename:
        return 'calc'
    elif '_plot' in filename or filename in ['whole_domain', 'vortex_region', 'vortex_region_r250']:
        return 'plot'
    else:
        # Default to plot for most files
        return 'plot'

def update_shell_file(filepath):
    """Update paths in a single shell file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Update comment paths first (simpler substitution)
    for old_pattern, new_pattern in COMMENT_MAPPINGS:
        content = re.sub(old_pattern, new_pattern, content)

    # Update python script paths with type determination
    for pattern, template in PATH_MAPPINGS:
        matches = list(re.finditer(pattern, content))
        for match in reversed(matches):  # Process in reverse to maintain positions
            script_name = match.group(1)
            file_type = determine_file_type(script_name)
            # Replace placeholders: \1 with script_name, {type} with file_type
            new_path = template.replace(r'\1', script_name).replace('{type}', file_type)
            content = content[:match.start()] + new_path + content[match.end():]

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Update all .sh files"""
    root = Path('/Users/hiroshimurata/tc_analyze')
    sh_files = list(root.glob('analysis/**/*.sh'))

    updated = 0
    for sh_file in sorted(sh_files):
        if update_shell_file(sh_file):
            print(f"Updated: {sh_file.relative_to(root)}")
            updated += 1
        else:
            print(f"No change: {sh_file.relative_to(root)}")

    print(f"\nTotal: {len(sh_files)} files, {updated} updated")

if __name__ == "__main__":
    main()
