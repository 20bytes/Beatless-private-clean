
20Bytes Log
Posts
Paper Reading
About
Archives
Search
切换到English
中文
Dark Theme
TABLE OF CONTENTS
1. 问题拆解
2. 技术选型
3. 核心思路：用对 API 端点
4. 整体架构
5. 聚合层的关键设计
5.1 机器人过滤
5.2 大厂项目识别
5.3 个人亮点提取
6. 邮件结构
7. GitHub Actions 配置
8. 本地测试
9. 几个踩过的坑
10. 可扩展的方向
11. 总结
GitHub 动态邮件摘要Blur image
Apr 12, 2026
/
Update Apr 12, 2026
9 min read
zh
github /
github actions /
python /
自动化 /
效率工具
用 GitHub Actions 把关注圈动态整理成每日邮件摘要
GitHub Dashboard 信息太杂？本文介绍如何用 Python + GitHub Actions 构建一个零成本的自动化工具，每天把你关注的人的动态整理成一封结构化的 HTML 邮件发给自己。
views | comments
每天打开 GitHub Dashboard，几百条动态刷出来：某个大厂仓库被几十个人同时 star、机器人在各种 PR 里留评论、github-actions[bot] 贡献了大半的活动量……真正有价值的信号——“某个你关注的人开始了一个新项目”、“某个朋友 fork 了一个不起眼但很有意思的库”——全被淹没在噪声里。

这篇文章记录我是怎么解决这个问题的：用 Python 写一个脚本，搭配 GitHub Actions 每天自动跑，把真正值得看的动态整理成一封 HTML 邮件发给自己，零服务器成本。

1. 问题拆解#
解决之前先想清楚”好的摘要”长什么样。我给自己列了三条标准：

聚焦个人行为：我更想知道”张三今天创建了一个新仓库”，而不是”anthropics/claude-code 今天被 40 个人 star 了”。
大厂项目只看数字：Google、Anthropic、OpenAI 这类大厂的项目每天都会有大量 star，列出所有 star 的人名没有意义，只需要知道”今天涨了多少”。
过滤掉机器人：github-actions[bot]、dependabot、renovate 这类账号的活动对我没有信息量，应该直接剔除。
2. 技术选型#
需求	方案
获取关注人的动态	GitHub REST API
定时运行	GitHub Actions（免费）
发送邮件	Python smtplib + Gmail App Password
AI 摘要（可选）	兼容 OpenAI 格式的 API
没有服务器、没有数据库、没有额外费用。整个系统的”基础设施”就是一个 GitHub 仓库和一个 YAML 文件。

3. 核心思路：用对 API 端点#
这是整个项目最关键的设计决策，也是最容易走弯路的地方。

GitHub 有一个看起来很合适的接口：

GET /users/{username}/received_events/public

它会返回你 Dashboard 上的聚合动态流。但实际用下来会发现一个严重问题：它会静默丢弃很多事件。Dashboard 上明明显示的动态，这个接口可能根本不返回。

正确做法是分两步走：

第一步：GET /users/{me}/following
         → 拿到你关注的所有人的 login 列表

第二步：对每个人循环调用
         GET /users/{user}/events/public
         → 拿到他们各自的公开动态

这样等于把 GitHub 内部的聚合逻辑自己实现了一遍，结果和 Dashboard 完全一致。

API 调用量估算：假设你关注了 100 人，每天有活动的可能有 30 人：

1 次 /following 请求
100 次 /events/public 请求
30 次 /users/{user} 请求（只对有活动的人拉 profile 用于显示真名）
共 ~131 次，而 GitHub 认证用户每小时限额 5000 次，完全够用
4. 整体架构#
项目分成五个模块，按流水线顺序执行：

main.py
  ↓
[1] fetcher.py   — 拉 following 列表 + 每人的动态
  ↓
[2] aggregator.py — 分组、去重、过滤机器人、识别大厂项目
  ↓
[3] summarizer.py — 调用 AI 接口生成 3-6 条摘要（可选）
  ↓
[4] renderer.py   — 生成 HTML 邮件
  ↓
[5] mailer.py     — 通过 SMTP 发送

每一步只负责自己的事，输出传给下一步，方便单独测试和修改。

5. 聚合层的关键设计#
aggregator.py 是整个系统信息质量的核心，几个重要决策：

5.1 机器人过滤#
GitHub 的官方机器人账号都带有 [bot] 后缀，直接按字符串匹配就能过滤：

def _is_bot(login: str) -> bool:
    if login.endswith("[bot]"):
        return True
    # 少数没有 [bot] 后缀的常见机器人账号
    return login.lower() in {"dependabot", "renovate", "codecov"}

5.2 大厂项目识别#
维护一个大厂组织名单，对这些 org 下的仓库在 trending 区只显示数量，不列人名：

