# Kai 的 Orca 工作流程技能包

這個 repository 提供兩個可獨立觸發、也可透過 [`npx skills`](https://github.com/vercel-labs/skills) 一起安裝與更新的 agent skills。

| Skill | 用途 |
| --- | --- |
| `gate-workflow` | 以人工核准編排垂直切片 issue、Gate worktree、開發、獨立驗收、返工與合併／PR 交付。 |
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

Agent B 必須與開發者是不同類型的 agent，且未參與該 Gate 開發；後續 Gates 沿用指定，
每次驗收使用新 session（或使用者指定的既有目標）。

Gate 採可獨立展示或驗證的垂直切片，小 issue 可以只有一個 Gate。核准 issue 時一併約定
測試邊界與驗收環境；適合自動測試的邏輯以一個行為、一個失敗測試、一個最小實作逐段完成，
每個 Gate 同步必要文件後交給獨立驗收者。這沿用 `to-tickets` 的切片與 `tdd` 的測試精神；
Gate 自行編排 commit、審查與交付，不再套用整套 `implement` 流程。

專案規則決定直接合併或 PR 交付，未指定時預設直接合併。開始 Gate 包含本機開發與該 issue
進度紀錄，不自動授權雲端設定或部署。交付只補問尚缺的授權，並列明 push 會觸發的 CI／部署；
PR 交付後等待指定的人合併，issue 與 worktree 保留至實際結案；合併後取得結案授權，
才清除 worktree、本機與遠端 branch 並關閉 issue。

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
