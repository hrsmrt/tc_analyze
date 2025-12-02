# TC Analysis Viewer

インタラクティブな3Dデータビューア for TC解析図

## 機能

- 📊 **ドメイン選択**: whole domain / TC-centric
- 📁 **カテゴリ選択**: energy, energy_density, vortex_region等
- 🔢 **Z層選択**: スライダーで垂直レベルを選択
- ⏱️ **時間ステップ選択**: スライダーとPrev/Nextボタン
- 🖼️ **画像表示**: ワンクリックで図を切り替え

## 必要なパッケージ

```bash
pip install streamlit pillow
```

## 使い方

### 1. 任意のディレクトリから起動

ビューアは、`run_viewer.sh`を使えば**どのディレクトリからでも**起動できます。
スクリプトが自動的にプロジェクトルート（`tc_analyze/`）に移動してから起動します。

**方法1: プロジェクトルートから**
```bash
cd /path/to/tc_analyze
bash viewer/run_viewer.sh
# または
streamlit run viewer/tc_viewer.py
```

**方法2: 任意のサブディレクトリから**
```bash
cd /path/to/tc_analyze/analysis/energy
bash ../../viewer/run_viewer.sh
```

**方法3: 絶対パスで任意のディレクトリから起動**
```bash
cd /any/directory
bash /path/to/tc_analyze/viewer/run_viewer.sh
# run_viewer.shが自動的にtc_analyze/に移動してから起動
```

### 2. ブラウザで開く

起動すると自動的にブラウザが開きます（通常 http://localhost:8501）

### 3. 操作方法

**サイドバー（左側）:**
- **Domain**: `domain` または `tc-centric` を選択
- **Category**: 解析カテゴリを選択（energy, vortex_region等）
- **Z Level Index**: スライダーで垂直レベルを選択
- **Time Step**: スライダーで時間ステップを選択
- **Prev / Next**: ボタンで前後の時間ステップに移動

**メインエリア（中央）:**
- 選択した図が表示されます
- 画像をクリックして拡大表示可能

## 図ディレクトリの設定

ビューアは**setting.jsonの`fig_dir`**を読み取ります。

### 設定の読み込み順序

1. **script/setting.json** から `fig_dir` を読み取る（推奨）
2. 見つからない場合: **setting.json**（プロジェクトルート直下）
3. 見つからない場合: デフォルト値 `fig/` を使用

### setting.json の例

```json
{
  "fig_dir": "./fig",
  "glevel": 11,
  ...
}
```

`fig_dir`は絶対パスまたは相対パス（プロジェクトルートからの）で指定できます。

## ディレクトリ構造

ビューアは以下の2つのディレクトリ構造に対応しています（`fig_dir`で指定された場所）：

**構造1: カテゴリ直下にz層フォルダ**
```
{fig_dir}/
└── domain/
    └── vortex_region/
        ├── z00/
        │   ├── t000.png
        │   ├── t001.png
        │   └── ...
        ├── z09/
        └── ...
```

**構造2: サブカテゴリを経由してz層フォルダ**
```
{fig_dir}/
├── domain/
│   └── energy/
│       ├── total_energy/
│       │   ├── z00/
│       │   │   ├── t000.png
│       │   │   ├── t001.png
│       │   │   └── ...
│       │   ├── z09/
│       │   └── ...
│       ├── kinetic_energy/
│       │   ├── z00/
│       │   └── ...
│       └── ...
└── tc_centric/
    └── energy_density/
        └── ...
```

どちらの構造でも自動的に検出して表示します。

## キーボードショートカット

Streamlitのデフォルトショートカット:
- `R`: アプリをリロード
- `C`: キャッシュをクリア

## トラブルシューティング

### "No plots found in fig" エラー

解析スクリプトを実行して図を生成してください：

```bash
cd /path/to/tc_analyze
bash run/analyze.sh energy
```

### ポートが既に使用中

別のポートで起動：

```bash
streamlit run viewer/tc_viewer.py --server.port 8502
```

### 画像が表示されない

1. 図が生成されているか確認: `ls fig/domain/energy/internal_energy/z00/`
2. ファイル名が正しいか確認: `t000.png`, `t001.png`等

## 今後の拡張予定

- [ ] アニメーション機能（時間方向の自動再生）
- [ ] 複数図の並列表示（比較用）
- [ ] データ値の表示（マウスオーバー）
- [ ] 図のダウンロード機能
- [ ] カスタムカラーマップ選択

## 依存パッケージ

- streamlit >= 1.28.0
- Pillow >= 10.0.0
- Python >= 3.8
