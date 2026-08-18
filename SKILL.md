---
name: gate-workflow
description: 以人工核准逐步編排需求釐清、GitHub issue、Gate branch／worktree、Agent A 開發、Agent B 獨立驗收與完成清理。草擬或核准 issue、開始或續作 Gate、處理 PASS／TRIM／BLOCK／ADD、完成 issue 時使用；每個接力點都停下等待使用者明確指示。
---

# Ticket／Gate 開發接力

先讀目前 repo 的 agent instructions、GitHub issue 與本次 Gate 直接相關的文件。專案指令決定
命名、必要測試、驗收判準與 Git 邊界；未規定的部分才使用本技能的預設值。

一張 issue 使用同一個 branch／worktree 完成所有 Gates。一次只處理目前接力點。

## 1. 從需求到 issue

1. 仍有會改變方案的未決事項時，使用可用的需求釐清技能；沒有時直接詢問必要問題。
2. 等使用者確認已有共同理解，再草擬一張 GitHub issue，只記錄要達成的結果、依序排列的
   Gates，以及每個 Gate 的 test cases。
3. 等使用者明確核准後才建立 issue。建立後停止，等待建立 worktree 或開始 Gate 1 的指示。

需求已清楚且已有 issue 時，找出第一個尚未 PASS 的 Gate，回報後等待使用者指示。

## 2. 建立 issue worktree

先確認預設 branch、既有 worktree、同名 branch／路徑與未提交變更。保留使用者或來源不明的
變更，不帶入 issue。

專案未指定命名時，預設使用：

- branch：`issue/<編號>-<英文簡稱>`
- 相鄰 worktree：`../<repo 名稱>-issue-<編號>`

只有使用者明確要求時才建立或沿用 worktree。新 worktree 缺少 runtime 時，依專案文件建立。

## 3. Agent A 開發目前 Gate

1. 只實作目前 Gate。
2. 執行 issue 所列且與改動相稱的測試及真實環境 E2E；失敗就找出原因、修正並重跑。
3. 只 stage 本 Gate 的明確路徑並 commit。
4. 回報 Gate 目標、commit、改動檔案、實際驗證與結果。
5. 停止。等使用者明確要求後，才交給另一個 Agent B 驗收。

## 4. Agent B 獨立驗收

只讀 issue、目前 Gate、這次 diff 與必要的相關代碼。依專案的驗收判準只回覆一個結論，
不直接修改，然後停止：

- `PASS`：目前 Gate 已滿足最小需求，可以進下一個 Gate。
- `TRIM`：做太多；明確指出要刪除或簡化的部分。
- `BLOCK`：具體問題使目前 Gate 無法達成應有行為；指出問題，不提供解法。
- `ADD`：尚未滿足最小需求；明確指出缺少的部分。

只判斷目前 Gate。忽略 nice-to-have、未來重構與無關觀察。

收到 `PASS` 後，回報可以進下一個 Gate 並停止。收到其他結論後，回報需處理的問題並停止；
等使用者明確指示後，才由 Agent A 處理被指出的部分。

## 5. 完成 issue

最後一個 Gate PASS 後先停止。只有使用者明確要求完成 issue，才由 Agent A：

1. 更新本次行為真正影響的專案文件；沒有影響就不製造文件變更。
2. 執行最後一次適用驗證並 commit。
3. 確認 issue worktree 與預設 branch worktree 都乾淨。
4. 合併 issue branch 回預設 branch。合併衝突或驗證失敗就停止並回報。
5. 確認預設 branch 正確後，移除乾淨的 issue worktree 並安全刪除本機 branch。
6. 回報 merge commit、驗證結果、文件變更、預設 branch 狀態與未完成事項。

推送 branch、建立 PR 或刪除 remote branch 前，取得使用者明確許可。
