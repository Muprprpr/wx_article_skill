#!/usr/bin/env python3
"""
微信文章 HTML 转换器
将标准化 Markdown 转换为微信公众号兼容的 HTML
支持图片提取和重命名
"""

import json
import os
import re
import shutil
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional


# ============================================
# 图片提取器 (Updated)
# ============================================

class ImageExtractor:
    """图片提取器，负责复制和重命名图片，支持 Obsidian 库"""

    def __init__(self, input_dir: Path, output_dir: Path, assets_dirs: List[Path] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.assets_dirs = [Path(d) for d in (assets_dirs or [])]
        self.mapping: Dict[str, str] = {}
        self.counter = 1
        
        # 尝试检测 Obsidian 库根目录
        self.obsidian_root = self._detect_obsidian_root()
        self.search_paths = self._build_search_paths()

    def _detect_obsidian_root(self) -> Optional[Path]:
        """向上查找是否存在 .obsidian 文件夹以确定库根目录"""
        current = self.input_dir
        # 防止死循环，向上查找最多 10 层或到达根目录
        for _ in range(10):
            obsidian_config = current / ".obsidian"
            if obsidian_config.exists() and obsidian_config.is_dir():
                print(f"[INFO] Detected Obsidian Vault Root: {current}")
                return current
            parent = current.parent
            if parent == current:  # 到达系统根目录
                break
            current = parent
        return None

    def _build_search_paths(self) -> List[Path]:
        """构建图片搜索路径列表"""
        paths = []
        # 1. 当前输入目录
        if self.input_dir:
            paths.append(self.input_dir)
        
        # 2. 指定的资源目录
        paths.extend(self.assets_dirs)
        
        # 3. 如果是 Obsidian 库，加入根目录
        if self.obsidian_root:
            paths.append(self.obsidian_root)
            # Obsidian 常见的附件文件夹命名
            common_obsidian_folders = ['attachments', 'Attachments', 'assets', 'Assets', 'media', 'images']
            for folder in common_obsidian_folders:
                attach_path = self.obsidian_root / folder
                if attach_path.exists():
                    paths.append(attach_path)

        # 4. 普通 Markdown 项目常见子目录
        if self.input_dir:
            common_names = ['assets', 'attachments', 'images', 'img', '附件']
            for name in common_names:
                paths.append(self.input_dir / name)
                paths.append(self.input_dir.parent / name)
        
        # 去重并验证存在性
        unique_paths = []
        seen = set()
        for p in paths:
            p = Path(p)
            if p not in seen and p.exists():
                unique_paths.append(p)
                seen.add(p)
        return unique_paths

    def extract_images(self, markdown: str) -> str:
        """从 Markdown 中提取图片并更新路径"""
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # 处理 Obsidian Wiki 链接 ![[filename]] 或 ![[filename|alt]]
        def replace_wiki_image(match):
            content = match.group(1)
            if '|' in content:
                filename, alt_text = content.split('|', 1)
            else:
                filename, alt_text = content, content
            
            # 清理文件名两侧空白
            filename = filename.strip()
            new_filename = self._copy_image(filename)
            return f'![{alt_text}](images/{new_filename})'

        # 先替换 Wiki 链接
        markdown = re.sub(r'!\[\[(.*?)\]\]', replace_wiki_image, markdown)

        # 处理标准 Markdown 链接 ![alt](path)
        def replace_std_image(match):
            alt_text = match.group(1)
            original_path = match.group(2)
            # 解码 URL (例如 "image%20name.png" -> "image name.png")
            original_path = urllib.parse.unquote(original_path)
            new_filename = self._copy_image(original_path)
            return f'![{alt_text}](images/{new_filename})'

        updated_markdown = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', replace_std_image, markdown)
        return updated_markdown

    def _copy_image(self, original_path: str) -> str:
        """复制图片到输出目录并重命名"""
        source_file = self._find_image_file(original_path)
        if source_file:
            ext = source_file.suffix.lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
                ext = '.png'
        else:
            ext = self._get_extension(original_path)
        
        new_filename = f"img_{self.counter:03d}{ext}"
        self.counter += 1
        
        if not source_file:
            print(f"[!] Image not found: {original_path} -> {new_filename} (Search paths: {len(self.search_paths)})", file=sys.stderr)
            return new_filename
            
        dest_file = self.images_dir / new_filename
        try:
            shutil.copy2(source_file, dest_file)
            print(f"[OK] {source_file.name} -> {new_filename}")
            self.mapping[str(source_file)] = new_filename
        except Exception as e:
            print(f"[X] Copy failed: {source_file} - {e}", file=sys.stderr)
        return new_filename

    def _find_image_file(self, original_path: str) -> Optional[Path]:
        """查找图片文件"""
        # 1. 尝试直接路径（绝对路径）
        direct_path = Path(original_path)
        if direct_path.exists() and direct_path.is_file():
            return direct_path
            
        # 2. 尝试相对于输入文件的路径
        if self.input_dir:
            relative_path = self.input_dir / original_path
            if relative_path.exists() and relative_path.is_file():
                return relative_path

        # 3. 在所有搜索路径（包括 Obsidian 根目录）中查找
        filename = Path(original_path).name
        if filename:
            for search_dir in self.search_paths:
                # 3.1 直接拼接查找
                file_path = search_dir / original_path
                if file_path.exists() and file_path.is_file():
                    return file_path
                
                # 3.2 仅根据文件名拼接查找（应对路径不匹配的情况）
                file_path_name = search_dir / filename
                if file_path_name.exists() and file_path_name.is_file():
                    return file_path_name

                # 3.3 递归搜索 (rglob) - 解决深层目录下的文件
                # 注意：rglob 可能会比较慢，如果有大量文件
                try:
                    matches = list(search_dir.rglob(filename))
                    for match in matches:
                        if match.is_file():
                            return match
                except Exception:
                    continue
        return None

    def _get_extension(self, path: str) -> str:
        """从路径中提取扩展名"""
        ext = Path(path).suffix.lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
            return ext
        return '.png'

    def get_summary(self) -> str:
        """获取提取摘要"""
        msg = f"Extracted {len(self.mapping)} image(s) to {self.images_dir}/"
        if self.obsidian_root:
            msg += f" [Obsidian Root: {self.obsidian_root.name}]"
        return msg


# ============================================
# 主题加载系统
# ============================================

class ThemeManager:
    """主题管理器，支持加载和切换主题"""

    def __init__(self, themes_dir: str = None):
        if themes_dir is None:
            themes_dir = Path(__file__).parent / "themes"
        self.themes_dir = Path(themes_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def list_themes(self) -> list[str]:
        """列出所有可用主题"""
        if not self.themes_dir.exists():
            return []
        return [f.stem for f in self.themes_dir.glob("*.json") if f.name != "_schema"]

    def load_theme(self, name: str) -> Dict[str, Any]:
        """加载指定主题配置"""
        if name in self._cache:
            return self._cache[name]
        theme_path = self.themes_dir / f"{name}.json"
        if not theme_path.exists():
            raise FileNotFoundError(f"Theme '{name}' not found: {theme_path}")
        with open(theme_path, "r", encoding="utf-8") as f:
            theme = json.load(f)
        self._cache[name] = theme
        return theme


# ============================================
# Markdown 解析器
# ============================================

class MarkdownParser:
    """轻量级 Markdown 解析器，针对微信文章优化"""

    def __init__(self, theme: Dict[str, Any], use_real_images: bool = True):
        self.theme = theme
        self.use_real_images = use_real_images

    def parse(self, markdown: str) -> str:
        """将 Markdown 解析为 HTML"""
        lines = markdown.split("\n")
        html_lines = []
        in_code_block = False
        code_lang = ""
        code_content = []
        in_details = False
        details_content = []
        in_ul = False
        in_ol = False
        list_items = []

        for line in lines:
            # 处理折叠块
            if line.strip().startswith("<details>"):
                style = self.theme["components"]["blocks"].get("details", "")
                html_lines.append(f'<details style="{style}">')
                continue
            elif line.strip().startswith("<summary>"):
                style = self.theme["components"]["blocks"].get("summary", "")
                content = line.replace("<summary>", "").replace("</summary>", "").strip()
                html_lines.append(f'<summary style="{style}">{self._inline_parse(content)}</summary>')
                continue
            elif line.strip().startswith("</details>"):
                html_lines.append('</details>')
                continue

            # 代码块处理
            if line.startswith("```"):
                # 先处理未完成的列表
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False

                if not in_code_block:
                    in_code_block = True
                    code_lang = line[3:].strip() or "text"
                else:
                    html_lines.append(self._render_code_block(code_lang, "\n".join(code_content)))
                    code_content = []
                    in_code_block = False
                continue

            if in_code_block:
                code_content.append(line)
                continue

            # 标题处理 - 先结束未完成的列表
            if line.startswith("#### ") or line.startswith("### ") or line.startswith("## "):
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False

            if line.startswith("#### "):
                html_lines.append(self._render_h4(line[5:]))
            elif line.startswith("### "):
                html_lines.append(self._render_h3(line[4:]))
            elif line.startswith("## "):
                html_lines.append(self._render_h2(line[3:]))
            # 水平线
            elif line.strip() == "---":
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False
                html_lines.append(self._render_hr())
            # 引用块
            elif line.startswith("> "):
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False
                html_lines.append(self._render_quote(line[2:]))
            # 任务列表
            elif re.match(r'^[\s]*[-*+]\s*\[[x\s]\]', line):
                list_type = "ul"  # 任务列表属于无序列表
                if list_type == "ul" and not in_ul:
                    if in_ol:
                        html_lines.append(self._render_ol_close())
                        in_ol = False
                    html_lines.append(self._render_ul_open())
                    in_ul = True
                elif list_type == "ol" and not in_ol:
                    if in_ul:
                        html_lines.append(self._render_ul_close())
                        in_ul = False
                    html_lines.append(self._render_ol_open())
                    in_ol = True
                html_lines.append(self._render_task_item(line))
            # 图片
            elif line.startswith("![") and "](" in line:
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False
                html_lines.append(self._render_image(line))
            # 空行 - 保持列表状态
            elif line.strip() == "":
                continue
            # 无序列表项
            elif re.match(r'^[\s]*[-*+]\s', line):
                if not in_ul:
                    if in_ol:
                        html_lines.append(self._render_ol_close())
                        in_ol = False
                    html_lines.append(self._render_ul_open())
                    in_ul = True
                html_lines.append(self._render_list_item(line, False))
            # 有序列表项
            elif re.match(r'^[\s]*\d+\.\s', line):
                if not in_ol:
                    if in_ul:
                        html_lines.append(self._render_ul_close())
                        in_ul = False
                    html_lines.append(self._render_ol_open())
                    in_ol = True
                html_lines.append(self._render_list_item(line, True))
            # 普通段落
            else:
                if in_ul:
                    html_lines.append(self._render_ul_close())
                    in_ul = False
                elif in_ol:
                    html_lines.append(self._render_ol_close())
                    in_ol = False
                html_lines.append(self._render_paragraph(line))

        # 结束未关闭的列表
        if in_ul:
            html_lines.append(self._render_ul_close())
        elif in_ol:
            html_lines.append(self._render_ol_close())

        return "\n".join(html_lines)

    def _render_ul_open(self) -> str:
        style = self.theme["components"]["lists"].get("ul", "")
        if style:
            return f'<ul style="{style}">'
        return "<ul>"

    def _render_ul_close(self) -> str:
        return "</ul>"

    def _render_ol_open(self) -> str:
        style = self.theme["components"]["lists"].get("ol", "")
        if style:
            return f'<ol style="{style}">'
        return "<ol>"

    def _render_ol_close(self) -> str:
        return "</ol>"

    def _render_h1(self, text: str) -> str:
        style = self.theme["components"]["headings"].get("h1", self.theme["components"]["headings"]["h2"])
        return f'<h1 style="{style}">{self._inline_parse(text)}</h1>'

    def _render_h2(self, text: str) -> str:
        style = self.theme["components"]["headings"]["h2"]
        return f'<h2 style="{style}">{self._inline_parse(text)}</h2>'

    def _render_h3(self, text: str) -> str:
        style = self.theme["components"]["headings"]["h3"]
        return f'<h3 style="{style}">{self._inline_parse(text)}</h3>'

    def _render_h4(self, text: str) -> str:
        style = self.theme["components"]["headings"].get("h4", "")
        if style:
            return f'<h4 style="{style}">{self._inline_parse(text)}</h4>'
        return f'<h4>{self._inline_parse(text)}</h4>'

    def _render_paragraph(self, text: str) -> str:
        style = self.theme["components"]["text"]["paragraph"]
        return f'<p style="{style}">{self._inline_parse(text)}</p>'

    def _render_code_block(self, lang: str, code: str) -> str:
        style = self.theme["components"]["blocks"]["code_block"]
        escaped = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre style="{style}"><code>{escaped}</code></pre>'

    def _render_quote(self, text: str) -> str:
        # 检测引用类型
        if text.startswith("[!WARNING]") or text.startswith("[!CAUTION]"):
            text = text.split("]", 1)[1].strip() if "]" in text else text
            style = self.theme["components"]["blocks"].get("quote_warning",
                     self.theme["components"]["blocks"]["quote_tip"])
        elif text.startswith("[!TIP]") or text.startswith("[!T]"):
            text = text.split("]", 1)[1].strip() if "]" in text else text
            style = self.theme["components"]["blocks"]["quote_tip"]
        elif text.startswith("[!NOTE]") or text.startswith("[!N]"):
            text = text.split("]", 1)[1].strip() if "]" in text else text
            style = self.theme["components"]["blocks"].get("quote_note",
                     self.theme["components"]["blocks"]["quote_tip"])
        elif text.startswith("[!INFO]") or text.startswith("[!I]"):
            text = text.split("]", 1)[1].strip() if "]" in text else text
            style = self.theme["components"]["blocks"].get("quote_info",
                     self.theme["components"]["blocks"]["quote_tip"])
        else:
            style = self.theme["components"]["blocks"].get("quote_default",
                     self.theme["components"]["blocks"]["quote_tip"])
        return f'<blockquote style="{style}">{self._inline_parse(text)}</blockquote>'

    def _render_task_item(self, line: str) -> str:
        """渲染任务列表项"""
        match = re.match(r'^[\s]*[-*+]\s*\[([x\s])\]\s*(.*)', line, re.IGNORECASE)
        if match:
            checked = match.group(1).lower() == 'x'
            content = match.group(2)
            li_style = self.theme["components"]["lists"]["li"]
            if checked:
                item_style = self.theme["components"]["lists"]["task_checked"]
                symbol = "&#10003;"
            else:
                item_style = self.theme["components"]["lists"]["task_unchecked"]
                symbol = "&#9724;"
            return f'<li style="{li_style}"><span style="{item_style}">{symbol}</span> {self._inline_parse(content)}</li>'
        return self._render_list_item(line, False)

    def _render_list_item(self, line: str, ordered: bool) -> str:
        """渲染普通列表项"""
        match = re.match(r'^[\s]*([-*+]|\d+\.)\s+(.*)', line)
        if match:
            content = match.group(2)
            li_style = self.theme["components"]["lists"]["li"]
            return f'<li style="{li_style}">{self._inline_parse(content)}</li>'
        return f'<li>{line}</li>'

    def _render_image(self, line: str) -> str:
        match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
        if match:
            alt, url = match.groups()
            if self.use_real_images:
                img_style = self.theme["components"]["media"].get("image",
                    "max-width: 100%; height: auto; display: block; margin: 15px 0;")
                return f'<img src="{url}" alt="{alt}" style="{img_style}" />'
            else:
                style = self.theme["components"]["media"]["image_placeholder"]
                return f'<section style="{style}">[Image: {alt}]</section>'
        return ""

    def _render_hr(self) -> str:
        style = self.theme["components"]["blocks"]["hr"]
        return f'<hr style="{style}">'

    def _inline_parse(self, text: str) -> str:
        """行内元素解析"""
        # 数学公式（优先处理）
        text = re.sub(r'\$\$([^$]+)\$\$', self._replace_math_block, text)
        text = re.sub(r'\$([^$]+)\$', self._replace_math_inline, text)
        # 行内图片 ![alt](url) - 需要在其他替换之前处理
        text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', self._replace_inline_image, text)
        # 删除线
        text = re.sub(r'~~([^~]+)~~', self._replace_strikethrough, text)
        # 高亮 ==text== 或 ==text==
        text = re.sub(r'==([^=]+)==', self._replace_highlight, text)
        # 加粗 **text**
        text = re.sub(r'\*\*([^*]+)\*\*', self._replace_bold, text)
        # 斜体 *text*
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', self._replace_italic, text)
        # 行内代码 `code`
        text = re.sub(r'`([^`]+)`', self._replace_inline_code, text)
        # 链接 [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', self._replace_link, text)
        return text

    def _replace_math_block(self, match):
        style = self.theme["components"]["math"]["block"]
        return f'<div style="{style}">{match.group(1)}</div>'

    def _replace_math_inline(self, match):
        style = self.theme["components"]["math"]["inline"]
        return f'<span style="{style}">{match.group(1)}</span>'

    def _replace_strikethrough(self, match):
        style = self.theme["components"]["text"].get("strikethrough", "text-decoration: line-through;")
        return f'<span style="{style}">{match.group(1)}</span>'

    def _replace_highlight(self, match):
        style = self.theme["components"]["text"].get("highlight",
                 self.theme["components"]["text"].get("mark", "background-color: yellow;"))
        return f'<span style="{style}">{match.group(1)}</span>'

    def _replace_bold(self, match):
        style = self.theme["components"]["text"]["strong"]
        return f'<strong style="{style}">{match.group(1)}</strong>'

    def _replace_italic(self, match):
        style = self.theme["components"]["text"].get("italic", "font-style: italic;")
        return f'<span style="{style}">{match.group(1)}</span>'

    def _replace_inline_code(self, match):
        style = self.theme["components"]["text"]["code_inline"]
        return f'<code style="{style}">{match.group(1)}</code>'

    def _replace_link(self, match):
        style = self.theme["base"]["link"]
        return f'<a href="{match.group(2)}" style="{style}">{match.group(1)}</a>'

    def _replace_inline_image(self, match):
        """替换行内图片"""
        alt, url = match.groups()
        if self.use_real_images:
            img_style = self.theme["components"]["media"].get("image",
                "max-width: 100%; height: auto; display: block; margin: 15px 0;")
            return f'<img src="{url}" alt="{alt}" style="{img_style}" />'
        else:
            style = self.theme["components"]["media"]["image_placeholder"]
            return f'<section style="{style}">[Image: {alt}]</section>'


# ============================================
# HTML 生成器
# ============================================

class HTMLGenerator:
    """HTML 生成器，组装最终输出"""

    def __init__(self, theme: Dict[str, Any]):
        self.theme = theme

    def generate(self, content_html: str) -> str:
        """生成完整的 HTML"""
        container_style = self.theme["base"]["container"]
        header = self._render_header()
        footer = self._render_footer()

        return f'''<section id="nice" style="{container_style}">
{header}

{content_html}

{footer}
</section>'''

    def _render_header(self) -> str:
        """渲染模拟窗口栏头部"""
        hw = self.theme["components"]["header_window"]
        dots_html = "\n".join(
            f'<span style="{d}"></span>' for d in hw.get("dots", [])
        )
        return f'''<div style="{hw["style"]}">
{dots_html}
<span style="{hw["title_style"]}">markdown.md</span>
</div>'''

    def _render_footer(self) -> str:
        """渲染页脚"""
        f = self.theme["components"]["footer"]
        return f'''<div style="{f["style"]}">
<p style="{f["text"]}">_壹五_ @ AI Vibe Coding</p>
</div>'''


# ============================================
# 主程序
# ============================================

def convert_markdown_to_html(
    markdown: str,
    theme_name: str = "vibelight",
    use_real_images: bool = True,
    input_dir: Path = None,
    output_dir: Path = None,
    assets_dirs: List[Path] = None
) -> Tuple[str, ImageExtractor]:
    """转换 Markdown 到 HTML"""
    manager = ThemeManager()
    theme = manager.load_theme(theme_name)

    extractor = None
    if input_dir and output_dir and use_real_images:
        extractor = ImageExtractor(input_dir, output_dir, assets_dirs)
        markdown = extractor.extract_images(markdown)

    parser = MarkdownParser(theme, use_real_images=use_real_images)
    content_html = parser.parse(markdown)

    generator = HTMLGenerator(theme)
    return generator.generate(content_html), extractor


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="WeChat Article HTML Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md -o output.html
  %(prog)s input.md -o output.html -t finance-professional
  %(prog)s input.md -o output.html --assets "C:\\Attachments"
  %(prog)s input.md -o output.html --no-images
  %(prog)s --list-themes
        """
    )
    parser.add_argument("input", help="Input Markdown file path")
    parser.add_argument("-o", "--output", required=True, help="Output HTML file path")
    parser.add_argument("-t", "--theme", default="vibelight", help="Theme name (default: vibelight)")
    parser.add_argument("-a", "--assets", action="append", dest="assets_dirs",
                        help="Assets/attachments directories")
    parser.add_argument("--list-themes", action="store_true", help="List all available themes")
    parser.add_argument("--no-images", action="store_true", help="Use placeholders instead of real images")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed information")

    args = parser.parse_args()

    manager = ThemeManager()

    if args.list_themes:
        themes = manager.list_themes()
        if themes:
            print("Available themes:")
            for t in sorted(themes):
                print(f"  - {t}")
        else:
            print("No theme files found")
        return

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    use_images = not args.no_images
    assets_dirs = [Path(d) for d in args.assets_dirs] if args.assets_dirs else []

    if args.verbose and assets_dirs:
        print(f"[INFO] Assets directories: {assets_dirs}")

    html, extractor = convert_markdown_to_html(
        markdown,
        args.theme,
        use_real_images=use_images,
        input_dir=input_path.parent,
        output_dir=output_path.parent,
        assets_dirs=assets_dirs
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Generated: {output_path}")

    if extractor:
        print(extractor.get_summary())


if __name__ == "__main__":
    main()