# Kai 的 Orca 工作流程技能包

這個 repository 提供兩個可獨立觸發、也可透過 [`npx skills`](https://github.com/vercel-labs/skills) 一起安裝與更新的 agent skills。

| Skill | 用途 |
| --- | --- |
| `gate-workflow` | 以人工核准編排 GitHub issue、Gate worktree、開發、獨立驗收、返工與結案。 |
| `orca-clean-orphan-workspace` | 安全清除 Orca 側邊欄的 `Unknown`／孤兒工作區，同時保留底層資料夾與 Git 資料。 |

## 一次安裝兩個 skills

需要 Node.js。以下指令會安裝兩個 skills，並讓 `npx skills` 記錄來源以供後續更新：

```sh
npx skills add moxamax/gate-workflow-skill --skill '*' --global
```

安裝程式會詢問目標 agent；選擇實際使用的 Codex、Claude Code 或其他相容 agent 即可。若只想安裝其中一個：

```sh
npx skills add moxamax/gate-workflow-skill --skill gate-workflow --global
npx skills add moxamax/gate-workflow-skill --skill orca-clean-orphan-workspace --global
```

如果以前已從本 repo 安裝過單一的 `gate-workflow`，請重新執行一次「一次安裝兩個 skills」指令。這會登記新的多技能目錄與第二個 skill；之後即可正常更新。

## 更新與確認

同時更新這個技能包的兩個 skills：

```sh
npx skills update gate-workflow orca-clean-orphan-workspace --global
```

確認安裝狀態：

```sh
npx skills list --global
```

## 使用

可直接描述需求讓 agent 自動選用，或明確指定：

```text
使用 $gate-workflow 實作已核准的 issue；Agent B 使用 Claude。
```

```text
使用 $orca-clean-orphan-workspace 清除 Orca 側邊欄的 Unknown 專案，保留底層資料夾。
```

`orca-clean-orphan-workspace` 只允許 metadata-only 的 `forget-local` 路徑；它不會授權刪除目標 worktree、repository 或其檔案系統內容。

## Repository 結構

```text
skills/
├── gate-workflow/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── orca-clean-orphan-workspace/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/renderer-forget-local.md
```
