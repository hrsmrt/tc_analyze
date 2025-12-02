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
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
from PIL import Image
from st_keyup import st_keyup

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


def is_fig_directory(path: Path) -> bool:
    """
    Check if a directory contains domain folders (domain, tc_centric, center).

    Parameters
    ----------
    path : Path
        Directory to check

    Returns
    -------
    bool
        True if the directory contains at least one domain folder
    """
    if not path.exists() or not path.is_dir():
        return False

    domain_names = ['domain', 'tc_centric', 'tc-centric', 'center']
    for name in domain_names:
        if (path / name).is_dir():
            return True
    return False


# カレントディレクトリに domain, tc_centric, center などがあれば、それをFIG_DIRとして使用
if is_fig_directory(Path.cwd()):
    FIG_DIR = Path.cwd()
    PROJECT_ROOT = Path.cwd().parent
else:
    # 通常の動作: プロジェクトルートを検出
    PROJECT_ROOT = find_project_root()

    # setting.json から fig_dir を読み込む
    FIG_DIR = load_fig_dir(PROJECT_ROOT)

    # フォールバック: setting.json がない場合は fig/ を使用
    if FIG_DIR is None:
        FIG_DIR = PROJECT_ROOT / "fig"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def scan_available_plots(fig_dir_str: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Scan fig directory and find all available plots.

    Recursively searches for z-level directories (z00, z01, etc.)
    under each category, supporting arbitrary nesting depth.

    Parameters
    ----------
    fig_dir_str : str
        Figure directory path as string (for caching)

    Returns
    -------
    dict
        Nested dictionary: {domain: {category_path: [z_levels]}}
        category_path preserves the full path from category to z-level parent
    """
    fig_dir = Path(fig_dir_str)
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

    if not fig_dir.exists():
        st.warning(f"⚠️ FIG_DIR does not exist: {fig_dir}")
        return plots

    # Scan domain directories
    for domain_dir in fig_dir.iterdir():
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


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_image(fig_dir_str: str, domain: str, category: str, z_level: str, time_step: int) -> Image.Image:
    """
    Load image for specified parameters.

    Parameters
    ----------
    fig_dir_str : str
        Figure directory path as string (for caching)
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
    fig_dir = Path(fig_dir_str)
    img_path = fig_dir / domain / category / z_level / f"t{time_step:03d}.png"

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

    # キーボードリスナー（非表示の入力フィールド）
    # CSSで入力フィールドを非表示にする
    st.markdown("""
    <style>
    /* キーボード入力フィールドを非表示 */
    div[data-testid="stVerticalBlock"] > div:has(input[aria-label="keyboard_listener"]) {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # キーボードイベントをキャプチャ（debounce=50msで高速応答）
    key_pressed = st_keyup("keyboard_listener", key="keyboard_listener", debounce=50, label_visibility="hidden")

    # スキャンして利用可能なプロットを取得（キャッシュあり）
    available_plots = scan_available_plots(str(FIG_DIR))

    # プロジェクトルート情報を表示
    with st.expander("📂 Project Information", expanded=False):
        # setting.json の場所を確認
        setting_file = PROJECT_ROOT / "script" / "setting.json"
        if not setting_file.exists():
            setting_file = PROJECT_ROOT / "setting.json"

        setting_status = "✅ Found" if setting_file.exists() else "❌ Not found"

        # fig_dir のソースを表示
        if is_fig_directory(Path.cwd()):
            fig_source = "Current directory (auto-detected domain folders)"
        elif FIG_DIR == PROJECT_ROOT / "fig":
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
        # Session stateに保存
        st.session_state.domain = domain

        # Category selection
        if domain and domain in available_plots:
            category_names = list(available_plots[domain].keys())
            category = st.selectbox(
                "Category",
                category_names,
                help="Select analysis category"
            )
            # Session stateに保存
            st.session_state.category = category
        else:
            st.warning("No categories available")
            return

        # Z level selection
        if category and category in available_plots[domain]:
            z_levels = available_plots[domain][category]

            # z層の数値を抽出してスライダー用のインデックスに変換
            z_indices = [int(z[1:]) for z in z_levels]  # 'z00' -> 0

            # z_indicesをsession_stateに保存（キーボード操作用）
            st.session_state.z_indices = z_indices

            # Session state初期化（内部管理用の変数名を使用）
            if '_z_index' not in st.session_state:
                st.session_state._z_index = z_indices[0]

            # Z level control header
            st.header("🔢 Z Level Control")

            # Z level前後ボタン
            col1, col2 = st.columns(2)

            current_z_idx = z_indices.index(st.session_state._z_index) if st.session_state._z_index in z_indices else 0

            with col1:
                if st.button("⬇️ Down", key="z_down", use_container_width=True):
                    if current_z_idx > 0:
                        st.session_state._z_index = z_indices[current_z_idx - 1]
                        st.rerun()

            with col2:
                if st.button("Up ⬆️", key="z_up", use_container_width=True):
                    if current_z_idx < len(z_indices) - 1:
                        st.session_state._z_index = z_indices[current_z_idx + 1]
                        st.rerun()

            # Z levelスライダー（keyを削除してvalueだけで制御）
            z_index = st.select_slider(
                "Z Level Index",
                options=z_indices,
                value=st.session_state._z_index if st.session_state._z_index in z_indices else z_indices[0],
                help="Select vertical level"
            )

            # スライダーの値を内部状態に同期
            st.session_state._z_index = z_index

            # 選択されたインデックスに対応するz層名
            z_level = f"z{st.session_state._z_index:02d}"
            # Session stateに保存
            st.session_state.z_level = z_level
        else:
            st.warning("No z levels available")
            return

        st.markdown("---")

        # Time step selection
        time_steps = get_time_steps(domain, category, z_level)

        if not time_steps:
            st.warning(f"No time steps found for {domain}/{category}/{z_level}")
            return

        # time_stepsをsession_stateに保存（アニメーション用）
        st.session_state.time_steps = time_steps

        st.header("⏱️ Time Control")

        # Session state初期化（内部管理用の変数名を使用）
        if '_time_step' not in st.session_state:
            st.session_state._time_step = time_steps[0]
        if 'playing' not in st.session_state:
            st.session_state.playing = False

        # ボタンで値が変更された場合の処理
        current_idx = time_steps.index(st.session_state._time_step) if st.session_state._time_step in time_steps else 0

        # 前後ボタン
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅️ Prev", key="time_prev", use_container_width=True):
                if current_idx > 0:
                    st.session_state._time_step = time_steps[current_idx - 1]
                    st.rerun()

        with col2:
            if st.button("Next ➡️", key="time_next", use_container_width=True):
                if current_idx < len(time_steps) - 1:
                    st.session_state._time_step = time_steps[current_idx + 1]
                    st.rerun()

        # 時間ステップスライダー（keyを削除してvalueだけで制御）
        time_step = st.select_slider(
            "Time Step",
            options=time_steps,
            value=st.session_state._time_step if st.session_state._time_step in time_steps else time_steps[0],
            help="Select time step"
        )

        # スライダーの値を内部状態に同期（アニメーション中は同期しない）
        if not st.session_state.get('playing', False):
            st.session_state._time_step = time_step

        # アニメーション
        st.markdown("---")
        st.header("🎬 Animation")

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            play_speed = st.selectbox(
                "Speed",
                options=[0, 0.05, 0.1, 0.3, 0.5, 1.0],
                index=2,
                format_func=lambda x: "Max speed" if x == 0 else f"{x}s/frame"
            )
            # play_speedをsession_stateに保存
            st.session_state.play_speed = play_speed

        with col2:
            if st.button("▶️ Play", key="play_btn", use_container_width=True):
                st.session_state.playing = True
                st.rerun()

        with col3:
            if st.button("⏸️ Stop", key="stop_btn", use_container_width=True):
                st.session_state.playing = False
                st.rerun()

        # 情報表示
        st.markdown("---")
        st.header("ℹ️ Info")
        playing_status = st.session_state.get('playing', False)
        current_time_step = st.session_state.get('_time_step', 'Not set')
        st.info(f"""
        **Domain:** {domain}
        **Category:** {category}
        **Z Level:** {z_level}
        **Time Step:** {current_time_step}
        **Available Steps:** {len(time_steps)}
        **Playing:** {'▶️ Yes' if playing_status else '⏸️ No'}
        **Debug - Current Index:** {time_steps.index(st.session_state._time_step) if st.session_state._time_step in time_steps else 'N/A'}
        """)

    # メインエリア: 画像表示（session_stateから変数を取得）
    if all(key in st.session_state for key in ['domain', 'category', 'z_level', '_time_step']):
        domain = st.session_state.domain
        category = st.session_state.category
        z_level = st.session_state.z_level
        time_step = st.session_state._time_step

        # アニメーション処理
        if st.session_state.get('playing', False):
            # アニメーション中は、空のコンテナを作成してループで更新
            time_steps = st.session_state.time_steps
            current_idx = time_steps.index(st.session_state._time_step) if st.session_state._time_step in time_steps else 0

            # 画像情報ヘッダー用のプレースホルダー
            header_placeholder = st.empty()

            # 画像表示用のプレースホルダー
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                image_placeholder = st.empty()

            # 画像詳細用のプレースホルダー
            details_placeholder = st.empty()

            # アニメーションループ
            play_speed = st.session_state.get('play_speed', 0.1)
            for i in range(current_idx, len(time_steps)):
                t_step = time_steps[i]
                img = load_image(str(FIG_DIR), domain, category, z_level, t_step)

                if img is not None:
                    # ヘッダーを更新
                    header_placeholder.subheader(f"{domain} / {category} / {z_level} / t={t_step:03d}")

                    # 画像を更新
                    image_placeholder.image(img, use_container_width=True)

                    # 詳細情報を更新
                    with details_placeholder.expander("🔍 Image Details"):
                        st.write(f"**Size:** {img.size[0]} x {img.size[1]} pixels")
                        st.write(f"**Mode:** {img.mode}")
                        st.write(f"**Path:** `fig/{domain}/{category}/{z_level}/t{t_step:03d}.png`")

                    # 現在のtime_stepを更新
                    st.session_state._time_step = t_step

                    # プレイ速度に応じて待機
                    if play_speed > 0:
                        time.sleep(play_speed)
                else:
                    st.error(f"Image not found: {domain}/{category}/{z_level}/t{t_step:03d}.png")
                    break

                # 停止ボタンが押されたかチェック（session_stateの変更をチェック）
                if not st.session_state.get('playing', False):
                    break

            # アニメーション終了: playingをFalseにしてリロード
            st.session_state.playing = False
            st.rerun()
        else:
            # 通常の静止画表示
            img = load_image(str(FIG_DIR), domain, category, z_level, time_step)

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
    else:
        st.info("Select domain, category, and z-level from the sidebar to display images.")

    # キーボードイベント処理
    if key_pressed:
        # 矢印キーの処理
        if key_pressed == "ArrowLeft":
            # 左矢印: 前のtime step
            if 'time_steps' in st.session_state and '_time_step' in st.session_state:
                time_steps = st.session_state.time_steps
                current_idx = time_steps.index(st.session_state._time_step) if st.session_state._time_step in time_steps else 0
                if current_idx > 0:
                    st.session_state._time_step = time_steps[current_idx - 1]
                    st.rerun()

        elif key_pressed == "ArrowRight":
            # 右矢印: 次のtime step
            if 'time_steps' in st.session_state and '_time_step' in st.session_state:
                time_steps = st.session_state.time_steps
                current_idx = time_steps.index(st.session_state._time_step) if st.session_state._time_step in time_steps else 0
                if current_idx < len(time_steps) - 1:
                    st.session_state._time_step = time_steps[current_idx + 1]
                    st.rerun()

        elif key_pressed == "ArrowDown":
            # 下矢印: Z level Down (インデックスを減らす)
            if 'z_indices' in st.session_state and '_z_index' in st.session_state:
                z_indices = st.session_state.z_indices
                current_idx = z_indices.index(st.session_state._z_index) if st.session_state._z_index in z_indices else 0
                if current_idx > 0:
                    st.session_state._z_index = z_indices[current_idx - 1]
                    st.rerun()

        elif key_pressed == "ArrowUp":
            # 上矢印: Z level Up (インデックスを増やす)
            if 'z_indices' in st.session_state and '_z_index' in st.session_state:
                z_indices = st.session_state.z_indices
                current_idx = z_indices.index(st.session_state._z_index) if st.session_state._z_index in z_indices else 0
                if current_idx < len(z_indices) - 1:
                    st.session_state._z_index = z_indices[current_idx + 1]
                    st.rerun()

    # フッター
    st.markdown("---")
    st.markdown(
        "**TC Analysis Viewer** | "
        "Use sidebar to navigate through time steps and vertical levels | "
        "**Keyboard**: ⬅️➡️ Time / ⬆️⬇️ Z Level"
    )


if __name__ == "__main__":
    main()
