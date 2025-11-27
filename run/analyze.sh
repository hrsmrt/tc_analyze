#!/bin/bash

# ============================================================================
# TC Analysis Pipeline Script
# ============================================================================
# より柔軟に解析を実行できるスクリプト
#
# 注意: setting.jsonがあるディレクトリで実行してください
#
# 使用方法:
#   sh /path/to/tc_analyze/script/analyze_all.sh [OPTIONS] [CATEGORIES...]
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
#   3d                 - 3次元解析
#   2d                 - 2次元解析
#   z_profile          - 鉛直プロファイル
#   center             - 中心位置の計算とプロット
#   vortex_region      - 渦領域解析 (3d, 2d, z_profile)
#   azim               - 方位平均解析
#   azim_eliassen      - 方位平均解析 (Eliassen)
#   azim_eq_momentum_u - 方位平均解析 (運動量方程式 u)
#   azim_eq_momentum_w - 方位平均解析 (運動量方程式 w)
#   azim_q8            - 方位平均解析 (Q8)
#   sums               - 合計解析
#   symmetrisity       - 対称性解析
#   z_profile_q4       - 鉛直プロファイル (Q4)
#   all                - 全てのカテゴリ (デフォルト)
#
# 例:
#   cd /path/to/your/workdir  # setting.jsonがあるディレクトリに移動
#   sh $WORK/tc_analyze/script/analyze.sh                        # 全て実行
#   sh $WORK/tc_analyze/script/analyze.sh --style dark_background # スタイル指定
#   sh $WORK/tc_analyze/script/analyze.sh center 3d              # 一部のみ実行
#   sh $WORK/tc_analyze/script/analyze.sh --dry-run center       # ドライラン
#   sh $WORK/tc_analyze/script/analyze.sh --log ./logs/run       # ログファイル出力
#   nohup sh $WORK/tc_analyze/script/analyze.sh -s $style --log ./log01 & # バックグラウンド実行+ログ
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
  sh /path/to/tc_analyze/script/analyze_all.sh [OPTIONS] [CATEGORIES...]

オプション:
  -s, --style STYLE     matplotlibスタイル (default, dark_background, 等)
  -d, --dry-run         実行せずにコマンドのみ表示
  -h, --help            このヘルプを表示
  -l, --list            利用可能なカテゴリ一覧を表示
  -v, --verbose         詳細な出力（実行ファイルの出力を表示）
  --log PREFIX          ログファイルを出力 (PREFIX_stdout.log, PREFIX_stderr.log)
  --stop-on-error       エラーが発生したら停止 (デフォルト: 継続)

カテゴリ:
  3d                 - 3次元解析
  2d                 - 2次元解析
  z_profile          - 鉛直プロファイル
  center             - 中心位置の計算とプロット
  vortex_region      - 渦領域解析 (3d, 2d, z_profile)
  azim               - 方位平均解析
  azim_eliassen      - 方位平均解析 (Eliassen)
  azim_eq_momentum_u - 方位平均解析 (運動量方程式 u)
  azim_eq_momentum_w - 方位平均解析 (運動量方程式 w)
  azim_q8            - 方位平均解析 (Q8)
  sums               - 合計解析
  symmetrisity       - 対称性解析
  z_profile_q4       - 鉛直プロファイル (Q4)
  all                - 全てのカテゴリ (デフォルト)

例:
  cd /path/to/your/workdir  # setting.jsonがあるディレクトリに移動
  sh \$WORK/tc_analyze/script/analyze_all.sh                        # 全て実行
  sh \$WORK/tc_analyze/script/analyze_all.sh --style dark_background # スタイル指定
  sh \$WORK/tc_analyze/script/analyze_all.sh center 3d              # 一部のみ実行
  sh \$WORK/tc_analyze/script/analyze_all.sh --dry-run center       # ドライラン
  sh \$WORK/tc_analyze/script/analyze_all.sh --log ./logs/run       # ログファイル出力
  nohup sh \$WORK/tc_analyze/script/analyze_all.sh --log ./logs/run & # バックグラウンド実行+ログ
EOF
}

list_categories() {
    echo -e "${COLOR_BOLD}利用可能なカテゴリ:${COLOR_RESET}"
    echo "  3d                 - 3次元解析"
    echo "  2d                 - 2次元解析"
    echo "  z_profile          - 鉛直プロファイル"
    echo "  center             - 中心位置の計算とプロット"
    echo "  vortex_region      - 渦領域解析 (3d, 2d, z_profile)"
    echo "  azim               - 方位平均解析"
    echo "  azim_eliassen      - 方位平均解析 (Eliassen)"
    echo "  azim_eq_momentum_u - 方位平均解析 (運動量方程式 u)"
    echo "  azim_eq_momentum_w - 方位平均解析 (運動量方程式 w)"
    echo "  azim_q8            - 方位平均解析 (Q8)"
    echo "  sums               - 合計解析"
    echo "  symmetrisity       - 対称性解析"
    echo "  z_profile_q4       - 鉛直プロファイル (Q4)"
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

run_2d() {
    log_section "2D Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/whole_domain.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/2d/y_ave.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_abs_whole_domain.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/calc/ss_wind10m_max_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_max_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/calc/ss_wind10m_radial_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/2d/plot/ss_wind10m_radial_plot.py ${STYLE}"
}

run_3d() {
    log_section "3D Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/spatial/3d/whole_domain.sh"
    run_cmd "python ${TC_ANALYZE}/3d/streamplot_whole_domain.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/whole_domain_wind_uv_abs_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/ms_wind_radial_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/vorticity_z_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/vorticity_z_absolute_whole_domain_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/divergence_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/divergence_whole_domain_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/theta_e_calc.py"
    run_cmd "python ${TC_ANALYZE}/3d/theta_e_plot_whole_region.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/psi_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/psi_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/3d/psi_plot_r200.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/ms_dyn_radial_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_dyn_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/ms_dyn_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/3d/relative_u.py"
    run_cmd "python ${TC_ANALYZE}/3d/relative_v.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/relative_wind_radial_tangential_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_tangential_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_radial_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/calc/relative_wind_uv_abs_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/spatial/3d/plot/relative_wind_uv_abs_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/3d/cape.py ${STYLE}"
}

run_z_profile() {
    log_section "Z Profile Analysis"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/z_profile_calc.sh"
    run_cmd "sh ${TC_ANALYZE}/analysis/vertical/profile/z_profile_plot.sh"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/profile/calc/hf_calc.py"
    run_cmd "python ${TC_ANALYZE}/analysis/vertical/profile/plot/hf_plot.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/z_profile/sounding_rh_from_qv.py ${STYLE}"
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
    run_cmd "python ${TC_ANALYZE}/azim_mean/azim_plot_momentum_theta_e.py ${STYLE}"
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
    run_cmd "python ${TC_ANALYZE}/azim_mean/azim_wind_tangential_r_v.py ${STYLE}"
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
    run_cmd "python ${TC_ANALYZE}/3d/theta_e_plot_vortex_region.py ${STYLE}"
    run_cmd "python ${TC_ANALYZE}/3d/psi_plot_vortex_region.py ${STYLE}"
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
            run_3d
            ;;
        2d)
            run_2d
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
            run_3d
            run_2d
            run_z_profile
            run_center
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
