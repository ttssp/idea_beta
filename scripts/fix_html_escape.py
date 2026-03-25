#!/usr/bin/env python3
"""
批量修复 Python 文件中的 HTML 转义污染
修复:
  - &gt; -> >
  - &lt; -> <
  - &amp; -> &
  - &quot; -> "
  - &apos; -> '
"""

import os
import re
import sys
import py_compile
from pathlib import Path


def fix_file(file_path: Path) -> tuple[bool, list[str]]:
    """修复单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 替换 HTML 转义字符
        replacements = [
            ('&gt;', '>'),
            ('&lt;', '<'),
            ('&amp;', '&'),
            ('&quot;', '"'),
            ('&apos;', "'"),
        ]

        changes = []
        for old, new in replacements:
            if old in content:
                count = content.count(old)
                content = content.replace(old, new)
                changes.append(f"{old} -> {new} ({count} 处)")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes

        return False, []

    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False, []


def check_syntax(file_path: Path) -> bool:
    """检查 Python 语法"""
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ 语法错误 {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查失败 {file_path}: {e}")
        return False


def main():
    root_dir = Path(__file__).parent.parent

    # 目标目录
    target_dirs = [
        root_dir / 'src' / 'policy_control',
        root_dir / 'backend' / 'e3',
    ]

    print("=" * 70)
    print("HTML 转义污染修复工具")
    print("=" * 70)

    all_files = []
    for target_dir in target_dirs:
        if target_dir.exists():
            py_files = list(target_dir.rglob('*.py'))
            all_files.extend(py_files)
            print(f"\n📁 扫描目录: {target_dir}")
            print(f"   发现 {len(py_files)} 个 Python 文件")

    if not all_files:
        print("\n⚠️  没有找到 Python 文件")
        return

    print(f"\n📋 总计 {len(all_files)} 个文件待处理\n")

    fixed_count = 0
    syntax_errors = []

    for file_path in sorted(all_files):
        rel_path = file_path.relative_to(root_dir)
        was_fixed, changes = fix_file(file_path)

        if was_fixed:
            fixed_count += 1
            print(f"✅ 修复 {rel_path}")
            for change in changes:
                print(f"   - {change}")

        # 检查语法
        if not check_syntax(file_path):
            syntax_errors.append(rel_path)

    print("\n" + "=" * 70)
    print(f"修复完成:")
    print(f"  - 处理文件: {len(all_files)}")
    print(f"  - 修复文件: {fixed_count}")
    print(f"  - 语法错误: {len(syntax_errors)}")

    if syntax_errors:
        print("\n❌ 以下文件存在语法错误:")
        for err in syntax_errors:
            print(f"   - {err}")
        sys.exit(1)
    else:
        print("\n✅ 所有文件语法检查通过!")
        sys.exit(0)


if __name__ == '__main__':
    main()
