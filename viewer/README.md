# TC Analysis Viewer

インタラクティブな3Dデータビューア for TC解析図

## 機能

- 📊 **ドメイン選択**: whole domain / TC-centric / center
- 📁 **カテゴリ選択**: energy, energy_density, vortex_region等（任意の階層に対応）
- 🔢 **Z層選択**: スライダー + Down/Upボタンで垂直レベルを選択
- ⏱️ **時間ステップ選択**: スライダー + Prev/Nextボタンで時間を移動
- 🎬 **アニメーション再生**: Play/Stopボタンで時系列の自動再生（速度調整可能）
- 🖼️ **画像表示**: 高速な図の切り替えと拡大表示

## 必要なパッケージ

```bash
pip install streamlit pillow
```

## 使い方

### 1. 任意のディレクトリから起動

ビューアは、`run_viewer.sh`を使えば**どのディレクトリからでも**起動できます。

**方法1: 図ディレクトリの中から起動（最も簡単・推奨）**
```bash
cd /path/to/fig     # fig, fig2, output, results など任意の名前
bash /path/to/tc_analyze/viewer/run_viewer.sh
# domain, tc_centric, center フォルダが検出されれば自動的に使用
```

**方法2: プロジェクトルートから**
```bash
cd /path/to/tc_analyze
bash viewer/run_viewer.sh
# または
streamlit run viewer/tc_viewer.py
```

**方法3: 任意のサブディレクトリから**
```bash
cd /path/to/tc_analyze/analysis/energy
bash ../../viewer/run_viewer.sh
```

**方法4: 絶対パスで任意のディレクトリから起動**
```bash
cd /any/directory
bash /path/to/tc_analyze/viewer/run_viewer.sh
# プロジェクトルートを検出し、setting.jsonからfig_dirを読み取る
```

**自動検出の仕組み:**
- カレントディレクトリに `domain/`, `tc_centric/`, `center/` フォルダがあれば、カレントディレクトリを図ディレクトリとして使用
- フォルダ名は問わない（`fig`, `fig2`, `output`, `results` など何でもOK）
- 検出されない場合は、プロジェクトルートを探して `setting.json` から読み取る

### 2. ブラウザで開く

起動すると自動的にブラウザが開きます（通常 http://localhost:8501）

### 3. 操作方法

**サイドバー（左側）:**

**📊 Plot Selection**
- **Domain**: `domain`, `tc-centric`, `center` から選択
- **Category**: 解析カテゴリを選択（任意の階層構造に対応）

**🔢 Z Level Control**
- **⬇️ Down / Up ⬆️ ボタン**: 1クリックで前後のZ levelに移動
- **スライダー**: 任意のZ levelに直接移動

**⏱️ Time Control**
- **⬅️ Prev / Next ➡️ ボタン**: 1クリックで前後の時間ステップに移動
- **スライダー**: 任意の時間ステップに直接移動

**🎬 Animation**
- **▶️ Play ボタン**: 時系列アニメーションを開始
- **⏸️ Stop ボタン**: アニメーションを停止
- **Speed 選択**:
  - `Max speed` (0s/frame): 最速
  - `0.05s` ~ `1.0s/frame`: 速度を調整可能
- アニメーションは自動的に最後のフレームで停止します

**ℹ️ Info**
- 現在の選択状態（Domain, Category, Z Level, Time Step）を表示
- アニメーション再生状態を表示

**メインエリア（中央）:**
- 選択した図が大きく表示されます
- 画像をクリックして拡大表示可能
- アニメーション中は自動的にフレームが切り替わります

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

ビューアは**任意の階層数のディレクトリ構造**に対応しています（`fig_dir`で指定された場所）。
z層フォルダ（`z00`, `z01`, ...）を再帰的に探索します。

**例1: カテゴリ直下にz層フォルダ**
```
{fig_dir}/
└── domain/
    └── vortex_region/
        ├── z00/
        │   ├── t000.png
        │   └── ...
        └── z09/
```

**例2: サブカテゴリを経由**
```
{fig_dir}/
└── domain/
    └── energy/
        └── total_energy/
            ├── z00/
            │   ├── t000.png
            │   └── ...
            └── z09/
```

**例3: さらに深い階層（centerなど）**
```
{fig_dir}/
└── center/
    └── ms_pres/
        └── smoothed/
            └── some_metric/
                ├── z00/
                │   ├── t000.png
                │   └── ...
                └── z09/
```

ビューアは自動的にz層フォルダを探索し、そこまでのパスを
カテゴリ名として表示します（例: "ms_pres/smoothed/some_metric"）。

## キーボードショートカット

**Streamlitのデフォルトショートカット:**
- `R`: アプリをリロード
- `C`: キャッシュをクリア

**注意:** 矢印キーでの直接操作は、Streamlitの技術的制約により現在サポートされていません。代わりに、サイドバーのボタン（⬅️ Prev/Next ➡️、⬇️ Down/Up ⬆️）をご利用ください。

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

## 実装済み機能

- [x] アニメーション機能（時間方向の自動再生）✨
- [x] Z Level / Time Step のボタンナビゲーション
- [x] 任意階層のディレクトリ構造に対応
- [x] アニメーション速度調整

## 今後の拡張予定

- [ ] 複数図の並列表示（比較用）
- [ ] データ値の表示（マウスオーバー）
- [ ] 図のダウンロード機能
- [ ] カスタムカラーマップ選択
- [ ] キーボード矢印キー対応（Streamlitの制約により困難）

## 依存パッケージ

- streamlit >= 1.28.0
- Pillow >= 10.0.0
- Python >= 3.8
