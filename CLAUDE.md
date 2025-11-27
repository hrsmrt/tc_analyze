# TC解析プロジェクトのコンテキスト

このプロジェクトは修士課程の研究で使用している熱帯低気圧の解析コード群です。

---

## 📚 主要ドキュメント

### 必須ドキュメント（優先度順）

1. **プロジェクト概要**
   @./README.md

2. **コマンドリファレンス（よく使うコマンド）**
   @./docs/COMMAND_REFERENCE.md

3. **アーキテクチャ設計書**
   @./docs/ARCHITECTURE.md

4. **作業履歴とコーディング規約**
   @./docs/WORK_LOG.md

### 補足ドキュメント（archive/docs/）

5. **リファクタリング概要**
   @./archive/docs/REFACTORING_SUMMARY.md

6. **マイグレーション完了報告**
   @./archive/docs/MIGRATION_COMPLETE.md

7. **ディレクトリ再構成提案書**
   @./archive/docs/DIRECTORY_RESTRUCTURE_PROPOSAL.md

---

## ⚡ クイックリファレンス

### 環境セットアップ
```bash
cd /path/to/tc_analyze
pip install -e .
```

### よく使うコマンド
```bash
# 全解析実行
sh $WORK/tc_analyze/run/analyze.sh all

# 特定カテゴリのみ
sh $WORK/tc_analyze/run/analyze.sh center 3d azim

# カテゴリ一覧表示
sh $WORK/tc_analyze/run/analyze.sh --list
```

### ディレクトリ構成
```
tc_analyze/
├── analysis/       # 解析スクリプト（パターンB構造）
│   ├── spatial/   # 空間解析（2d, 3d）
│   ├── azimuthal/ # 方位角平均解析
│   ├── vertical/  # 鉛直解析
│   ├── center/    # TC中心位置計算
│   └── diagnostics/ # 診断解析
├── utils/          # 共通モジュール（config, grid, plotting）
├── run/            # 実行スクリプト（analyze.sh, setting.json）
├── tools/          # 開発・保守ツール
├── docs/           # ドキュメント
└── archive/        # アーカイブ
```

---

## 📋 追加の注意事項

- **コードスタイル**: pylint, autoflake, isort, autopep8 で整形済み
- **設定ファイル**: `run/setting.json` を使用
- **実行スクリプト**: `run/analyze.sh` でカテゴリ別に実行可能
- **Python環境**: `pip install -e .` で開発モードでインストールが必要
- **依存関係**: numpy, matplotlib, joblib（setup.pyで自動インストール）
- **ディレクトリ構造**: パターンB（解析タイプ別 + calc/plot分離）を採用

---

## 🎯 タスク別参照先

| やりたいこと | 参照先 |
|------------|--------|
| **コマンド実行方法を知りたい** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) |
| **システム構成を理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) |
| **新しい解析を追加したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) の拡張ガイド |
| **コーディング規約を確認したい** | [docs/WORK_LOG.md](./docs/WORK_LOG.md) の確立されたコーディングパターン |
| **エラーが発生した** | [docs/COMMAND_REFERENCE.md](./docs/COMMAND_REFERENCE.md) のトラブルシューティング |
| **データフローを理解したい** | [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) のデータフロー |

---

**最終更新**: 2025-11-27
