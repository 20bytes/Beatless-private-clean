
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
1. 标准 PR 七步法
2. 开始前先理解：PR 到底是什么
3. 第一步：Fork 仓库
4. 第二步：Clone 到本地
5. 第三步：创建分支
6. 第四步：编码并提交 Commit
7. 第五步：Push 到自己的远程仓库
8. 第六步：Open PR
9. 第七步：Review 与二次修改
10. 新人最常见的三个坑
10.1 直接在 main 上改代码
10.2 PR 太大
10.3 只写标题，不写描述
11. 一套适合直接照抄的完整命令
12. 总结
13. 参考资料
GitHub Pull Request 协作流程Blur image
Apr 11, 2026
/
Update Apr 11, 2026
11 min read
zh
git /
github /
pull request /
workflow /
开源协作
GitHub PR 流程指南：从 Fork 到 Merge 的标准七步法
用一篇文章讲清 GitHub Pull Request 的标准流程：Fork、Clone、Branch、Commit、Push、Open PR、Review，以及协作中最常见的注意事项。
views | comments
PR 是协作的核心。即便你只是修复一个很小的 Bug，比如某个 Issue 里提到的边界情况问题，最终也往往要通过 Pull Request 把修改提交给维护者审查、讨论，再合并进主分支。

如果你是第一次给别人的仓库贡献代码，最容易卡住的并不是写代码本身，而是不清楚整套流程该怎么走。本文就按照一个最常见的开源协作场景，把 GitHub PR 的标准流程完整走一遍。

1. 标准 PR 七步法#
步骤	作用	命令 / 动作
1. Fork	把别人的仓库复制到自己的 GitHub 账号下	点击原仓库右上角 Fork
2. Clone	把自己账号下的仓库下载到本地	git clone https://github.com/你的名字/仓库名.git
3. Branch	为本次修改创建独立分支，不直接改 main	git checkout -b fix-bug-description
4. Commit	编写代码并提交，提交信息要清晰	git commit -m "fix: handle empty array in geval"
5. Push	把本地分支推送到自己的 GitHub 仓库	git push origin fix-bug-description
6. Open PR	从你的分支发起 Pull Request	GitHub 页面点击 Compare & pull request
7. Review	等待审核并根据反馈继续修改	回复评论、追加提交，直到被合并
先记住一句最重要的话：

永远不要直接在 main 分支上改代码并提交 PR。

这样做的好处是，你的每一次修改都是独立、可回退、可审查的，不会把别的实验性代码混在一起。

2. 开始前先理解：PR 到底是什么#
PR 的全称是 Pull Request。它并不是“把代码直接塞给别人”，而是：

你先在自己的分支完成修改。
然后发起一个“请把我这部分改动拉进来”的请求。
维护者查看差异、提出意见、要求修改或直接合并。
所以 PR 本质上既是代码提交方式，也是沟通方式。好的 PR 不只是在“交代码”，更是在告诉 reviewer：

我改了什么
为什么这样改
影响范围是什么
我已经怎么验证过
3. 第一步：Fork 仓库#
如果你没有原仓库的直接写权限，通常第一步就是 Fork。

Fork 的作用是把原仓库复制一份到你自己的账号下。比如原仓库是：

https://github.com/upstream-owner/project

Fork 之后，你会得到：

https://github.com/your-name/project

后续你的所有修改，都会先推到你自己的这个仓库里，而不是直接推到原作者的仓库。

适用场景很简单：

开源项目贡献代码：通常需要 Fork
团队内部仓库且你有写权限：有时可以直接拉分支，不一定需要 Fork
4. 第二步：Clone 到本地#
Fork 完成后，把自己的仓库克隆到本地：

git clone https://github.com/your-name/project.git
cd project

这一步的作用是把远程代码下载到你电脑上，方便你本地开发、运行和测试。

如果你准备长期给这个项目贡献代码，推荐额外配置一个 upstream，也就是原仓库地址：

git remote add upstream https://github.com/upstream-owner/project.git
git remote -v

这样以后同步原仓库更新会更方便。

5. 第三步：创建分支#
不要在 main 上直接开发，而是为这次任务单独建一个分支：

git checkout -b fix-bug-description

如果你已经提前配置了 upstream，更稳妥的做法是先同步原仓库主分支，再切新分支：

git checkout main
git pull upstream main
git checkout -b fix-bug-description

分支命名建议做到“看名字就知道在做什么”，常见格式如下：

fix-empty-array-bug
docs-update-pr-guide
feat-user-profile
分支名不要起成 test、new-branch、update 这种信息量太低的名字，否则后面自己都容易看不懂。

6. 第四步：编码并提交 Commit#
接下来就是正常改代码、运行测试、确认修改没有问题，然后提交。

git add .
git commit -m "fix: handle empty array in geval"

Commit message 最好满足两个要求：

一眼能看懂你改了什么
使用动词开头，尽量具体
几个对比：

