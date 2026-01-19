#!/usr/bin/env python3
"""批量更新主题文件"""

import json
from pathlib import Path

def update_theme_file(file_path: Path):
    """更新单个主题文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        theme = json.load(f)

    # 删除 author 字段
    if 'meta' in theme and 'author' in theme['meta']:
        del theme['meta']['author']

    # 更新版本号
    if 'meta' in theme:
        theme['meta']['version'] = '2.0.0'

    # 确保所有组件存在
    components = theme.setdefault('components', {})

    # 更新 text 样式
    text = components.setdefault('text', {})
    if 'italic' not in text:
        text['italic'] = "font-style: italic;"
    if 'strikethrough' not in text:
        text['strikethrough'] = "text-decoration: line-through; opacity: 0.7;"
    if 'highlight' not in text:
        text['highlight'] = "background-color: #fff8c5; padding: 1px 4px; border-radius: 2px;"
    if 'mark' not in text:
        text['mark'] = "background-color: #fff8c5; padding: 1px 4px; border-radius: 2px;"

    # 更新 blocks 样式
    blocks = components.setdefault('blocks', {})
    if 'quote_note' not in blocks:
        blocks['quote_note'] = "background-color: #e8f4fd; border-left: 4px solid #0969da; color: #0c3d6a; padding: 12px; margin-bottom: 15px; border-radius: 0 6px 6px 0;"
    if 'quote_info' not in blocks:
        blocks['quote_info'] = "background-color: #def7ff; border-left: 4px solid #58a6ff; color: #0c447a; padding: 12px; margin-bottom: 15px; border-radius: 0 6px 6px 0;"
    if 'quote_default' not in blocks:
        blocks['quote_default'] = "background-color: #f6f8fa; border-left: 4px solid #57606a; color: #57606a; padding: 12px; margin-bottom: 15px; border-radius: 0 6px 6px 0;"
    if 'details' not in blocks:
        blocks['details'] = "background-color: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 12px; margin-bottom: 15px;"
    if 'summary' not in blocks:
        blocks['summary'] = "font-weight: bold; cursor: pointer; color: #0969da; margin-bottom: 8px;"

    # 添加 lists 样式
    if 'lists' not in components:
        components['lists'] = {
            "ul": "margin-bottom: 15px; padding-left: 20px;",
            "ol": "margin-bottom: 15px; padding-left: 20px;",
            "li": "margin-bottom: 6px;",
            "task_checked": "color: #22a627; text-decoration: line-through;",
            "task_unchecked": "color: #24292e;"
        }

    # 确保 media 有 image 样式
    media = components.setdefault('media', {})
    if 'image' not in media:
        media['image'] = "max-width: 100%; height: auto; display: block; margin: 15px 0; border-radius: 4px;"
    if 'video' not in media:
        media['video'] = "width: 100%; border-radius: 6px; margin: 15px 0;"

    # 添加 math 样式
    if 'math' not in components:
        components['math'] = {
            "inline": "background-color: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-family: 'Times New Roman', serif; font-style: italic;",
            "block": "background-color: #f6f8fa; padding: 15px; border-radius: 6px; text-align: center; margin: 15px 0; overflow-x: auto; font-family: 'Times New Roman', serif;"
        }

    # 添加 h1 和 h4 样式
    headings = components.setdefault('headings', {})
    if 'h1' not in headings:
        headings['h1'] = headings.get('h2', headings['h2'] if 'h2' in headings else "font-size: 20px; font-weight: bold; margin-bottom: 20px;")
    if 'h4' not in headings:
        headings['h4'] = "font-size: 15px; font-weight: bold; margin-bottom: 8px; color: #57606a; margin-top: 20px;"

    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(theme, f, ensure_ascii=False, indent=2)

    return True

def main():
    themes_dir = Path(__file__).parent / "themes"
    theme_files = [f for f in themes_dir.glob("*.json") if f.name != "_schema.json"]

    for theme_file in theme_files:
        try:
            update_theme_file(theme_file)
        except Exception as e:
            pass

    print("All themes updated!")

if __name__ == "__main__":
    main()
