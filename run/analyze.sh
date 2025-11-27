#!/bin/bash

# ============================================================================
# TC Analysis Pipeline Script
# ============================================================================
# より柔軟に解析を実行できるスクリプト
#
# 注意: setting.jsonがあるディレクトリで実行してください
#
# 使用方法:
#   sh /path/to/tc_analyze/run/analyze.sh [OPTIONS] [CATEGORIES...]
#
# オプション:
#   -s, --style STYLE     matplotlibスタイル (default, dark_background, 等)
#   -d, --dry-run         実行せずにコマンドのみ表示
#   -h, --help            このヘルプを表示
#   -l, --list            利用可能なカテゴリ一覧を表示
#   -v, --verbose         詳細な出力（実行ファイルの出力を表示）
#   --log PREFIX          ログファイルを出力 (PREFIX_stdout.log, PREFIX_stderr.log)
#   --stop-on-error       エラーが発生したら停止 (デフォルト: 継続)
#
# カテゴリ:
#   3d                 - 3次元空間解析 (basic + wind)
#   3d_basic           - 3次元空間解析 基本 (中心位置非依存)
#   3d_wind            - 3次元空間解析 風成分 (中心位置依存、center後に実行)
#   2d                 - 2次元空間解析 (analysis/spatial/2d/)
#   z_profile          - 鉛直プロファイル (analysis/vertical/profile/)
#   center             - TC中心位置計算 (analysis/center/)
#   vortex_region      - 渦領域解析 (3d, 2d, z_profile)
#   azim               - 方位平均基本解析 (analysis/azimuthal/basic/)
#   azim_eliassen      - Eliassen方程式 (analysis/azimuthal/eliassen/)
#   azim_eq_momentum_u - 運動量方程式 u成分 (analysis/azimuthal/momentum/u/)
#   azim_eq_momentum_w - 運動量方程式 w成分 (analysis/azimuthal/momentum/w/)
#   azim_q8            - 8方位分割解析 (analysis/azimuthal/q8/)
#   sums               - 積算値計算 (analysis/diagnostics/sums/)
#   symmetrisity       - 対称性解析 (analysis/diagnostics/symmetrisity/)
#   z_profile_q4       - 4象限鉛直プロファイル (analysis/vertical/q4/)
#   all                - 全てのカテゴリ (デフォルト)
#
# 例:
#   cd /path/to/your/workdir  # setting.jsonがあるディレクトリに移動
#   sh $WORK/tc_analyze/run/analyze.sh                        # 全て実行
#   sh $WORK/tc_analyze/run/analyze.sh --style dark_background # スタイル指定
#   sh $WORK/tc_analyze/run/analyze.sh center 3d              # 一部のみ実行
#   sh $WORK/tc_analyze/run/analyze.sh --dry-run center       # ドライラン
#   sh $WORK/tc_analyze/run/analyze.sh --log ./logs/run       # ログファイル出力
#   nohup sh $WORK/tc_analyze/run/analyze.sh -s $style --log ./log01 & # バックグラウンド実行+ログ
# ============================================================================

set -u  # 未定義変数の使用でエラー

# ============================================================================
# TC_ANALYZEルートの検出
# ============================================================================

