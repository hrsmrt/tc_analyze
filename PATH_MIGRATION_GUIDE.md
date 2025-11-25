# パス設定のカスタマイズガイド

**作成日**: 2025-11-25
**バージョン**: 1.0

## 概要

このガイドでは、データと図の入出力パスを`setting.json`で設定可能にする方法を説明します。

## 背景

以前は、データの入出力パスが各スクリプトにハードコードされていました：
- データ入力: `./data/`
- 図出力: `./fig/`

これにより、異なるディレクトリ構造を使用する際にコードを修正する必要がありました。

## 新機能

### 1. setting.json での設定

`setting.json` に以下の設定項目が追加されました：

```json
{
    "data_dir": "./data",
    "fig_dir": "./fig"
}
```

### 2. AnalysisConfig クラスの拡張

`utils/config.py` に以下が追加されました：

#### プロパティ
- `config.data_dir`: データディレクトリのパス
- `config.fig_dir`: 図ディレクトリのパス

#### ヘルパーメソッド
- `config.get_data_path(*paths)`: データディレクトリ配下のパスを生成
- `config.get_fig_path(*paths)`: 図ディレクトリ配下のパスを生成

## 移行方法

### パターン1: データ出力パス（計算スクリプト）

**移行前:**
```python
# 出力フォルダの作成
FOLDER_RADIAL = "./data/3d/relative_wind_radial/"
FOLDER_TANGENTIAL = "./data/3d/relative_wind_tangential/"
os.makedirs(FOLDER_RADIAL, exist_ok=True)
os.makedirs(FOLDER_TANGENTIAL, exist_ok=True)
```

**移行後:**
```python
# 出力フォルダの作成
FOLDER_RADIAL = config.get_data_path("3d", "relative_wind_radial")
FOLDER_TANGENTIAL = config.get_data_path("3d", "relative_wind_tangential")
os.makedirs(FOLDER_RADIAL, exist_ok=True)
os.makedirs(FOLDER_TANGENTIAL, exist_ok=True)
```

### パターン2: データ入力パス

**移行前:**
```python
# データ読み込み
data_u = np.load(f"./data/3d/relative_u/t{str(t).zfill(3)}.npy")
data_v = np.load(f"./data/3d/relative_v/t{str(t).zfill(3)}.npy")
```

**移行後:**
```python
# データ読み込み
data_u = np.load(f"{config.get_data_path('3d', 'relative_u')}/t{str(t).zfill(3)}.npy")
data_v = np.load(f"{config.get_data_path('3d', 'relative_v')}/t{str(t).zfill(3)}.npy")
```

### パターン3: 図の出力パス（プロットスクリプト）

**移行前:**
```python
# 出力フォルダの作成
os.makedirs("./fig/3d/vortex_region/relative_wind_radial/", exist_ok=True)

# 鉛直レベルリスト
z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(
        f"./fig/3d/vortex_region/relative_wind_radial/z{str(z).zfill(2)}",
        exist_ok=True
    )

# 保存
fig.savefig(
    f"./fig/3d/vortex_region/relative_wind_radial/z{str(z).zfill(2)}/t{str(t).zfill(3)}.png"
)
```

**移行後:**
```python
# 出力フォルダの作成
output_folder = config.get_fig_path("3d", "vortex_region", "relative_wind_radial")
os.makedirs(output_folder, exist_ok=True)

# 鉛直レベルリスト
z_list = [0, 9, 17, 23, 29, 36, 42, 48, 54, 60]
for z in z_list:
    os.makedirs(
        os.path.join(output_folder, f"z{str(z).zfill(2)}"),
        exist_ok=True
    )

# 保存
fig.savefig(
    os.path.join(output_folder, f"z{str(z).zfill(2)}", f"t{str(t).zfill(3)}.png")
)
```

### パターン4: azim_mean などの場合

**移行前:**
```python
output_folder = "./data/azim/relative_wind_radial/"
os.makedirs(output_folder, exist_ok=True)

np.save(f"{output_folder}t{str(t).zfill(3)}.npy", azim_mean)
```

**移行後:**
```python
output_folder = config.get_data_path("azim", "relative_wind_radial")
os.makedirs(output_folder, exist_ok=True)

np.save(f"{output_folder}/t{str(t).zfill(3)}.npy", azim_mean)
```

## 使用例

### 例1: 異なるデータディレクトリを使用

```json
{
    "data_dir": "/mnt/scratch/tc_data",
    "fig_dir": "/mnt/scratch/tc_figures"
}
```

### 例2: プロジェクト内の別の場所を使用

```json
{
    "data_dir": "../output/data",
    "fig_dir": "../output/figures"
}
```

### 例3: 実験ごとに異なるディレクトリを使用

```json
{
    "data_dir": "./experiments/exp001/data",
    "fig_dir": "./experiments/exp001/figures"
}
```

## ヘルパーメソッドの詳細

### `config.get_data_path(*paths)`

