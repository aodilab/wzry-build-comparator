---
name: deploy-sync
description: >-
  Build synchronization, dual-repository (public origin vs private commercial) isolation, and Cloudflare deployment workflow.
  Activate whenever running build pipelines, committing code to git, syncing branches, or deploying to Cloudflare.
---

# 构建同步、双仓隔离与线上发布规范 (Deploy & Sync)

在执行构建、Git 提交、分支同步或线上部署（`npx wrangler deploy`）时，必须严格遵守本流程。

## 一、 单一数据源与构建同步
1. **网页端唯一源头**：网页对决台修改以 `dist_pages/compare/index.html` 为基准，修改后必须运行 `python build.py --sandbox`，自动同步至 `dist_pages/index.html`、`index.html` 与 `sandbox.html`，严禁只改单处导致线上与本地不一致。
2. **小程序双端镜像**：修改小程序逻辑或样式时，必须同步维护 `templates/preview/`、`templates/miniprogram/`，并运行 `python build.py --miniprogram` 确保 `preview_miniprogram.html` 与 `miniprogram/` 原生包 1:1 对齐。

## 二、 双仓隔离红线（Public vs Private）
1. **公开开源仓 (`origin` -> `main` 分支)**：
   - 仅允许提交公开基础构建器、8 卷基础文档与前端静态展示页。
   - **严禁提交或泄露**：`AGENTS.md`、`.agents/`、`taobao/`、`miniprogram/`、`templates/`、私有构建脚本及商业 PDF（均已在 `.gitignore` 中屏蔽，严禁在 `main` 分支使用 `git add -f` 强行添加）。
2. **私有全量仓 (`private` -> `private-master` 分支映射至 `private/main`)**：
   - 保存全量商业源码、模板、小程序、海报、PDF、`AGENTS.md` 与 `.agents/skills/`。
3. **并发隔离操作**：
   - 若主工作区处于 `main` 分支或存在多任务并发，操作 `private-master` 时优先在 `scratch/wt_private` 创建临时 `git worktree` 进行提交、推送与 Cloudflare 部署，完成后立即执行 `git worktree remove --force`。

## 三、 线上发布与收尾清场
1. **Cloudflare 部署**：在包含完整 `dist_pages/` 的分支下执行 `npx wrangler deploy`，核对终端输出确保静态资源上传成功并返回最新 `Version ID`。
2. **清场铁律**：每次任务结束或提交前，必须彻底清空 `scratch/` 目录及根目录下的任何临时预览/测试文件，确保 `git status --short` 干净无残留。