# $WORKが未設定の場合、スクリプトから自動検出
if [ -z "${WORK:-}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    WORK="$(cd "${SCRIPT_DIR}/../.." && pwd)"
    export WORK
    echo "[INFO] WORK環境変数が未設定のため自動検出しました: ${WORK}"
fi

TC_ANALYZE="${WORK}/tc_analyze"

# TC_ANALYZEの存在確認
if [ ! -d "${TC_ANALYZE}" ]; then
    echo "[ERROR] tc_analyzeディレクトリが見つかりません: ${TC_ANALYZE}"
    echo "        期待されるパス: ${TC_ANALYZE}"
    echo "        スクリプトの場所: $(dirname "${BASH_SOURCE[0]}")"
    exit 1
fi

# ============================================================================
# 設定
# ============================================================================

# デフォルト値
DEFAULT_STYLE="default"
STYLE="${DEFAULT_STYLE}"
DRY_RUN=false
VERBOSE=false
STOP_ON_ERROR=false
LOG_STDOUT=""
LOG_STDERR=""
CATEGORIES=()
FAILED_COMMANDS=()  # エラーが発生したコマンドを記録

# カラー出力
if [[ -t 1 ]]; then
    COLOR_RESET="\033[0m"
    COLOR_BOLD="\033[1m"
    COLOR_GREEN="\033[32m"
    COLOR_YELLOW="\033[33m"
    COLOR_RED="\033[31m"
    COLOR_BLUE="\033[34m"
else
    COLOR_RESET=""
    COLOR_BOLD=""
    COLOR_GREEN=""
    COLOR_YELLOW=""
    COLOR_RED=""
    COLOR_BLUE=""
fi

# ============================================================================
# 関数定義
# ============================================================================

show_help() {
    cat << EOF
TC Analysis Pipeline Script

注意: setting.jsonがあるディレクトリで実行してください

使用方法:
  sh /path/to/tc_analyze/run/analyze.sh [OPTIONS] [CATEGORIES...]

オプション:
  -s, --style STYLE     matplotlibスタイル (default, dark_background, 等)
  -d, --dry-run         実行せずにコマンドのみ表示
  -h, --help            このヘルプを表示
  -l, --list            利用可能なカテゴリ一覧を表示
  -v, --verbose         詳細な出力（実行ファイルの出力を表示）
  --log PREFIX          ログファイルを出力 (PREFIX_stdout.log, PREFIX_stderr.log)
  --stop-on-error       エラーが発生したら停止 (デフォルト: 継続)

カテゴリ:
  3d                 - 3次元空間解析 (basic + wind)
  3d_basic           - 3次元空間解析 基本 (中心位置非依存)
  3d_wind            - 3次元空間解析 風成分 (中心位置依存、center後に実行)
  2d                 - 2次元空間解析 (analysis/spatial/2d/)
  z_profile          - 鉛直プロファイル (analysis/vertical/profile/)
  center             - TC中心位置計算 (analysis/center/)
  vortex_region      - 渦領域解析 (3d, 2d, z_profile)
  azim               - 方位平均基本解析 (analysis/azimuthal/basic/)
  azim_eliassen      - Eliassen方程式 (analysis/azimuthal/eliassen/)
  azim_eq_momentum_u - 運動量方程式 u成分 (analysis/azimuthal/momentum/u/)
  azim_eq_momentum_w - 運動量方程式 w成分 (analysis/azimuthal/momentum/w/)
  azim_q8            - 8方位分割解析 (analysis/azimuthal/q8/)
  sums               - 積算値計算 (analysis/diagnostics/sums/)
  symmetrisity       - 対称性解析 (analysis/diagnostics/symmetrisity/)
  z_profile_q4       - 4象限鉛直プロファイル (analysis/vertical/q4/)
  all                - 全てのカテゴリ (デフォルト)

例:
  cd /path/to/your/workdir  # setting.jsonがあるディレクトリに移動
  sh \$WORK/tc_analyze/run/analyze.sh                        # 全て実行
  sh \$WORK/tc_analyze/run/analyze.sh --style dark_background # スタイル指定
  sh \$WORK/tc_analyze/run/analyze.sh center 3d              # 一部のみ実行
  sh \$WORK/tc_analyze/run/analyze.sh --dry-run center       # ドライラン
  sh \$WORK/tc_analyze/run/analyze.sh --log ./logs/run       # ログファイル出力
  nohup sh \$WORK/tc_analyze/run/analyze.sh --log ./logs/run & # バックグラウンド実行+ログ
EOF
}

list_categories() {
    echo -e "${COLOR_BOLD}利用可能なカテゴリ:${COLOR_RESET}"
    echo "  3d                 - 3次元空間解析 (basic + wind)"
    echo "  3d_basic           - 3次元空間解析 基本 (中心位置非依存)"
    echo "  3d_wind            - 3次元空間解析 風成分 (中心位置依存、center後に実行)"
    echo "  2d                 - 2次元空間解析 (basic + wind)"
    echo "  2d_basic           - 2次元空間解析 基本 (中心位置非依存)"
    echo "  2d_wind            - 2次元空間解析 風成分 (中心位置依存、center後に実行)"
    echo "  z_profile          - 鉛直プロファイル (analysis/vertical/profile/)"
    echo "  center             - TC中心位置計算 (analysis/center/)"
    echo "  vortex_region      - 渦領域解析 (3d, 2d, z_profile)"
    echo "  azim               - 方位平均基本解析 (analysis/azimuthal/basic/)"
    echo "  azim_eliassen      - Eliassen方程式 (analysis/azimuthal/eliassen/)"
    echo "  azim_eq_momentum_u - 運動量方程式 u成分 (analysis/azimuthal/momentum/u/)"
    echo "  azim_eq_momentum_w - 運動量方程式 w成分 (analysis/azimuthal/momentum/w/)"
    echo "  azim_q8            - 8方位分割解析 (analysis/azimuthal/q8/)"
    echo "  sums               - 積算値計算 (analysis/diagnostics/sums/)"
    echo "  symmetrisity       - 対称性解析 (analysis/diagnostics/symmetrisity/)"
    echo "  z_profile_q4       - 4象限鉛直プロファイル (analysis/vertical/q4/)"
    echo "  all                - 全てのカテゴリ"
}

log_info() {
    echo -e "${COLOR_GREEN}[INFO]${COLOR_RESET} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_section() {
    echo ""
    echo -e "${COLOR_BOLD}${COLOR_BLUE}========================================${COLOR_RESET}"
    echo -e "${COLOR_BOLD}${COLOR_BLUE} $1${COLOR_RESET}"
    echo -e "${COLOR_BOLD}${COLOR_BLUE}========================================${COLOR_RESET}"
}

# コマンドを実行（ドライランモード対応）
run_cmd() {
    local cmd="$1"

    # 実行中のファイル名を抽出して表示
    if [[ "${cmd}" =~ (python|sh)[[:space:]]+([^[:space:]]+\.(py|sh)) ]]; then
        local file_path="${BASH_REMATCH[2]}"
        local file_name=$(basename "${file_path}")
        echo -e "${COLOR_GREEN}→${COLOR_RESET} ${file_name}"
    fi

    if [[ "${VERBOSE}" == true ]]; then
        echo -e "${COLOR_BLUE}  >> ${cmd}${COLOR_RESET}"
    fi

    if [[ "${DRY_RUN}" == true ]]; then
        echo "[DRY-RUN] ${cmd}"
        return 0
    fi

    # 出力のリダイレクト
    if [[ -n "${LOG_STDOUT}" ]] && [[ -n "${LOG_STDERR}" ]]; then
        # ログファイルが指定されている場合
        eval "${cmd}" >> "${LOG_STDOUT}" 2>> "${LOG_STDERR}"
    elif [[ "${VERBOSE}" == true ]]; then
        # VERBOSEモードの場合は全て表示
        eval "${cmd}"
    else
        # デフォルト: 標準出力のみ抑制（エラー出力は表示）
        eval "${cmd}" > /dev/null
    fi
    local exit_code=$?

    if [[ ${exit_code} -ne 0 ]]; then
        log_error "コマンドが失敗しました (exit code: ${exit_code}): ${cmd}"

        # エラーが発生したコマンドを記録
        FAILED_COMMANDS+=("${cmd}")

        if [[ "${STOP_ON_ERROR}" == true ]]; then
            log_error "エラーにより処理を中断します"
            exit ${exit_code}
        fi
    fi

    return ${exit_code}
}

# ============================================================================
# コマンドライン引数の解析
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--style)
            STYLE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -l|--list)
            list_categories
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --log)
            LOG_STDOUT="$2_stdout.log"
            LOG_STDERR="$2_stderr.log"
            shift 2
            ;;
        --stop-on-error)
            STOP_ON_ERROR=true
            shift
            ;;
        -*)
            log_error "不明なオプション: $1"
            show_help
            exit 1
            ;;
        *)
            CATEGORIES+=("$1")
            shift
            ;;
    esac