データディレクトリ配下のパスを生成します。

**引数:**
- `*paths`: パスの構成要素（可変長引数）

**戻り値:**
- `str`: 完全なパス

**例:**
```python
# 基本的な使用法
path = config.get_data_path("3d", "relative_wind_radial")
# 結果: "./data/3d/relative_wind_radial"

# ファイル名を含む場合
path = config.get_data_path("azim", "wind_u", "t000.npy")
# 結果: "./data/azim/wind_u/t000.npy"

# 単一のパス要素
path = config.get_data_path("center")
# 結果: "./data/center"
```

### `config.get_fig_path(*paths)`

図ディレクトリ配下のパスを生成します。

**引数:**
- `*paths`: パスの構成要素（可変長引数）

**戻り値:**
- `str`: 完全なパス

**例:**
```python
# 基本的な使用法
path = config.get_fig_path("3d", "vortex_region", "wind")
# 結果: "./fig/3d/vortex_region/wind"

# ファイル名を含む場合
path = config.get_fig_path("2d", "slp", "t024.png")
# 結果: "./fig/2d/slp/t024.png"
```

## TC中心座標ファイルのパスについて

TC中心座標ファイルのパスも自動的に`data_dir`に基づいて解決されるようになりました：

**以前:**
```python
center_x = np.loadtxt("./data/ss_slp_center_x.txt", ndmin=1)
center_y = np.loadtxt("./data/ss_slp_center_y.txt", ndmin=1)
```

**現在:**
```python
# AnalysisConfigクラス内で自動的に処理される
center_x = config.center_x  # {data_dir}/ss_slp_center_x.txt から読み込まれる
center_y = config.center_y  # {data_dir}/ss_slp_center_y.txt から読み込まれる
```

## トラブルシューティング

### パスの区切り文字について

`os.path.join()` を使用することで、OSに依存しない正しいパス区切り文字が使用されます：

```python
# 推奨（クロスプラットフォーム対応）
path = os.path.join(output_folder, "subfolder", "file.npy")

# 非推奨（Windowsで問題が発生する可能性）
path = f"{output_folder}/subfolder/file.npy"
```

### 相対パスと絶対パス

`setting.json` では相対パスと絶対パスの両方が使用できます：

```json
{
    "data_dir": "./data",              # 相対パス
    "fig_dir": "/absolute/path/to/fig" # 絶対パス
}
```

### 既存のスクリプトとの互換性

デフォルト値として `"./data"` と `"./fig"` が設定されているため、`setting.json` に追加しなくても既存のコードは動作します。

## 移行チェックリスト

既存のスクリプトを移行する際は、以下をチェックしてください：

- [ ] `"./data/"` で始まるパスを `config.get_data_path()` に置き換え
- [ ] `"./fig/"` で始まるパスを `config.get_fig_path()` に置き換え
- [ ] `f"{path}/"` の形式から `os.path.join()` に変更
- [ ] ハードコードされた `"./data/"` や `"./fig/"` の文字列を削除
- [ ] 構文チェックを実行: `python -m py_compile <script.py>`
- [ ] 実際にスクリプトを実行して動作確認

## 推奨される移行手順

1. **バックアップを作成**
   ```bash
   cp your_script.py your_script.py.bak
   ```

2. **スクリプトを編集**
   - このガイドのパターンに従ってパスを修正

3. **構文チェック**
   ```bash
   python -m py_compile your_script.py
   ```

4. **動作確認**
   - 小規模なテストデータで実行
   - 出力先のディレクトリが正しく作成されるか確認
   - データが正しく読み書きされるか確認

5. **完全な実行**
   - 全時刻で実行して最終確認

## サンプルコード

完全なサンプルスクリプトは以下を参照してください：
- `3d/relative_wind_radial_tangential_calc.py` - データ出力のサンプル
- `3d/relative_wind_radial_plot.py` - 図出力のサンプル

## 今後の展開

### 予定されている機能

- [ ] 入力データディレクトリの設定（`input_data_dir`）
- [ ] ログファイルディレクトリの設定（`log_dir`）
- [ ] 一時ファイルディレクトリの設定（`tmp_dir`）

### 全スクリプトの移行

現在、以下のスクリプトが移行済みです：
- ✅ `3d/relative_wind_radial_tangential_calc.py`
- ✅ `3d/relative_wind_radial_plot.py`

残りの約160ファイルも段階的に移行していく予定です。

## まとめ

この機能により、以下が実現されました：

1. ✅ **柔軟なディレクトリ構造**: プロジェクトの要件に応じてパスを変更可能
2. ✅ **設定の一元管理**: `setting.json` で全パスを管理
3. ✅ **コードの保守性向上**: ハードコードされたパスを削減
4. ✅ **互換性の維持**: デフォルト値により既存コードも動作
5. ✅ **使いやすさ**: シンプルなヘルパーメソッド

---

**更新履歴**
- 2025-11-25: 初版作成
