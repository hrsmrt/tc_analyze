# 3dディレクトリ パス移行完了報告

**実施日**: 2025-11-25
**ステータス**: ✅ 完了

## 📊 移行結果サマリー

### 完了した作業
1. ✅ **ハードコードされたパスの移行** - 3dディレクトリ内の全Pythonファイル
   - `./data/` → `config.get_data_path()`
   - `./fig/` → `config.get_fig_path()`

2. ✅ **全ファイルの構文検証** - 計35ファイル

### 移行統計

| 項目 | 件数 |
|------|------|
| **総ファイル数** | 35 |
| **移行済みファイル** | 33 |
| **既に移行済み** | 2 (relative_wind_radial_tangential_calc.py, relative_wind_radial_plot.py) |
| **構文エラー** | 0 |

## 🎯 移行パターン

### パターン1: データ出力フォルダの定義
**変更前:**
```python
OUTPUT_FOLDER = "./data/3d/xxx/"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
```
**変更後:**
```python
OUTPUT_FOLDER = config.get_data_path("3d", "xxx")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
```

### パターン2: 図出力フォルダの定義
**変更前:**
```python
OUTPUT_DIR = "./fig/3d/xxx/yyy/"
os.makedirs(OUTPUT_DIR, exist_ok=True)
```
**変更後:**
```python
OUTPUT_DIR = config.get_fig_path("3d", "xxx", "yyy")
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

### パターン3: データ読み込み (f-string内)
**変更前:**
```python
data = np.load(f"./data/3d/xxx/t{str(t).zfill(3)}.npy")
```
**変更後:**
```python
data = np.load(f"{config.get_data_path('3d', 'xxx')}/t{str(t).zfill(3)}.npy")
```

### パターン4: 図の保存 (f-string内 - z階層付き)
**変更前:**
```python
fig.savefig(f"./fig/3d/xxx/z{z}/t{t}.png")
```
**変更後:**
```python
fig.savefig(os.path.join(OUTPUT_DIR, f"z{z}", f"t{t}.png"))
```

### パターン5: サブフォルダ作成 (z階層付き)
**変更前:**
```python
os.makedirs(f"./fig/3d/xxx/z{str(z).zfill(2)}", exist_ok=True)
```
**変更後:**
```python
os.makedirs(os.path.join(OUTPUT_DIR, f"z{str(z).zfill(2)}"), exist_ok=True)
```

### パターン6: 変数を含むパス
**変更前:**
```python
os.makedirs(str(f"./fig/3d/whole_domain/{VARNAME}"), exist_ok=True)
```
**変更後:**
```python
OUTPUT_DIR = config.get_fig_path("3d", "whole_domain", VARNAME)
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

## 📝 移行したファイル一覧

### 計算ファイル (*_calc.py)
1. psi_calc.py
2. theta_e_calc.py
3. ms_wind_radial_tangential_calc.py
4. ms_dyn_radial_tangential_calc.py
5. relative_wind_uv_abs_calc.py
6. divergence_calc.py
7. vorticity_z_calc.py
8. relative_u.py
9. relative_v.py

### プロットファイル (*_plot.py)
1. psi_plot.py
2. psi_plot_r200.py
3. psi_plot_vortex_region.py
4. ms_wind_radial_plot.py
5. ms_wind_tangential_plot.py
6. ms_dyn_radial_plot.py
7. ms_dyn_tangential_plot.py
8. divergence_whole_domain_plot.py
9. divergence_vortex_region_plot.py
10. vorticity_z_absolute_whole_domain_plot.py
11. vorticity_z_vortex_region_plot.py
12. theta_e_plot_whole_region.py
13. theta_e_plot_vortex_region.py
14. relative_wind_tangential_plot.py
15. relative_wind_uv_abs_plot.py
16. streamplot_whole_domain.py
17. whole_domain_wind_uv_abs_plot.py
18. vortex_region_wind_uv_abs_plot.py
19. whole_domain_with_center_plot.py

### その他のファイル
1. cape.py
2. vortex_region.py
3. vortex_region_r250.py
4. whole_domain.py
5. whole_domain copy.py

## 🔧 実施した手順

### 1. 自動移行スクリプトの作成
- `migrate_3d_paths.py` を作成
- 正規表現パターンマッチングで自動変換
- 18ファイルを自動移行

### 2. 手動での追加移行
- 複雑なパターン（変数を含むパスなど）を手動で修正
- 15ファイルを手動で移行

### 3. 構文検証
- 全35ファイルで `python -m py_compile` を実行
- ✅ 全ファイルが構文チェックを通過

## ✅ 検証済み項目

- [x] 全35ファイルの移行完了
- [x] 全ファイルの構文チェック通過
- [x] ハードコードされたパス (`./data/`, `./fig/`) の完全削除を確認
- [x] `config.get_data_path()` と `config.get_fig_path()` への統一

## 📈 期待される効果

### 保守性の向上
- **集中管理**: データ・図の保存先を一箇所で管理
- **環境依存性の削減**: 異なる環境でもパスの変更が容易
- **一貫性**: 全ファイルで同じパス取得方法を使用

### 開発効率の向上
- **パス変更**: 1箇所の修正で全ファイルに反映
- **デバッグ**: パス関連のエラーを容易に特定・修正
- **テスト**: 一時ディレクトリへの切り替えが容易

### 具体例
1. **出力先の変更**
   - 移行前: 35ファイルを個別修正 → 1-2時間
   - 移行後: `utils/config.py`の2行のみ → 1分

2. **テスト環境への切り替え**
   - 移行前: 各ファイルのパスを手動変更 → エラーのリスク大
   - 移行後: 環境変数またはconfig設定のみ → 確実・安全

## 🎉 まとめ

このパス移行により、3dディレクトリ内の全35ファイルが統一的なパス管理手法に移行されました：

1. ✅ **ハードコードされたパスの完全削除** (100%)
2. ✅ **config.get_data_path()とconfig.get_fig_path()への統一** (100%)
3. ✅ **構文エラーゼロ** (100%)
4. ✅ **保守性の大幅向上**
5. ✅ **環境依存性の削減**

プロジェクトの他のディレクトリ（2d/, azim_mean/, center/, z_profile/など）でも同様の移行を実施することで、さらなる統一化と保守性向上が期待できます。

---

**移行実施者**: Claude Code
**最終更新**: 2025-11-25
