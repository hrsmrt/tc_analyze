# TC解析プロジェクトのコンテキスト

このプロジェクトは修士課程の研究で使用している熱帯低気圧の解析コード群です。

---

## 📚 主要ドキュメント

### 必須ドキュメント（優先度順）

1. **プロジェクト概要**
   @./README.md

2. **コマンドリファレンス（よく使うコマンド）**
   @./COMMAND_REFERENCE.md

3. **アーキテクチャ設計書**
   @./ARCHITECTURE.md

4. **作業履歴とコーディング規約**
   @./WORK_LOG.md

### 補足ドキュメント

5. **リファクタリング概要**
   @./REFACTORING_SUMMARY.md

6. **マイグレーション完了報告**
   @./MIGRATION_COMPLETE.md

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
sh $WORK/tc_analyze/script/analyze.sh all

# 特定カテゴリのみ
sh $WORK/tc_analyze/script/analyze.sh center 3d azim

# カテゴリ一覧表示
sh $WORK/tc_analyze/script/analyze.sh --list
```

### ディレクトリ構成
```
tc_analyze/
├── utils/          # 共通モジュール（config, grid, plotting）
├── script/         # analyze.sh, setting.json
├── 3d/             # 3次元解析
├── azim_mean/      # 方位角平均解析
└── ...
```

---

## 📋 追加の注意事項

- **コードスタイル**: pylint, autoflake, isort, autopep8 で整形済み
- **設定ファイル**: `script/setting.json` を使用
- **実行スクリプト**: `script/analyze.sh` でカテゴリ別に実行可能
- **Python環境**: `pip install -e .` で開発モードでインストールが必要
- **依存関係**: numpy, matplotlib, joblib（setup.pyで自動インストール）

---

## 🎯 タスク別参照先

| やりたいこと | 参照先 |
|------------|--------|
| **コマンド実行方法を知りたい** | [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) |
| **システム構成を理解したい** | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| **新しい解析を追加したい** | [ARCHITECTURE.md](./ARCHITECTURE.md) の拡張ガイド |
| **コーディング規約を確認したい** | [WORK_LOG.md](./WORK_LOG.md) の確立されたコーディングパターン |
| **エラーが発生した** | [COMMAND_REFERENCE.md](./COMMAND_REFERENCE.md) のトラブルシューティング |
| **データフローを理解したい** | [ARCHITECTURE.md](./ARCHITECTURE.md) のデータフロー |

---

**最終更新**: 2025-11-27
