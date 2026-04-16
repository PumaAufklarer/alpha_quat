# 项目工作规范

## Git 工作流

- **分支管理**: 所有功能开发在远程创建的分支上进行，先 `git fetch` 查看远程分支，再 checkout 到对应分支
- **提交信息**: 遵循 Conventional Commits 规范，格式: `type(scope): description (#issue-number)`
- **远程优先**: 优先使用远程服务器创建的分支，而不是本地新建
- **描述文件更新**: 提交前需要review并更新readme文件

## 文件操作规范

- **删除前检查**: 删除文件或目录前，先用 `ls` 查看目标文件夹的内容，确认无误后再删除

## 开发工作流

- **测试优先**: 提交代码前必须先运行测试，确认功能无误后才能提交
- **模块运行**: 运行项目脚本使用 `uv run -m module.name` 格式
- **提交修复**: 尚未 push 到远程的提交遇到 bug，应该修复后合并到之前的提交中（amend/rebase），而不是添加一堆 fix 提交
- **代码格式化和检查**:
  - 使用 `black` 进行代码格式化：`uv run black <directory>`
  - 使用 `ruff` 进行代码检查并自动修复：`uv run ruff check --fix <directory>`
  - 提交前必须运行格式化和检查工具

## 代码规范

- 模块结构清晰，职责分离
- 使用类型提示 (type hints)

## 项目架构

- `data_fetcher/`: 数据获取层
- `tasks/`: 任务调度层
- `backtest/`: 回测框架层
- `scripts/`: 脚本层
