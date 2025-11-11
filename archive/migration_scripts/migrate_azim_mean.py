#!/usr/bin/env python3
"""
Migrate azim_mean files to use utils.config and utils.grid
"""
import os
import re
from pathlib import Path

def migrate_file(filepath):
    """Migrate a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Skip already migrated files
    if 'from utils.config import AnalysisConfig' in content:
        print(f"Skipping {filepath} - already migrated")
        return False

    # Skip if no setting.json
    if "with open('setting.json'" not in content:
        print(f"Skipping {filepath} - no setting.json")
        return False

    print(f"Migrating {filepath}...")

    # Determine if this is a plot file (needs plotting utils)
    is_plot_file = '_plot' in filepath.name
    needs_grid = 'X, Y = np.meshgrid' in content or 'grid.X' in content or 'vgrid = np.loadtxt' in content

    # Pattern 1: Remove setting.json block
    setting_pattern = r"# ファイルを開いてJSONを読み込む\n.*?with open\('setting\.json'.*?\n.*?setting = json\.load\(f\)\n(.*?(?:config\.\w+ = .*?\n|glevel = .*?\n|triangle_size = .*?\n|dt = .*?\n|time_list = .*?\n))*"
    content = re.sub(setting_pattern, '', content, flags=re.DOTALL)

    # Pattern 2: Remove individual setting variables
    lines_to_remove = [
        r"with open\('setting\.json'.*?\n",
        r"setting = json\.load\(f\)\n",
        r"glevel = setting\['glevel'\]\n",
        r"config\.nt = setting\['config\.nt'\]\n",
        r"nt = setting\['nt'\]\n",
        r"dt = setting\['dt_output'\]\n",
        r"config\.dt_hour = int\(dt / 3600\)\n",
        r"dt_hour = int\(dt / 3600\)\n",
        r"triangle_size = setting\['triangle_size'\]\n",
        r"config\.n_jobs = setting\.get\(\"config\.n_jobs\", 1\)\n",
        r"n_jobs = setting\.get\(\"n_jobs\", 1\)\n",
        r"config\.nx = 2 \*\* glevel\n",
        r"nx = 2 \*\* glevel\n",
        r"config\.ny = 2 \*\* glevel\n",
        r"ny = 2 \*\* glevel\n",
        r"config\.nz = 74\n",
        r"nz = 74\n",
        r"config\.x_width = triangle_size\n",
        r"x_width = triangle_size\n",
        r"config\.y_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5\n",
        r"y_width = triangle_size \* 0\.5 \* 3\.0 \*\* 0\.5\n",
        r"config\.dx = config\.x_width / config\.nx\n",
        r"dx = x_width / nx\n",
        r"config\.dy = config\.y_width / config\.ny\n",
        r"dy = y_width / ny\n",
        r"config\.input_folder = setting\['config\.input_folder'\]\n",
        r"input_folder = setting\['input_folder'\]\n",
        r"time_list = config\.time_list\n",
    ]

    for pattern in lines_to_remove:
        content = re.sub(pattern, '', content)

    # Remove unused imports
    if 'sys.argv' not in content and 'sys.path' not in content:
        content = re.sub(r'import sys\n', '', content)
    if 'json.load' not in content and 'json.dumps' not in content:
        content = re.sub(r'import json\n', '', content)

    # Remove script_dir lines
    content = re.sub(r'script_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\n', '', content)
    content = re.sub(r'sys\.path\.append\(.*?\)\n', '', content)

    # Add imports after initial comments
    lines = content.split('\n')
    import_insert_idx = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('#'):
            import_insert_idx = i
            break

    # Build import block
    imports_to_add = []
    if 'from utils.config import AnalysisConfig' not in content:
        imports_to_add.append('from utils.config import AnalysisConfig')
    if needs_grid and 'from utils.grid import GridHandler' not in content:
        imports_to_add.append('from utils.grid import GridHandler')
    if is_plot_file and 'from utils.plotting import parse_style_argument' not in content:
        if 'mpl_style_sheet = parse_style_argument' in content:
            imports_to_add.append('from utils.plotting import parse_style_argument')

    if imports_to_add:
        # Find where to insert (after existing imports)
        last_import_idx = import_insert_idx
        for i in range(import_insert_idx, len(lines)):
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                last_import_idx = i
            elif lines[i].strip() and not lines[i].strip().startswith('#'):
                break

        # Insert new imports
        for imp in reversed(imports_to_add):
            lines.insert(last_import_idx + 1, imp)

    content = '\n'.join(lines)

    # Add config initialization after imports
    if 'config = AnalysisConfig()' not in content:
        # Find position after imports
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
            elif insert_pos > 0 and line.strip() == '':
                insert_pos = i + 1
                break
            elif insert_pos > 0 and not line.startswith('import ') and not line.startswith('from ') and line.strip():
                break

        config_init = '\nconfig = AnalysisConfig()'
        if needs_grid:
            config_init += '\ngrid = GridHandler(config)\n'

        lines.insert(insert_pos, config_init)
        content = '\n'.join(lines)

    # Replace variable references
    replacements = [
        (r'\bnx\b', 'config.nx'),
        (r'\bny\b', 'config.ny'),
        (r'\bnz\b', 'config.nz'),
        (r'\bnt\b', 'config.nt'),
        (r'\bdt_hour\b', 'config.dt_hour'),
        (r'\bdx\b', 'config.dx'),
        (r'\bdy\b', 'config.dy'),
        (r'\bx_width\b', 'config.x_width'),
        (r'\by_width\b', 'config.y_width'),
        (r'\binput_folder\b', 'config.input_folder'),
        (r'\bn_jobs\b', 'config.n_jobs'),
        (r"setting\['vgrid_filepath'\]", 'config.vgrid_filepath'),
        (r'\btime_list\b', 'config.time_list'),
    ]

    for pattern, replacement in replacements:
        # Be careful not to replace in strings or comments
        content = re.sub(pattern, replacement, content)

    # Replace vgrid loading
    content = re.sub(
        r'vgrid = np\.loadtxt\(f?["\']?\{?config\.vgrid_filepath\}?["\']?\)',
        'vgrid = grid.create_vertical_grid()',
        content
    )

    # Replace rgrid patterns
    content = re.sub(
        r'rgrid = np\.array\(\[\s*r \* config\.dx - config\.dx/2 for r in range\(int\(nr\)\)\]\)',
        '# rgrid generated via grid.create_radial_vertical_meshgrid or grid.create_radial_grid',
        content
    )

    # Replace X,Y meshgrid for radial-vertical plots
    if re.search(r'X\s*,\s*Y\s*=\s*np\.meshgrid\(rgrid\s*,\s*vgrid\)', content):
        # Try to find radius value
        radius_match = re.search(r'radius\s*=\s*(\d+e\d+)', content)
        if radius_match:
            radius = radius_match.group(1)
            content = re.sub(
                r'X\s*,\s*Y\s*=\s*np\.meshgrid\(rgrid\s*,\s*vgrid\)',
                f'X, Y = grid.create_radial_vertical_meshgrid({radius})',
                content
            )

    # Replace plot ticks setting
    if is_plot_file:
        # Add import for set_azimuthal_plot_ticks if needed
        if 'set_xticks([0,250e3,500e3,750e3,1000e3]' in content or 'set_xticks([0e3,250e3,500e3,750e3,1000e3]' in content:
            if 'from utils.plotting import set_azimuthal_plot_ticks' not in content:
                content = content.replace(
                    'from utils.plotting import parse_style_argument',
                    'from utils.plotting import parse_style_argument, set_azimuthal_plot_ticks'
                )

            # Replace the ticks setting
            pattern = r'ax\.set_ylim\(\[0,\s*20e3\]\)\s*\n\s*ax\.set_xticks\(\[0e?3?,250e3,500e3,750e3,1000e3\],\["","","","",""\]\)\s*\n\s*ax\.set_yticks\(\[0,5e3,10e3,15e3,20e3\],\["","","","",""\]\)'
            replacement = 'set_azimuthal_plot_ticks(ax, r_max=1000e3, z_max=20e3)'
            content = re.sub(pattern, replacement, content)

    # Clean up extra blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Write back
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Migrated {filepath}")
        return True
    else:
        print(f"✗ No changes for {filepath}")
        return False

def main():
    azim_mean_dir = Path('/Users/hiroshimurata/tc_analyze/azim_mean')

    # Get all Python files
    py_files = list(azim_mean_dir.rglob('*.py'))

    migrated_count = 0
    for py_file in sorted(py_files):
        if migrate_file(py_file):
            migrated_count += 1

    print(f"\n{'='*60}")
    print(f"Migration complete: {migrated_count}/{len(py_files)} files migrated")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
