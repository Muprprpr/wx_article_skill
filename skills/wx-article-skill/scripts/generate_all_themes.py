#!/usr/bin/env python3
"""
生成所有主题的测试 HTML
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from converter import convert_markdown_to_html


def convert_obsidian_images(markdown: str) -> str:
    """将 Obsidian 图片格式 ![[filename]] 转换为标准 Markdown 格式"""
    import re
    # 匹配 ![[filename]] 格式
    def replace_obsidian(match):
        filename = match.group(1).strip()
        # 移除可能的图片尺寸参数，如 ![[image.png|300]] 或 ![[image.png|300x200]]
        if '|' in filename:
            filename = filename.split('|')[0].strip()
        return f'![{filename}]({filename})'

    return re.sub(r'!\[\[([^\]]+)\]\]', replace_obsidian, markdown)


def main():
    # 输入文件路径
    input_file = Path(r"C:\Users\ASUS\Documents\obsidian文档管理\默认知识库\02_Resourses\文章_Skills保姆级入门指南.md")
    output_dir = Path(r"C:\Users\ASUS\mywork\wx_article_skill\test_output\all_themes")

    # 读取 Markdown 内容
    with open(input_file, "r", encoding="utf-8") as f:
        markdown = f.read()

    # 转换 Obsidian 图片格式
    markdown = convert_obsidian_images(markdown)

    # 获取所有主题
    from converter import ThemeManager
    manager = ThemeManager()
    themes = manager.list_themes()

    print(f"Found {len(themes)} themes")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    # 为每个主题生成 HTML
    success_count = 0
    for theme_name in sorted(themes):
        try:
            html, _ = convert_markdown_to_html(
                markdown=markdown,
                theme_name=theme_name,
                use_real_images=True,  # 使用真实图片（如果找不到会显示占位符）
                input_dir=input_file.parent,
                output_dir=output_dir,
                assets_dirs=None
            )

            # 写入文件
            output_file = output_dir / f"{theme_name}.html"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"[OK] {theme_name}")
            success_count += 1
        except Exception as e:
            print(f"[FAIL] {theme_name}: {e}")

    print("-" * 50)
    print(f"Generated {success_count}/{len(themes)} themes successfully")
    print(f"Output files in: {output_dir}")


if __name__ == "__main__":
    main()
