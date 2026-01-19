# 微信公众号文章编译器

> 一项 Claude Code Skill，将 Markdown 转换为微信公众号兼容的 HTML，支持 26+ 主题和图片自动提取

[![Claude Skills](https://img.shields.io/badge/Claude_Skills-2-blue)](https://github.com/anthropics/claude-code)
[![Themes](https://img.shields.io/badge/Themes-26-green)](./themes)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

现在你只需要聚焦于文字内容，将 Markdown 文件提交给 AI，即可自动生成经过清洗、排版后的公众号内容。

---

## 特性

- **AI 智能清洗** - 自动标准化 Markdown 格式，修复层级结构
- **26+ 主题模板** - 覆盖金融、科技、生活、校园、情感、亚文化、Web3、政工等多个领域
- **图片自动提取** - 支持绝对路径、相对路径，自动检测 Obsidian 库
- **微信兼容** - 生成的 HTML 可直接粘贴到公众号后台，样式完整保留
- **批量生成** - 一键为所有主题生成预览，快速选择最合适的风格

---

## 安装

### 方式一：通过 Claude Marketplace（推荐）

在 Claude Code 中执行：

```bash
/plugin marketplace add Muprprpr/wx_article_skill
/plugin install skill@wx_article_skill
```

### 方式二：克隆项目

```bash
git clone https://github.com/Muprprpr/wx_article_skill.git
cd wx_article_skill
claude
```

---

## 使用方法

安装后，在 Claude Code 中直接对话：

```
帮我把 article.md 转换成公众号 HTML
```

```
用 finance-professional 主题转换这篇文章
```

```
为所有主题生成这篇文章的预览
```

### 也可以直接运行脚本

```bash
# 基本用法
python converter.py input.md -o output.html

# 指定主题
python converter.py input.md -o output.html -t finance-professional

# 列出所有主题
python converter.py --list-themes

# 批量生成所有主题
python generate_all_themes.py
```

---

## 支持的主题

### 金融类

| 主题 | 说明 | 配色 |
|------|------|------|
| `finance-professional` | 专业金融风格 | 深蓝金 |
| `finance-elegant` | 优雅金融风格 | 金黑 |
| `finance-data` | 数据金融风格 | 红绿 |

### 科技类

| 主题 | 说明 | 配色 |
|------|------|------|
| `tech-cyberpunk` | 赛博朋克风格 | 霓虹紫 |
| `tech-minimal` | 极简科技风格 | 黑白灰 |
| `tech-gradient` | 渐变科技风格 | 紫橙 |

### 生活类

| 主题 | 说明 | 配色 |
|------|------|------|
| `life-warm` | 温暖生活风格 | 米色暖橙 |
| `life-fresh` | 清新生活风格 | 薄荷绿 |
| `life-cozy` | 温馨生活风格 | 奶茶色 |

### 校园类

| 主题 | 说明 | 配色 |
|------|------|------|
| `campus-youth` | 青春校园风格 | 蓝橙 |
| `campus-academic` | 学术校园风格 | 墨绿 |
| `campus-cute` | 可爱校园风格 | 粉嫩 |

### 情感类

| 主题 | 说明 | 配色 |
|------|------|------|
| `emotion-rose` | 玫瑰情感风格 | 深粉 |
| `emotion-serene` | 宁静情感风格 | 淡紫 |
| `emotion-sunrise` | 晨曦情感风格 | 金橙 |

### 亚文化类

| 主题 | 说明 | 配色 |
|------|------|------|
| `subculture-acg` | 二次元ACG风格 | 樱花粉 |
| `subculture-punk` | 朋克亚文化风格 | 黑白红 |
| `subculture-vaporwave` | 蒸汽波风格 | 紫粉渐变 |

### Web3类

| 主题 | 说明 | 配色 |
|------|------|------|
| `web3-blockchain` | 区块链风格 | 深蓝金 |
| `web3-metaverse` | 元宇宙风格 | 霓虹紫蓝 |
| `web3-defi` | DeFi专业风格 | 绿色收益 |

### 政工类

| 主题 | 说明 | 配色 |
|------|------|------|
| `political-red` | 红色政工风格 | 经典红金 |
| `political-solemn` | 庄重政工风格 | 深红灰 |
| `political-modern` | 现代政工风格 | 红白简洁 |

### 基础主题

| 主题 | 说明 |
|------|------|
| `vibelight` | 浅色终端风格 |
| `vibedark` | 深色终端风格 |

---

## 项目结构

```
wx_article_skill/
├── skill.md                   # Claude Code Skill 定义
├── converter.py               # 核心转换脚本
├── generate_all_themes.py     # 批量生成脚本
├── themes/                    # 26 个主题配置
│   ├── _schema.json           # 主题规范
│   ├── campus-*.json          # 校园风格 (3)
│   ├── emotion-*.json         # 情感风格 (3)
│   ├── finance-*.json         # 金融风格 (3)
│   ├── life-*.json            # 生活风格 (3)
│   ├── political-*.json       # 政工风格 (3)
│   ├── subculture-*.json      # 亚文化风格 (3)
│   ├── tech-*.json            # 科技风格 (3)
│   ├── web3-*.json            # Web3 风格 (3)
│   ├── vibelight.json         # 浅色基础主题
│   └── vibedark.json          # 深色基础主题
└── previews/                  # 主题预览示例
```

---

## 工作原理

```
┌─────────────────┐
│  你的 Markdown   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI 智能清洗     │  ← 标准化格式、修复层级
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  主题应用        │  ← 选择 26+ 主题之一
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  图片提取        │  ← 自动检测 Obsidian 库
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HTML 输出       │  ← 直接粘贴到公众号
└─────────────────┘
```

---

## 图片查找逻辑

脚本按以下顺序自动查找图片：

| 顺序 | 说明 |
|------|------|
| 1 | 绝对路径 |
| 2 | 相对于 Markdown 文件 |
| 3 | 自动检测 Obsidian 库根目录 |
| 4 | 常见附件目录（assets/、attachments/、images/） |
| 5 | 递归搜索文件名 |

### Obsidian 用户

项目已完全兼容 Obsidian 的图片语法：

```markdown
![[image.png]]           <!-- Wiki 链接 -->
![alt](path/image.png)   <!-- 标准 Markdown -->
```

系统会自动检测 Obsidian 库根目录，无需额外配置。

---

## 主题扩展

在 `themes/` 目录创建 JSON 文件即可添加新主题，参考 `themes/_schema.json` 查看完整规范。

**快速创建主题**：

```bash
# 复制一个现有主题作为模板
cp themes/vibelight.json themes/my-theme.json

# 编辑配置文件
# 修改 colors、fonts 等样式

# 使用新主题
python converter.py input.md -o output.html -t my-theme
```

---

## License

[MIT](LICENSE)
