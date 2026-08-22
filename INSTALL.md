# 安裝說明（給不熟技術的使用者）

這份 skill 是一套「工作流程說明書」。安裝之後，你在 Orca 這類 ADE 裡跑的 AI coding
agent（Claude Code、Codex⋯）就會照著它一步一步做事，而且每個接力點都會停下來等你點頭。

安裝本身只是「把一個檔案放到正確的資料夾」，下面兩種方法擇一即可。

## 開始之前

- 已經安裝好 Orca（或其他 ADE / agent CLI）。
- 方法 A 需要電腦裡有 Node.js。不確定有沒有、或不想碰指令，直接用方法 B。

## 方法 A：一行指令（推薦）

打開終端機（Orca 內建的終端機也可以），貼上這一行後按 Enter：

```sh
npx skills add moxamax/gate-workflow-skill --global
```

它會問你要裝給哪些 agent，用方向鍵移動、空白鍵勾選你在用的（例如 Claude Code），
再按 Enter 完成。

- 加 `--global`：所有專案都能用（建議）。
- 不加 `--global`：只裝在你目前所在的那個專案資料夾。

## 方法 B：手動放檔案（完全不用指令）

1. 打開 <https://github.com/moxamax/gate-workflow-skill>
2. 按綠色的 **Code** 按鈕 → **Download ZIP**
3. 解壓縮，把資料夾改名成 `gate-workflow`
4. 把它整個搬到 agent 的 skills 資料夾：
   - macOS／Linux：`~/.claude/skills/`（`~` 是你的家目錄，例如 `/Users/你的名字`）
   - Windows：`C:\Users\你的名字\.claude\skills\`

放好之後，路徑看起來要像這樣（最底層直接就是 `SKILL.md`，不要多包一層）：

```
~/.claude/skills/gate-workflow/SKILL.md
```

小提醒：

- 沒有 `skills` 資料夾就自己建一個。
- `.claude` 開頭有一個點，是隱藏資料夾。macOS 在 Finder 按 `Cmd + Shift + .` 可以顯示隱藏檔。
- 用別的工具的話資料夾名稱不同，例如 Cursor 是 `~/.cursor/skills/`、
  OpenCode 是 `~/.opencode/skills/`、Cline 是 `~/.cline/skills/`。不確定就用方法 A。

## 在 Orca 裡確認裝好了

Orca 會自動掃描 Claude、Codex、Agent Skills 與 OMP（`~/.omp/agent/skills`）的 skill 資料夾，
所以放到上面的位置就會被認出來，不需要額外設定。

1. 重開 Orca，或重開 agent 的對話（session）。
2. 到 Orca 設定裡的 Skills 頁面，應該會看到 `gate-workflow`。
3. 也可以在終端機執行 `npx skills list` 確認。

## 怎麼開始用

在 Orca 裡開好你的專案，對 agent 說：

> 使用 gate-workflow 準備目前接力點，完成後停止並等我明確指示下一步。

接下來每個階段（釐清需求 → 建 GitHub issue → 開 worktree → 開發一個 Gate →
另一個 agent 獨立驗收 → 本機合併與清理 → push 並關閉 issue）它都會做完就停，等你明確說
下一步才繼續。本機完成不會自動 push。

驗收結果只會是三種之一：`PASS`（已經夠了）、`TRIM`（做太多）、`REWORK`（必要行為缺少、
錯誤或驗證失敗）。

## 更新與移除

```sh
npx skills update              # 更新
npx skills remove gate-workflow  # 移除
```

用方法 B 安裝的話，更新就是重新下載覆蓋，移除就是把資料夾刪掉。

## 常見問題

- **agent 說找不到這個 skill**：重開一次對話；再檢查資料夾裡是不是直接放著 `SKILL.md`，
  而不是又包了一層 `gate-workflow-skill-main` 之類的資料夾。
- **裝好了但 agent 沒照流程走**：在對話裡直接講出技能名稱 `gate-workflow`。
- **它要建 GitHub issue 卻失敗**：這套流程會用到 GitHub，請先確定電腦上的 GitHub
  指令工具（`gh`）已經登入你的帳號。
