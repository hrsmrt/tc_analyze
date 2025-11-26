#!/usr/bin/env python
"""
使い方コメントとファイル名の一致をチェックするスクリプト
"""

import os
import re
from pathlib import Path


def check_file(filepath):
    """ファイルの使い方コメントとファイル名の一致をチェック"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:15]  # 最初の15行をチェック

        # "# python" で始まる行を探す
        for line in lines:
            if line.strip().startswith('# python'):
                # tc_analyze/xxx/yyy.py のパターンを探す（バックスラッシュエスケープも考慮）
                match = re.search(r'tc_analyze/(.+?\.py)', line)
                if match:
                    comment_path = match.group(1).replace(r'\ ', ' ')  # バックスラッシュエスケープを戻す
                    # 実際のファイルパス（tc_analyzeを除く）
                    actual_path = str(filepath).replace('\\', '/').replace('./', '')

                    if comment_path != actual_path:
                        return {
                            'file': actual_path,
                            'comment': comment_path,
                            'line': line.strip()
                        }
    except Exception as e:
        pass

    return None


def main():
    mismatches = []

    # 全てのPythonファイルをチェック
    for filepath in Path('.').rglob('*.py'):
        # utils, examples ディレクトリは除外
        if 'utils/' in str(filepath) or 'examples/' in str(filepath):
            continue

        result = check_file(filepath)
        if result:
            mismatches.append(result)

    if mismatches:
        print(f"❌ 見つかった不一致: {len(mismatches)}件\n")
        for m in mismatches:
            print(f"ファイル: {m['file']}")
            print(f"コメント: {m['comment']}")
            print(f"行内容: {m['line']}")
            print()
    else:
        print("✅ 全てのファイルが一致しています")

    return mismatches


if __name__ == '__main__':
    main()
