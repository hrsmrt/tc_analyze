# TC解析プロジェクトのコンテキスト

このプロジェクトは修士課程の研究で使用している熱帯低気圧の解析コード群です。

## プロジェクト概要
@./README.md

## 作業履歴とコーディング規約
@./WORK_LOG.md

## リファクタリング概要
@./REFACTORING_SUMMARY.md

## マイグレーション完了報告
@./MIGRATION_COMPLETE.md

---

## 追加の注意事項

- コードスタイル: pylint, autoflake, isort, autopep8 で整形済み
- 設定ファイル: `script/setting.json` を使用
- 実行スクリプト: `script/analyze.sh` でカテゴリ別に実行可能
- Python環境: `pip install -e .` で開発モードでインストールが必要