done

# カテゴリが指定されていない場合はallをデフォルトとする
if [[ ${#CATEGORIES[@]} -eq 0 ]]; then
    CATEGORIES=("all")
fi

# ============================================================================
# 実行開始
# ============================================================================

log_section "TC解析パイプライン開始"
log_info "実行ディレクトリ: $(pwd)"
log_info "スタイル: ${STYLE}"
log_info "カテゴリ: ${CATEGORIES[*]}"
if [[ -n "${LOG_STDOUT}" ]]; then
    log_info "標準出力ログ: ${LOG_STDOUT}"
    log_info "エラー出力ログ: ${LOG_STDERR}"
fi
if [[ "${DRY_RUN}" == true ]]; then
    log_warn "ドライランモード: コマンドを実行せずに表示のみ"
fi

# ============================================================================
# カテゴリ別実行関数
# ============================================================================

run_center() {
    log_section "Center Analysis"
    run_cmd "python ${TC_ANALYZE}/analysis/center/calc/ss_slp_center_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/center/plot/ss_slp_center_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/center/ss_slp_center_velocity.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/center/mass_all.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/center/mass_under20km.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/center/mass.py ${STYLE}"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/3d/whole_domain_with_center_plot.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/whole_domain_with_center_plot.sh"
}

run_2d_basic() {
    log_section "2D Analysis - Basic (中心位置非依存)"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/whole_domain.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/y_ave.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_abs_whole_domain.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/calc/ss_wind10m_max_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_max_plot.py ${STYLE}"
}

run_2d_wind() {
    log_section "2D Analysis - Wind Components (中心位置依存)"
    # ⚠️ 注意: これらは台風中心位置に依存するため、run_center の後に実行する必要があります
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/calc/ss_wind10m_radial_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_radial_plot.py ${STYLE}"
}

run_2d() {
    # 互換性のため: run_2d は run_2d_basic と run_2d_wind を両方実行
    # ⚠️ 注意: run_2d_wind は中心位置に依存するため、run_center の後に実行してください
    run_2d_basic
    run_2d_wind
}

run_3d_basic() {
    log_section "3D Analysis - Basic (中心位置非依存)"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/3d/whole_domain.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/streamplot_whole_domain.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/whole_domain_wind_uv_abs_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/vorticity_z_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/vorticity_z_absolute_whole_domain_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/divergence_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/divergence_whole_domain_plot.py ${STYLE}"
    # オンデマンド計算に移行: theta_e は plot ファイルで直接計算
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/theta_e_plot_whole_region.py ${STYLE}"
    # オンデマンド計算に移行: psi は plot ファイルで直接計算
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/psi_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/cape.py ${STYLE}"
}

run_3d_wind() {
    log_section "3D Analysis - Wind Components (中心位置依存)"
    # ⚠️ 注意: これらは台風中心位置に依存するため、run_center の後に実行する必要があります
    # オンデマンド計算に移行: ms_wind は plot ファイルで直接計算
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_wind_radial_plot.py ${STYLE}"
    # オンデマンド計算に移行: ms_dyn は plot ファイルで直接計算（ms_wind と同じ）
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_dyn_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_dyn_radial_plot.py ${STYLE}"
    # オンデマンド計算に移行: relative_wind は plot ファイルで直接計算
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_uv_abs_plot.py ${STYLE}"
}

run_3d() {
    # 互換性のため: run_3d は run_3d_basic と run_3d_wind を両方実行
    # ⚠️ 注意: run_3d_wind は中心位置に依存するため、run_center の後に実行してください
    run_3d_basic
    run_3d_wind
}

run_z_profile() {
    log_section "Z Profile Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/z_profile_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/z_profile_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/profile/calc/hf_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/profile/plot/hf_plot.py ${STYLE}"
    # sounding_rh_from_qv.py は archive に移動済み（使用されていない）
    #run_cmd "python ${TC_ANALYZE}/analysis/vertical/profile/plot/sounding_rh_from_qv.py ${STYLE}"
}

run_sums() {
    log_section "Sums Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/diagnostics/sums/sums_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/diagnostics/sums/sums_plot.sh"
}

run_azim() {
    log_section "Azimuthal Mean Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_2d_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_2d_plot.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_3d_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_3d_plot.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_core_3d_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_core_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_core_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_wind10m_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind10m_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind10m_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_wind10m_tangential_max_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind10m_tangential_max_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_momentum_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_momentum_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_theta_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_theta_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_theta_e_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_theta_e_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_plot_momentum_theta_e.py ${STYLE}"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_pert_3d_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/basic/azim_pert_3d_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_wind_relative_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_relative_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_relative_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_relative_tangential_max_z_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_stream_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_stream_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_stream_max_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_stream2_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_stream2_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_vorticity_z_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_vorticity_z_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_vorticity_z_absolute_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_dyn_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_dyn_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_dyn_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_phy_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_phy_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_phy_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_tb_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_tb_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_tb_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_mp_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_mp_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_mp_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/calc/azim_wind_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/basic/plot/azim_wind_tangential_r_v.py ${STYLE}"
    #run_cmd "python ${TC_ANALYZE}/azim_mean/azim_wind_calc2.py"
    #run_cmd "python ${TC_ANALYZE}/azim_mean/azim_wind_radial_plot2.py ${STYLE}"
    #run_cmd "python ${TC_ANALYZE}/azim_mean/azim_wind_tangential_plot2.py ${STYLE}"
}

run_azim_eliassen() {
    log_section "Azimuthal Mean - Eliassen Analysis"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_N2_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_N2_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_I2_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_I2_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_I_prime2_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_I_prime2_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_B_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_B_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_R_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_R_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_gamma_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_gamma_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_xi_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_xi_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/calc/azim_buoyancy_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/eliassen/plot/azim_buoyancy_plot.py ${STYLE}"
}

run_azim_eq_momentum_u() {
    log_section "Azimuthal Mean - Momentum Equation (u)"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_du_dr_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_du_dr_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_du_dz_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_du_dz_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_udu_dr_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_udu_dr_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_wdu_dz_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_wdu_dz_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_centrifugal_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_centrifugal_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_coriolis_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_coriolis_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_grad_p_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_grad_p_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_gradient_wind_eq_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_gradient_wind_eq_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/calc/azim_gradient_balance_score_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/u/plot/azim_gradient_balance_score_plot.py ${STYLE}"
}

run_azim_eq_momentum_w() {
    log_section "Azimuthal Mean - Momentum Equation (w)"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/w/calc/azim_wdw_dz_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/w/plot/azim_wdw_dz_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/w/calc/azim_grad_p_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/momentum/w/plot/azim_grad_p_plot.py ${STYLE}"
}

run_azim_q8() {
    log_section "Azimuthal Mean - Q8 Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/q8/azim_q8_3d_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/azimuthal/q8/azim_q8_3d_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/q8/calc/azim_q8_wind_relative_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/q8/plot/azim_q8_wind_relative_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/azimuthal/q8/plot/azim_q8_wind_relative_tangential_plot.py ${STYLE}"
}

run_symmetrisity() {
    log_section "Symmetrisity Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/3d_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/3d_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/calc/relative_wind_radial_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/plot/relative_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/calc/relative_wind_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/diagnostics/symmetrisity/plot/relative_wind_tangential_plot.py ${STYLE}"
}

run_z_profile_q4() {
    log_section "Z Profile Q4 Analysis"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/q4/calc/vorticity_z_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/q4/plot/vorticity_z_plot.py ${STYLE}"
}

run_vortex_region() {
    log_section "Vortex Region Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/3d/vortex_region.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/3d/vortex_region_r250.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/vortex_region_wind_uv_abs_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/vorticity_z_vortex_region_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/divergence_vortex_region_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/theta_e_plot_vortex_region.py ${STYLE}"
    # オンデマンド計算に移行: psi は plot ファイルで直接計算（渦領域）
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/psi_plot_vortex_region.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/psi_plot_r200.py ${STYLE}"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/vortex_region.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_abs_vortex_region.py ${STYLE}"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/vortex_region_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/vortex_region_plot.sh"
}

# ============================================================================
# カテゴリの実行
# ============================================================================

ERROR_COUNT=0

for category in "${CATEGORIES[@]}"; do
    case "${category}" in
        3d)
            # 互換性のため: run_3d は basic と wind を両方実行
            run_3d
            ;;
        3d_basic)
            run_3d_basic
            ;;
        3d_wind)
            # ⚠️ 注意: 中心位置に依存するため、run_center の後に実行してください
            run_3d_wind
            ;;
        2d)
            run_2d
            ;;
        2d_basic)
            run_2d_basic
            ;;
        2d_wind)
            # ⚠️ 注意: 中心位置に依存するため、run_center の後に実行してください
            run_2d_wind
            ;;
        z_profile)
            run_z_profile
            ;;
        center)
            run_center
            ;;
        azim)
            run_azim
            ;;
        azim_eliassen)
            run_azim_eliassen
            ;;
        azim_eq_momentum_u)
            run_azim_eq_momentum_u
            ;;
        azim_eq_momentum_w)
            run_azim_eq_momentum_w
            ;;
        azim_q8)
            run_azim_q8
            ;;
        sums)
            run_sums
            ;;
        symmetrisity)
            run_symmetrisity
            ;;
        z_profile_q4)
            run_z_profile_q4
            ;;
        vortex_region)
            run_vortex_region
            ;;
        all)
            # 中心位置非依存の解析
            run_3d_basic
            run_2d_basic
            run_z_profile
            # ⚠️ 重要: run_center を最初に実行（中心位置計算が必要）
            run_center
            # 中心位置依存の解析
            run_3d_wind
            run_2d_wind
            run_vortex_region
            run_azim
            run_azim_eliassen
            run_azim_eq_momentum_u
            run_azim_eq_momentum_w
            run_azim_q8
            run_sums
            run_symmetrisity
            run_z_profile_q4
            ;;
        *)
            log_error "不明なカテゴリ: ${category}"
            log_info "利用可能なカテゴリは --list で確認してください"
            ERROR_COUNT=$((ERROR_COUNT + 1))
            ;;
    esac
