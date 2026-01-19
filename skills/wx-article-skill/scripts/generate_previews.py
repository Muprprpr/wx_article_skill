#!/usr/bin/env python3
"""为所有主题生成预览 HTML"""

import json
import sys
from pathlib import Path

# 预览 Markdown 内容 - 完整覆盖所有 markdown 语法
PREVIEW_MD = '''# 一级标题 H1

这是一段普通文本，展示基本的段落样式。这里包含了**加粗文字**和*斜体文字*，还有~~删除线文字~~和==高亮文字==。同时也包含`行内代码`示例。

## 二级标题 H2

这是二级标题下的段落内容。

### 三级标题 H3

这是三级标题下的段落内容。

#### 四级标题 H4

这是四级标题下的段落内容。

## 文本样式完整演示

本节展示所有支持的行内样式：

- **加粗文本**：使用双星号包围
- *斜体文本*：使用单星号包围
- ~~删除线文本~~：使用双波浪线包围
- ==高亮文本==：使用双等号包围
- `行内代码`：使用反引号包围
- **组合样式**：可以同时使用**加粗和*斜体*混合**

## 代码块演示

### Python 代码

```python
def hello_world():
    """打印 Hello World"""
    print("Hello, World!")
    return True

class Calculator:
    def add(self, a, b):
        return a + b
```

### JavaScript 代码

```javascript
// JavaScript 示例
const greeting = "Hello";
console.log(greeting);

function add(a, b) {
    return a + b;
}
```

### Bash 代码

```bash
#!/bin/bash
echo "Hello, World!"
ls -la
git status
```

### 无语言标记代码块

```
这是没有语言标记的代码块
使用纯文本样式渲染
```

## 引用块完整演示

### 提示引用块

> [!TIP]
> 这是一个提示引用块，用于提供有用的建议和小技巧。

> [!T]
> 简写形式的提示引用块。

### 警告引用块

> [!WARNING]
> 这是一个警告引用块，用于提醒用户注意潜在问题。

> [!CAUTION]
> 这是一个谨慎引用块，表示需要小心操作。

### 笔记引用块

> [!NOTE]
> 这是一个笔记引用块，用于记录额外的信息和备注。

> [!N]
> 简写形式的笔记引用块。

### 信息引用块

> [!INFO]
> 这是一个信息引用块，用于提供补充说明。

> [!I]
> 简写形式的信息引用块。

### 默认引用块

> 这是普通的引用块样式，没有特定类型标记。
> 可以有多行内容。
>
> 甚至可以包含**加粗**和`代码`等行内样式。

## 列表完整演示

### 无序列表

- 第一项
- 第二项
  - 嵌套无序列表项 A
  - 嵌套无序列表项 B
    - 深层嵌套项
  - 返回上层
- 第三项
- 第四项，包含`行内代码`

### 有序列表

1. 第一步操作
2. 第二步操作
3. 第三步操作
   1. 子步骤 A
   2. 子步骤 B
4. 第四步操作

### 任务列表

- [ ] 未完成的任务 A
- [x] 已完成的任务 B
- [ ] 另一个未完成任务
- [x] 带有**加粗**的已完成任务
- [ ] 带有`代码`的未完成任务

## 数学公式演示

### 行内公式

质能方程是 $E = mc^2$，这是爱因斯坦提出的著名公式。

勾股定理可以表示为 $a^2 + b^2 = c^2$。

### 块级公式

$$f(x) = \\frac{1}{\\sqrt{2\\pi}}\\int_{-\\infty}^{\\infty} e^{-t^2/2} dt$$

$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$

$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

## 其他元素演示

### 水平分隔线

---

上面是一条水平分隔线。

### 链接示例

访问 [GitHub](https://github.com) 了解更多信息。

这是一个 [带标题的链接](https://example.com "鼠标悬停显示标题")。

### 图片示例

![示例图片占位符](https://via.placeholder.com/800x400/f6f8fa/24292e?text=Image+Placeholder)

### 折叠块

<details>
<summary>点击展开：这是什么？</summary>
这是折叠块的隐藏内容，点击标题后才会显示。可以包含多行内容，甚至其他 markdown 元素。

比如这里有个**加粗文字**和`代码`。
</details>

<details>
<summary>点击展开：代码示例</summary>
```python
def hidden_function():
    return "这是隐藏在折叠块中的代码"
```
</details>

## 混合样式测试

这是一个综合测试段落，包含**加粗**、*斜体*、~~删除线~~、==高亮==和`行内代码`等各种样式的**组合**使用效果。

> [!TIP]
> 引用块中也可以使用各种**样式**，比如*斜体*、==高亮==和`代码`。
'''

def generate_preview(theme_name: str, themes_dir: Path, output_dir: Path):
    """为单个主题生成预览"""
    theme_path = themes_dir / f"{theme_name}.json"
    if not theme_path.exists():
        return False

    with open(theme_path, "r", encoding="utf-8") as f:
        theme = json.load(f)

    # 导入转换模块
    sys.path.insert(0, str(Path(__file__).parent))
    from converter import convert_markdown_to_html

    html, _ = convert_markdown_to_html(
        PREVIEW_MD,
        theme_name,
        use_real_images=False,
        input_dir=None,
        output_dir=None
    )

    output_path = output_dir / f"{theme_name}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return True

def main():
    """主程序"""
    base_dir = Path(__file__).parent
    themes_dir = base_dir / "themes"
    preview_dir = base_dir / "previews"
    preview_dir.mkdir(exist_ok=True)

    # 获取所有主题
    theme_files = [f for f in themes_dir.glob("*.json") if f.name != "_schema.json"]
    theme_names = sorted([f.stem for f in theme_files])

    print(f"Generating previews for {len(theme_names)} themes...")

    success_count = 0
    for theme_name in theme_names:
        try:
            if generate_preview(theme_name, themes_dir, preview_dir):
                print(f"[OK] {theme_name}")
                success_count += 1
            else:
                print(f"[SKIP] {theme_name}")
        except Exception as e:
            print(f"[ERROR] {theme_name}: {e}")

    print(f"\n{'='*50}")
    print(f"Generated {success_count}/{len(theme_names)} previews")
    print(f"Output directory: {preview_dir}")
    print(f"\nOpen previews/{theme_names[0]}.html to start viewing!")

if __name__ == "__main__":
    main()