BIG_ORGS = {
    "anthropics", "google", "google-gemini",
    "openai", "microsoft", "meta", "nvidia",
    "huggingface", "MiniMax-AI",
    # ... 可以按需扩充
}

def _is_big_org(repo_full_name: str) -> bool:
    org = repo_full_name.split("/")[0]
    return org.lower() in {o.lower() for o in BIG_ORGS}

5.3 个人亮点提取#
从所有事件里按优先级提取”值得单独展示”的个人行为：

优先级排序：
  新建仓库 (CreateEvent)  >  发布版本 (ReleaseEvent)
  > fork 了小众项目 (ForkEvent)  > star 了小众项目 (WatchEvent)

大厂仓库的 star 和 fork 不进入个人亮点，避免被大厂活动主导。

6. 邮件结构#
最终邮件分为四个区块，从上到下信息密度递减：

🤖 AI 速览         — 3-6 条 AI 提炼的要点（可选）
👤 个人亮点        — 新建仓库、发布版本、fork/star 小众项目
🔥 关注圈热门      — 小众热门（带 @who）/ 大厂项目（只看数量）
👥 按人分组        — 每人完整动态，过滤机器人后按事件数排序

同时展示 GitHub 登录名和真实显示名：

👤 个人亮点
🆕 Peter Steinberger (@steipete) 创建了新仓库 steipete/openclaw
⭐ Vincent Qin (@vincentqyw) star 了 isaaccorley/rsim

7. GitHub Actions 配置#
核心是这一段 cron 配置：

on:
  schedule:
    - cron: "0 23 * * *"   # UTC 23:00 = 北京时间 07:00
  workflow_dispatch: {}     # 支持手动触发

所有敏感信息通过 GitHub Secrets 注入，脚本里不硬编码任何账号信息：

env:
  GH_USERNAME: ${{ secrets.GH_USERNAME }}
  GH_TOKEN: ${{ secrets.GH_PAT }}
  SMTP_HOST: ${{ secrets.SMTP_HOST }}
  SMTP_PORT: ${{ secrets.SMTP_PORT }}
  SMTP_USER: ${{ secrets.SMTP_USER }}
  SMTP_PASS: ${{ secrets.SMTP_PASS }}
  MAIL_FROM: ${{ secrets.MAIL_FROM }}
  MAIL_TO: ${{ secrets.MAIL_TO }}

8. 本地测试#
用 SKIP_EMAIL=1 环境变量可以跳过发邮件，只在本地生成 HTML 文件查看效果：

# 复制 .env.example 并填好配置
cp .env.example .env

# 加载配置，跳过发邮件，只生成 HTML
export $(cat .env | grep -v '^#' | xargs)
SKIP_EMAIL=1 python main.py

# 用浏览器打开查看效果
xdg-open output/digest-*.html   # Linux
open output/digest-*.html        # macOS

9. 几个踩过的坑#
received_events 的坑：最开始用 /received_events/public，发现大量关注的人的活动根本不出现。排查了很久才意识到是 GitHub 那边的聚合策略问题，换成逐人拉取后完全解决。

SMTP 端口类型错误：在 GitHub Secrets 里填写端口号时，值被 Actions 读取后如果带了多余空格会导致 int() 转换失败。确保填入的是纯数字，没有引号和空格。

机器人噪声：最初的版本里 github-actions[bot] 贡献了超过 60 条”动态”，占据了大半版面。加了 bot 过滤后，邮件内容密度一下子提高了很多。

大厂项目列人名：早期版本在 trending 区把 anthropics/claude-code 的 35 个 starer 全部列出来，用处不大还占空间。按 org 分类后改成”35 人 star”，清晰多了。

10. 可扩展的方向#
DIGEST_HOURS 参数：改成 168 就变成每周摘要
事件类型过滤：不关心 IssueCommentEvent 的话，直接在 aggregator 里注释掉
大厂名单：BIG_ORGS 是一个普通的 Python set，按需增删
邮件样式：renderer.py 顶部的 CSS 常量可以直接改
11. 总结#
这个项目的核心并不复杂，一个 300 行的 Python 脚本加上一个 40 行的 GitHub Actions YAML，就能把一个每天手动刷 Dashboard 的习惯变成一封每天自动送到邮箱的摘要。

真正花时间的不是写代码，而是想清楚”什么信息对我有价值”——过滤掉机器人、区分大厂和小众项目、把个人行为置顶——这几个决策让最终的邮件质量差别很大。

如果你也被 GitHub Dashboard 的信息量压倒，可以参考这个思路自己搭一套。

用 GitHub Actions 把关注圈动态整理成每日邮件摘要
https://20bytes.github.io/blog/feed-digest
Author
昙柏
Published at
April 12, 2026
Copyright
CC BY-NC-SA 4.0

GitHub PR 流程指南：从 Fork 到 Merge 的标准七步法


10
%
© 2026 昙柏 & Site policy
Axi-Theme & astro-theme-pure powered
