# 项目工作规范

## Git 工作流

- **分支管理**: 所有功能开发在远程创建的分支上进行，先 `git fetch` 查看远程分支，再 checkout 到对应分支
- **提交信息**: 遵循 Conventional Commits 规范，格式: `type(scope): description (#issue-number)`
- **远程优先**: 优先使用远程服务器创建的分支，而不是本地新建
- **描述文件更新**: 提交前需要review并更新readme文件

## 代码规范

- 模块结构清晰，职责分离
- 使用类型提示 (type hints)

## 项目架构

- `data_fetcher/`: 数据获取层
- `tasks/`: 任务调度层
- `backtest/`: 回测框架层
- `scripts/`: 脚本层
