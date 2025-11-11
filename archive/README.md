# Archive Directory

このディレクトリには、リファクタリング作業中に使用された一時的なスクリプトとバックアップファイルが保存されています。

## 📁 ディレクトリ構造

```
archive/
├── migration_scripts/   # リファクタリング時に使用した移行スクリプト
└── backups/            # 古いバックアップファイル
```

## 🔧 migration_scripts/

リファクタリング作業で使用した一時的なスクリプト群。
移行作業は完了しているため、これらは参考用にのみ保存されています。

### 含まれるファイル

- `fix_all_remaining.py` - 残りの全ファイルを一括移行
- `fix_double_config.py` - 二重config定義の修正
- `fix_remaining_files.py` - 不完全な設定ブロックの修正
- `refactor_azim_batch.py` - azim_meanディレクトリのバッチリファクタリング
- `refactor_azim_mean.py` - azim_meanファイルの個別リファクタリング
- `auto_migrate.py` - 自動移行スクリプト
- `fix_azim_mean_issues.py` - azim_mean特有の問題修正
- `fix_data_paths.py` - データパスの修正
- `migrate_azim_mean.py` - azim_meanディレクトリの移行
- `migrate_helper.py` - 移行ヘルパースクリプト

## 💾 backups/

リファクタリング前のバックアップファイル。

### 含まれるファイル

- `whole_domain.py.old` - 2d/whole_domain.pyの旧バージョン
- `*.backup` - 160個の.backupファイル（リファクタリング前の各ファイルのバックアップ）

### 統計

- **総ファイル数**: 161個
- **.backup ファイル**: 160個
- **.old ファイル**: 1個

## ⚠️ 注意事項

- これらのファイルは**参考用**です
- 本番コードでは使用しないでください
- 必要に応じて削除可能です

## 🗑️ クリーンアップ

これらのファイルが不要になった場合は、以下のコマンドで削除できます：

```bash
rm -rf archive/
```

---

**作成日**: 2025-11-11
**目的**: リファクタリング作業の記録保持