好的写法：fix: handle empty array in geval
好的写法：docs: add pull request workflow guide
不推荐：update code
不推荐：fix bug
如果改动比较复杂，也可以拆成多次 commit。比起一个超大的提交，reviewer 通常更喜欢一组边界清晰的小提交。

7. 第五步：Push 到自己的远程仓库#
本地提交完成后，把分支推送到 GitHub：

git push origin fix-bug-description

第一次推送新分支时，也可以这样写：

git push -u origin fix-bug-description

加上 -u 后，Git 会记住本地分支和远程分支的跟踪关系。以后你再执行 git push、git pull 会更省事。

推送成功后，GitHub 通常会提示你这个分支刚刚更新，并给出一个快捷入口，让你直接发起 PR。

8. 第六步：Open PR#
现在回到 GitHub 页面，你会看到一个 Compare & pull request 按钮。点击之后，就进入创建 PR 的页面。

这里最重要的是检查两件事：

base repository 和 base branch 是否正确
head repository 和 compare branch 是否是你刚才推送的分支
多数情况下，你的目标应该是：

base: upstream-owner/project <- main
compare: your-name/project <- fix-bug-description

PR 标题建议直接概括这次改动，例如：

fix: handle empty array in geval
docs: add GitHub PR workflow guide
feat: support custom avatar upload
PR 描述则建议至少写清楚这几件事：

## 变更内容
- 修复空数组情况下的异常处理

## 为什么修改
- 某些输入会导致函数提前报错

## 如何验证
- 补充了测试用例
- 本地执行相关测试通过

## 影响范围
- 仅影响 `geval` 的边界处理逻辑

如果是界面类修改，附上截图；如果关联某个 Issue，也可以写上 Closes #8613 之类的说明，让 GitHub 在 PR 合并后自动关闭对应 Issue。

9. 第七步：Review 与二次修改#
发起 PR 并不意味着流程结束，很多时候这一步才是真正的协作开始。

维护者可能会：

直接通过并合并
提出代码风格建议
要求补测试
询问为什么这样实现
建议换一种更稳妥的写法
你需要做的是继续在同一个分支上修改，然后再次提交并 push：

git add .
git commit -m "refactor: simplify edge case handling"
git push origin fix-bug-description

不需要重新开一个新的 PR。只要你继续往这个分支 push，当前 PR 会自动更新。

这也是很多新手第一次用 PR 时最容易误解的地方：PR 不是“一次性投递”，而是“围绕同一个分支持续迭代”。

10. 新人最常见的三个坑#
10.1 直接在 main 上改代码#
这是最常见的问题。这样做会让你的工作分支混乱，也不利于后续继续同步上游仓库。

10.2 PR 太大#
如果一个 PR 同时改了 Bug、重构、文档、样式、命名，reviewer 会很难看。尽量做到一个 PR 只解决一个明确问题。

10.3 只写标题，不写描述#
对你自己来说你当然知道改了什么，但 reviewer 不一定知道。PR 描述写得越清楚，审核速度通常越快。

11. 一套适合直接照抄的完整命令#
下面是一套最常见的开源贡献命令流，你可以直接代入仓库地址和分支名：

# 1. 克隆自己的 Fork
git clone https://github.com/your-name/project.git
cd project

# 2. 添加上游仓库
git remote add upstream https://github.com/upstream-owner/project.git

# 3. 同步主分支
git checkout main
git pull upstream main

# 4. 新建功能分支
git checkout -b fix-bug-description

# 5. 修改代码后提交
git add .
git commit -m "fix: handle empty array in geval"

# 6. 推送到自己的仓库
git push -u origin fix-bug-description

然后回到 GitHub 页面，点击 Compare & pull request，补全标题和描述，等待 review 即可。

12. 总结#
一个标准的 GitHub PR 流程，可以概括为：

Fork -> Clone -> Branch -> Commit -> Push -> Open PR -> Review

把这七步跑顺之后，你就已经具备参与大多数开源项目协作的基础能力了。真正的重点不只是“把代码传上去”，而是通过清晰的分支、提交和 PR 描述，让别人更容易理解并接受你的修改。

如果你把 PR 当成一次正式沟通，而不仅仅是一段代码上传，协作体验会顺畅很多。

13. 参考资料#
GitHub Docs: About forks ↗
GitHub Docs: About pull requests ↗
GitHub Docs: Creating a pull request ↗
GitHub Docs: Creating a pull request from a fork ↗
GitHub Docs: Pull requests documentation ↗
Atlassian Git Tutorials: Making a Pull Request ↗
知乎：如何在 Github 上规范的提交 PR（图文详解） ↗
GitHub PR 流程指南：从 Fork 到 Merge 的标准七步法
https://20bytes.github.io/blog/github-pr
Author
昙柏
Published at
April 11, 2026
Copyright
CC BY-NC-SA 4.0

用 GitHub Actions 把关注圈动态整理成每日邮件摘要

构建个人学术追踪系统：自动化 arXiv 论文监控实践


10
%
© 2026 昙柏 & Site policy
Axi-Theme & astro-theme-pure powered