done

# ============================================================================
# 完了メッセージ
# ============================================================================

log_section "処理完了"
log_info "終了時刻: $(date '+%Y-%m-%d %H:%M:%S')"

# エラーが発生したファイルの列挙
if [[ ${#FAILED_COMMANDS[@]} -gt 0 ]]; then
    log_section "エラーが発生したファイル"
    log_warn "合計 ${#FAILED_COMMANDS[@]} 件のエラーが発生しました"
    echo ""

    for failed_cmd in "${FAILED_COMMANDS[@]}"; do
        # コマンドからファイル名を抽出 (python/sh file.py/file.sh pattern)
        if [[ "${failed_cmd}" =~ (python|sh)[[:space:]]+([^[:space:]]+\.(py|sh)) ]]; then
            file_path="${BASH_REMATCH[2]}"
            file_name=$(basename "${file_path}")
            echo -e "  ${COLOR_RED}✗${COLOR_RESET} ${file_name}"
            if [[ "${VERBOSE}" == true ]]; then
                echo -e "    ${COLOR_BLUE}→${COLOR_RESET} ${failed_cmd}"
            fi
        else
            echo -e "  ${COLOR_RED}✗${COLOR_RESET} ${failed_cmd}"
        fi
    done
    echo ""

    log_warn "詳細なエラー内容は上記のログを確認してください"
    exit 1
fi

if [[ ${ERROR_COUNT} -gt 0 ]]; then
    log_warn "エラーが ${ERROR_COUNT} 件発生しました"
    exit 1
else
    log_info "全ての処理が正常に完了しました"
    exit 0
fi
