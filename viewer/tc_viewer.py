#!/usr/bin/env python
"""
TC Analysis Interactive Viewer

Streamlit-based viewer for browsing TC analysis plots.
Navigate through time steps and vertical levels interactively.

Usage:
    streamlit run viewer/tc_viewer.py
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
from PIL import Image

# プロジェクトのルートディレクトリを検出
def find_project_root() -> Path:
    """
    Find project root by searching for fig directory or setting.json.

    Search order:
    1. Current working directory
    2. Parent directories up to 3 levels
    3. Script's parent directory (fallback)

    Returns
    -------
    Path
        Project root directory
    """
    # 1. カレントディレクトリから探す
    cwd = Path.cwd()

    # script/setting.json があればそこをルートとする
    if (cwd / "script" / "setting.json").exists():
        return cwd

    # fig ディレクトリがあればそこをルートとする
    if (cwd / "fig").exists():
        return cwd

    # 2. 親ディレクトリを最大3階層まで探す
    current = cwd
    for _ in range(3):
        current = current.parent
        if (current / "script" / "setting.json").exists():
            return current
        if (current / "fig").exists():
            return current

    # 3. フォールバック: スクリプトの親ディレクトリ
    script_dir = Path(__file__).parent.parent
    return script_dir


def load_fig_dir(project_root: Path) -> Optional[Path]:
    """
    Load fig_dir from setting.json.

    Parameters
    ----------
    project_root : Path
        Project root directory

    Returns
    -------
    Path or None
        Figure directory path from setting.json, or None if not found
    """
    # まず script/setting.json を探す
    setting_file = project_root / "script" / "setting.json"

    if not setting_file.exists():
        # フォールバック: プロジェクトルート直下のsetting.json
        setting_file = project_root / "setting.json"

    if not setting_file.exists():
        return None

    try:
        with open(setting_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # fig_dir を取得
        fig_dir = settings.get('fig_dir')

        if fig_dir:
            fig_path = Path(fig_dir)
            # 絶対パスでなければ、プロジェクトルートからの相対パスとして解釈
            if not fig_path.is_absolute():
                fig_path = project_root / fig_path
            return fig_path

    except (json.JSONDecodeError, KeyError, OSError) as e:
        st.warning(f"Error reading setting.json: {e}")

    return None


PROJECT_ROOT = find_project_root()

# setting.json から fig_dir を読み込む
FIG_DIR = load_fig_dir(PROJECT_ROOT)

# フォールバック: setting.json がない場合は fig/ を使用
if FIG_DIR is None:
    FIG_DIR = PROJECT_ROOT / "fig"


def scan_available_plots() -> Dict[str, Dict[str, List[str]]]:
    """
    Scan fig directory and find all available plots.

    Recursively searches for z-level directories (z00, z01, etc.)
    under each category, supporting arbitrary nesting depth.

    Returns
    -------
    dict
        Nested dictionary: {domain: {category_path: [z_levels]}}
        category_path preserves the full path from category to z-level parent
    """
    plots = {}
    debug_info = []

    def find_z_levels(base_path, relative_path="", depth=0, max_depth=5):
        """
        Recursively find directories containing z-level folders.

        Parameters
        ----------
        base_path : Path
            Current directory to search
        relative_path : str
            Relative path from category root
        depth : int
            Current recursion depth
        max_depth : int
            Maximum recursion depth to prevent infinite loops

        Returns
        -------
        dict
            {relative_path: [z_levels]}
        """
        if depth > max_depth:
            return {}

        results = {}
        z_dirs = []

        # Check if this directory contains z-level folders
        for item in base_path.iterdir():
            if item.is_dir() and item.name.startswith('z'):
                z_dirs.append(item.name)

        if z_dirs:
            # Found z-level directories at this level
            results[relative_path] = sorted(z_dirs)
        else:
            # Recurse into subdirectories
            subdirs = [d for d in base_path.iterdir() if d.is_dir()]
            for subdir in subdirs:
                new_relative = f"{relative_path}/{subdir.name}" if relative_path else subdir.name
                sub_results = find_z_levels(subdir, new_relative, depth + 1, max_depth)
                results.update(sub_results)

        return results

    if not FIG_DIR.exists():
        st.warning(f"⚠️ FIG_DIR does not exist: {FIG_DIR}")
        return plots

    # Scan domain directories
    for domain_dir in FIG_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        domain_name = domain_dir.name
        plots[domain_name] = {}
        debug_info.append(f"📁 Domain: {domain_name}")

        # Scan each category
        for category_dir in domain_dir.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name
            debug_info.append(f"  📂 Category: {category_name}")

            # Recursively find z-level directories
            z_level_paths = find_z_levels(category_dir)

            for rel_path, z_dirs in z_level_paths.items():
                if rel_path:
                    full_category_name = f"{category_name}/{rel_path}"
                else:
                    full_category_name = category_name

                plots[domain_name][full_category_name] = z_dirs
                indent = "    " + "  " * rel_path.count('/')
                debug_info.append(f"{indent}✅ {rel_path or '(root)'}: {len(z_dirs)} z-levels")

            if not z_level_paths:
                debug_info.append(f"    ❌ No z-level directories found")

    # Save debug info to session state
    st.session_state.debug_scan_info = "\n".join(debug_info)

    return plots


def get_time_steps(domain: str, category: str, z_level: str) -> List[int]:
    """
    Get available time steps for a given domain/category/z_level.

    Parameters
    ----------
    domain : str
        Domain name (e.g., 'domain', 'tc-centric')
    category : str
        Category path (e.g., 'energy/total_energy', 'vortex_region')
        Can be 'category' or 'category/subcategory'
    z_level : str
        Z level (e.g., 'z00', 'z09')

    Returns
    -------
    list of int
        Available time step indices
    """
    plot_dir = FIG_DIR / domain / category / z_level

    if not plot_dir.exists():
        return []

    time_steps = []
    for png_file in plot_dir.glob("t*.png"):
        # Extract time index from filename (e.g., "t042.png" -> 42)
        try:
            t_str = png_file.stem[1:]  # Remove 't' prefix
            time_steps.append(int(t_str))
        except ValueError:
            continue

    return sorted(time_steps)


def load_image(domain: str, category: str, z_level: str, time_step: int) -> Image.Image:
    """
    Load image for specified parameters.

    Parameters
    ----------
    domain : str
        Domain name
    category : str
        Category path (can be 'category' or 'category/subcategory')
    z_level : str
        Z level
    time_step : int
        Time step index

    Returns
    -------
    PIL.Image.Image
        Loaded image
    """
    img_path = FIG_DIR / domain / category / z_level / f"t{time_step:03d}.png"

    if not img_path.exists():
        return None

    return Image.open(img_path)


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="TC Analysis Viewer",
        page_icon="🌀",
        layout="wide"
    )

    st.title("🌀 TC Analysis Interactive Viewer")

    # スキャンして利用可能なプロットを取得
    available_plots = scan_available_plots()

    # プロジェクトルート情報を表示
    with st.expander("📂 Project Information", expanded=False):
        # setting.json の場所を確認
        setting_file = PROJECT_ROOT / "script" / "setting.json"
        if not setting_file.exists():
            setting_file = PROJECT_ROOT / "setting.json"

        setting_status = "✅ Found" if setting_file.exists() else "❌ Not found"

        # fig_dir のソースを表示
        if FIG_DIR == PROJECT_ROOT / "fig":
            fig_source = "Default (fig/)"
        else:
            fig_source = f"From setting.json: fig_dir"

        st.info(f"""
        **Project Root:** `{PROJECT_ROOT}`
        **Setting File:** {setting_status} - `{setting_file if setting_file.exists() else 'N/A'}`
        **Figure Directory:** `{FIG_DIR}` ({fig_source})
        **Current Working Directory:** `{Path.cwd()}`
        **FIG_DIR exists:** {'✅ Yes' if FIG_DIR.exists() else '❌ No'}
        **Scanned domains:** {list(available_plots.keys())}
        **Total categories found:** {sum(len(cats) for cats in available_plots.values())}
        """)

        # デバッグ情報を表示
        if hasattr(st.session_state, 'debug_scan_info'):
            st.text("Directory scan details:")
            st.code(st.session_state.debug_scan_info, language="text")

    st.markdown("---")

    if not available_plots:
        st.error(f"No plots found in {FIG_DIR}")
        st.info("Run analysis scripts to generate plots first.")
        st.warning(f"""
        **Troubleshooting:**
        1. Make sure you are in a directory with `fig` folder or `script/setting.json`
        2. Check that plots have been generated
        3. Current search location: `{PROJECT_ROOT}`
        """)
        return

    # サイドバー: 選択パネル
    with st.sidebar:
        st.header("📊 Plot Selection")

        # Domain selection
        domain_names = list(available_plots.keys())
        domain = st.selectbox(
            "Domain",
            domain_names,
            help="Select analysis domain (whole domain or TC-centric)"
        )

        # Category selection
        if domain and domain in available_plots:
            category_names = list(available_plots[domain].keys())
            category = st.selectbox(
                "Category",
                category_names,
                help="Select analysis category"
            )
        else:
            st.warning("No categories available")
            return

        # Z level selection
        if category and category in available_plots[domain]:
            z_levels = available_plots[domain][category]

            # z層の数値を抽出してスライダー用のインデックスに変換
            z_indices = [int(z[1:]) for z in z_levels]  # 'z00' -> 0

            z_index = st.select_slider(
                "Z Level Index",
                options=z_indices,
                help="Select vertical level"
            )

            # 選択されたインデックスに対応するz層名
            z_level = f"z{z_index:02d}"
        else:
            st.warning("No z levels available")
            return

        st.markdown("---")

        # Time step selection
        time_steps = get_time_steps(domain, category, z_level)

        if not time_steps:
            st.warning(f"No time steps found for {domain}/{category}/{z_level}")
            return

        st.header("⏱️ Time Control")

        # 時間ステップスライダー
        time_step = st.select_slider(
            "Time Step",
            options=time_steps,
            help="Select time step"
        )

        # 前後ボタン
        col1, col2 = st.columns(2)

        current_idx = time_steps.index(time_step)

        with col1:
            if st.button("⬅️ Prev", use_container_width=True):
                if current_idx > 0:
                    st.session_state.time_step = time_steps[current_idx - 1]
                    st.rerun()

        with col2:
            if st.button("Next ➡️", use_container_width=True):
                if current_idx < len(time_steps) - 1:
                    st.session_state.time_step = time_steps[current_idx + 1]
                    st.rerun()

        # アニメーション（オプション）
        st.markdown("---")
        st.header("🎬 Animation")

        if st.button("▶️ Play Animation", use_container_width=True):
            st.info("Animation feature coming soon!")

        # 情報表示
        st.markdown("---")
        st.header("ℹ️ Info")
        st.info(f"""
        **Domain:** {domain}
        **Category:** {category}
        **Z Level:** {z_level}
        **Time Step:** {time_step}
        **Available Steps:** {len(time_steps)}
        """)

    # メインエリア: 画像表示
    img = load_image(domain, category, z_level, time_step)

    if img is not None:
        # 画像情報
        st.subheader(f"{domain} / {category} / {z_level} / t={time_step:03d}")

        # 画像表示（幅を調整可能に）
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            st.image(img, use_container_width=True)

        # 画像サイズ情報
        with st.expander("🔍 Image Details"):
            st.write(f"**Size:** {img.size[0]} x {img.size[1]} pixels")
            st.write(f"**Mode:** {img.mode}")
            st.write(f"**Path:** `fig/{domain}/{category}/{z_level}/t{time_step:03d}.png`")
    else:
        st.error(f"Image not found: {domain}/{category}/{z_level}/t{time_step:03d}.png")

    # フッター
    st.markdown("---")
    st.markdown(
        "**TC Analysis Viewer** | "
        "Use sidebar to navigate through time steps and vertical levels"
    )


if __name__ == "__main__":
    main()
