#!/usr/bin/env python3
"""
Fix issues in migrated azim_mean files
"""
import re
from pathlib import Path


def fix_file(filepath):
    """Fix issues in a single file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix 1: Double config references (config.config.xxx -> config.xxx)
    content = re.sub(r"config\.config\.", "config.", content)

    # Fix 2: Wrong n_jobs parameter in Parallel calls
    content = re.sub(
        r"Parallel\(config\.n_jobs=config\.n_jobs\)",
        "Parallel(n_jobs=config.n_jobs)",
        content,
    )

    # Fix 3: Replace old style argument parsing
    old_style_pattern = r"""if len\(sys\.argv\) > 1:
    mpl_style_sheet = sys\.argv\[1\]
    plt\.style\.use\(mpl_style_sheet\)
    print\(f"Using style: \{mpl_style_sheet\}"\)
else:
    print\("No style sheet specified, using default\."\)"""

    if re.search(old_style_pattern, content):
        # Add import if needed
        if "from utils.plotting import" not in content:
            content = content.replace(
                "from utils.grid import GridHandler",
                "from utils.grid import GridHandler\nfrom utils.plotting import parse_style_argument",
            )
        elif "parse_style_argument" not in content:
            content = content.replace(
                "from utils.plotting import",
                "from utils.plotting import parse_style_argument,",
            )

        # Replace the pattern
        content = re.sub(
            old_style_pattern,
            "mpl_style_sheet = parse_style_argument(arg_index=1)",
            content,
        )

    # Fix 4: Remove imports at wrong position (in docstrings)
    # Move imports that are inside docstrings to proper location
    if content.startswith("'''") or content.startswith('"""'):
        lines = content.split("\n")
        # Find end of docstring
        quote_type = "'''" if content.startswith("'''") else '"""'
        docstring_end = -1
        for i in range(1, len(lines)):
            if quote_type in lines[i]:
                docstring_end = i
                break

        if docstring_end > 0:
            # Extract imports from docstring
            imports_in_docstring = []
            for i in range(1, docstring_end):
                if lines[i].startswith("from ") or lines[i].startswith("import "):
                    imports_in_docstring.append(lines[i])
                    lines[i] = ""  # Remove from docstring

            # Find where actual imports are
            first_import_idx = -1
            for i in range(docstring_end + 1, len(lines)):
                if lines[i].startswith("import ") or lines[i].startswith("from "):
                    first_import_idx = i
                    break

            # Insert extracted imports after docstring
            if imports_in_docstring and first_import_idx < 0:
                # No imports exist, add after docstring
                for imp in reversed(imports_in_docstring):
                    lines.insert(docstring_end + 1, imp)

            content = "\n".join(lines)

    # Fix 5: Fix rgrid that wasn't properly removed
    content = re.sub(
        r"rgrid = np\.array\(\[\s*r \* config\.dx - config\.dx/2 for r in range\(int\(nr\)\)\]\)",
        "# rgrid generated via grid.create_radial_vertical_meshgrid",
        content,
    )

    # Fix 6: Clean up extra blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)

    # Fix 7: Fix undefined X variable in plot files
    if "X*1e-3, Y*1e-3" in content or "X, Y" in content:
        if (
            "X, Y = grid.create_radial_vertical_meshgrid" not in content
            and "X, Y = grid.X, grid.Y" not in content
            and "X, Y = np.meshgrid" not in content
        ):
            # Need to add X, Y definition
            if "radius = 1000e3" in content or "r_max = 1000e3" in content:
                # Find where to insert (after radius/r_max definition)
                content = re.sub(
                    r"(r_max = 1000e3|radius = 1000e3)\n",
                    r"\1\n\nX, Y = grid.create_radial_vertical_meshgrid(1000e3)\n",
                    content,
                )

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    azim_mean_dir = Path("/Users/hiroshimurata/tc_analyze/azim_mean")
    py_files = list(azim_mean_dir.rglob("*.py"))

    fixed_count = 0
    for py_file in sorted(py_files):
        if fix_file(py_file):
            print(f"✓ Fixed {py_file}")
            fixed_count += 1

    print(f"\n{'=' * 60}")
    print(f"Fixed {fixed_count}/{len(py_files)} files")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
