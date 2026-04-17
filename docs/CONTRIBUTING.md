# 贡献指南

## 环境搭建

```bash
# 克隆仓库
git clone <repo-url>
cd alpha_quat

# 安装依赖
uv sync --dev

# 安装 pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install --hook-type pre-push
```

## Git 工作流

### 一个 Issue → 一个 MR → 一个 Commit

- 每个功能或修复对应一个 Issue
- 每个 Issue 对应一个 MR (Pull Request)
- 每个 MR 最终只包含一个 Commit

### 分支命名规范

格式：`{type}/{issue-number}-{description}`

示例：
- `feat/123-add-ci-system`
- `fix/456-fix-data-cache`
- `docs/789-update-readme`

### Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

格式：`type(scope): description (#issue-number)`

Type:
- `feat` - 新功能
- `fix` - 修复
- `docs` - 文档
- `style` - 格式
- `refactor` - 重构
- `perf` - 性能
- `test` - 测试
- `build` - 构建
- `ci` - CI/CD

示例：
- `feat(backtest): add multi-asset support (#11)`
- `fix(data): correct cache lookup logic (#42)`

### 处理反馈修改

收到反馈需要修改时，**不要新增 commit**，使用：

```bash
# 修改代码后
git add .
git commit --amend --no-edit
git push --force-with-lease
```

或者使用 interactive rebase：

```bash
git rebase -i HEAD~2
# 将需要合并的 commit 改为 squash
```

## 代码检查

```bash
# 格式化代码
uv run black .

# Lint 检查
uv run ruff check --fix .

# 类型检查
uv run mypy .

# 手动运行所有 pre-commit checks
uv run pre-commit run --all-files
```

## 运行模块

始终使用 `uv run -m` 格式：

```bash
# 正确
uv run -m scripts.daily_run --limit 10

# 错误
uv run scripts/daily_run.py
```
