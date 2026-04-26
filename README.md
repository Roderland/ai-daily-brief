# AI 创业每日简报

每日自动采集国内 AI 创业相关资讯，生成结构化简报，一键深挖感兴趣的话题。

## 功能

- **每日简报**：自动采集 36氪、虎嗅、少数派、知乎等平台 AI 相关资讯
- **AI 精选**：用 AI 筛选与 AI 创业/商业化最相关的内容，生成摘要和商业价值分析
- **标签分类**：工具类 / 商业模式 / 行业动态 / 观点
- **深挖分析**：对感兴趣的话题触发 AI Agent 进行深度商业模式分析
- **免费部署**：基于 GitHub Pages + GitHub Actions，零成本运行

## 部署指南

### 1. Fork 或创建仓库

在 GitHub 上创建仓库 `ai-daily-brief`，将本目录代码推送上去。

### 2. 配置 GitHub Pages

1. 进入仓库 **Settings → Pages**
2. **Source** 选择 **Deploy from a branch**
3. **Branch** 选择 `gh-pages`，目录选 `/(root)`
4. 点击 **Save**

### 3. 配置 API Key

进入仓库 **Settings → Secrets and variables → Actions**：

**添加 Secret：**
- `AI_API_KEY`：你的 API Key（Anthropic 或 OpenAI）

**添加 Variables（可选）：**
- `AI_PROVIDER`：`anthropic`（默认）或 `openai`
- `AI_MODEL`：模型名称，默认 `claude-sonnet-4-20250514`（Anthropic）或 `gpt-4o`（OpenAI）

### 4. 启用 Actions

进入 **Actions** 页面，确认两个 workflow 已启用：
- **每日简报**：每天 UTC 0:00（北京时间 8:00）自动运行，也可手动触发
- **深挖分析**：手动触发，需要输入话题

### 5. 首次运行

手动触发 **每日简报** workflow，等待运行完成（约 1-2 分钟）。
访问 `https://roderland.github.io/ai-daily-brief` 查看效果。

## 使用指南

### 每日浏览

每天打开页面，30 分钟内即可浏览完当日简报：
- 顶部选择日期、按分类筛选、搜索关键词
- 每条简报包含：标题、一句话摘要、商业价值分析、标签、重要度评分
- 点击标题可查看原文

### 深挖感兴趣的话题

1. 点击某条简报的 **🔍 深挖** 按钮
2. 弹窗中点击按钮跳转到 GitHub Actions 页面
3. 点击 **Run workflow** 触发分析
4. 几分钟后刷新页面，即可看到深度分析报告

## 技术架构

```
采集层 (Python)    →    AI 处理层 (Python + LLM API)    →    展示层 (静态页面)
                                                                  
collector/               processor/                            web/
  rss_collector.py         ai_summarizer.py                    index.html
  sources.py               deep_dive.py                        css/style.css
                                                               js/app.js
```

自动化由 GitHub Actions 驱动：`.github/workflows/daily-brief.yml` 和 `deep-dive.yml`

## 自定义信息源

编辑 `collector/sources.py` 中的 `RSS_SOURCES` 和 `ZHIHU_TOPICS` 即可增删信息源。

## 后续迭代方向

- [ ] 海外信息源（Product Hunt、Hacker News、TechCrunch）
- [ ] 即时推送（微信/飞书/Telegram）
- [ ] 轻量后端，网页直接触发深挖
- [ ] 历史话题归档和搜索
- [ ] 周报/月报汇总
