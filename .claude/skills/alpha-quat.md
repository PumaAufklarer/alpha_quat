---
name: alpha-quat
description: Alpha Quant project workflow assistant
---

# Alpha Quant Project Skill

## Core Principles (ALWAYS FOLLOW)

1. Use `uv run -m module.name` format for executing scripts
2. One Issue → One MR → One Commit
3. Commit messages follow Conventional Commits: `type(scope): description (#issue-number)`
4. Always rebase main before pushing
5. All content (issues, PRs, commits) in English, no emojis
6. Run `uv run black .` and `uv run ruff check --fix .` before committing

## Workflow Helpers

### Starting New Work

When user asks for new feature/fix:
1. Analyze requirements
2. Propose issue title in CC format (English, no emojis)
3. Wait for user approval
4. Create issue and branch using GitHub CLI

### Before Committing

1. Remind user to run formatters
2. Verify branch is correct
3. Check if rebase is needed

## Quick Reference

### Format and Check

```bash
uv run black .
uv run ruff check --fix .
uv run mypy .  # Optional, for type checking
```

### Commit Message Format

```
type(scope): description (#issue-number)

Types: feat, fix, docs, style, refactor, perf, test, build, ci
```

### Branch Name Format

```
{type}/{issue-number}-{description}
Example: feat/123-add-ci-system
```
