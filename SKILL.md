---
name: gate-workflow
description: 以人工核准逐步編排需求釐清、GitHub issue、Gate branch／worktree、開發、獨立驗收、本機完成與發布。當使用者以 backlog、issue 或 Gate 管理工作，或要求草擬／核准 issue、開始／續作／驗收 Gate、處理 PASS／TRIM／REWORK、完成本機 issue、push 並關閉 issue 時使用；每個接力點完成後停止。
---
# Ticket／Gate 人工接力

先讀目前 repo 的 agent instructions、GitHub issue 與本次 Gate 直接相關的文件。專案指令決定
命名、必要測試、驗收判準與 Git 邊界；未規定的部分才使用本技能的預設值。

使用者提到 backlog、issue 或 Gate 時使用本流程。使用者要求「直接做」時當成一般單次任務；
若範圍無法安全地一次完成，先回報並等待使用者決定是否改走 Gate，不自行建立 issue。

一張 issue 使用同一個 branch／worktree 完成所有 Gates。GitHub issue 是 Gate 進度的唯一紀錄。
協調者管理 issue 狀態與接力，開發者只實作目前 Gate，驗收者只驗收。驗收者必須是未參與
該 Gate 開發的另一個 agent／session。一次只處理目前接力點，完成後停止。

## 1. 從需求到 issue

1. 仍有會改變方案的未決事項時，使用可用的需求釐清技能，如 `$grilling`；若無相關技能，
   只詢問必要問題。需求尚未釐清時不建立 issue。
2. 使用者要求草擬 issue 後，只草擬：要達成的結果、依序排列的 Gates，以及每個 Gate 的
   test cases。每個 Gate 應是一個完整成果，不是實作手段或模糊範圍。
3. Issue 內文以 checkbox 記錄各 Gate；預留 PASS commit。只有使用者明確核准後才建立
   GitHub issue。建立後停止。

已有 issue 時，讀取 issue 與留言，找出第一個未勾選的 Gate 及上一個 PASS commit，回報目前
狀態後停止，等待開始或續作 Gate 的指示。

## 2. 開始或續作 Gate

使用者明確要求開始 Gate 1 時，授權同時建立或沿用該 issue 的 branch／worktree；不再為
worktree 另問一次。開始前先確認預設 branch、既有 worktree、同名 branch／路徑與未提交
變更，保留使用者或來源不明的變更，不帶入 issue。

專案未指定命名時，預設使用：

```sh
git worktree add "../<repo 名稱>-issue-<編號>" \
  -b "issue/<編號>-<英文簡稱>" "<預設 branch>"
git -C "../<repo 名稱>-issue-<編號>" submodule update --init --recursive
```

新 worktree 缺少 runtime 時，依專案文件建立。後續 Gates 沿用同一個 branch／worktree。

開發者接著：

1. 只實作目前 Gate，不預做後續 Gate。
2. 執行 issue 所列且與改動相稱的測試。改到可執行行為且有適用的真實環境 E2E 時，E2E
   必須成功；失敗就找出根因、修正並重跑。外部阻礙使適用驗證無法完成時，明確回報尚未完成。
3. 只 stage 本 Gate 的明確路徑並 commit。Gate 可以有多個 commits；交接前 worktree 必須乾淨。
4. 交接：Gate 目標、diff 起點、最新 commit、改動檔案、實際驗證與結果，以及 **交給驗收者的**  
   **一句話 prompt**。
5. 停止，等待使用者要求驗收。

Gate 1 的 diff 起點是 issue branch 的起點；後續 Gate 是上一個 PASS commit。開發完成不自動
啟動驗收。

## 3. 獨立驗收

只有使用者明確要求驗收目前 Gate 時才開始。驗收者必須是另一個 agent／session；若無法取得
獨立驗收者，回報後停止，不得由開發者切換身份驗收自己。

驗收者只讀 issue、issue 留言、目前 Gate、這次 diff 與必要的相關代碼，並依 repo 的專案現實、
使用者要求、實際風險、成本與效益判斷是否已是最小合理實作。可以重跑必要的針對性驗證；
不必重跑開發者的全部測試，也不預設重跑會登入外部服務或寫入正式資料的 E2E。

驗收者不修改檔案、不 stage、不 commit，也不更新 GitHub issue。最後只給一個結論：

- `PASS`：目前 Gate 已滿足最小需求。
- `TRIM`：目前 Gate 做太多；明確指出超出範圍、應刪除或簡化的部分。
- `REWORK`：必要行為缺少、錯誤或驗證失敗；明確指出問題與證據，不提供實作方案。

一個結論可以列出多個直接相關的問題。忽略 nice-to-have、未來重構與無關觀察。回報後停止；
任何結論都不自動觸發 issue 寫入、修正或下一個 Gate。

## 4. 接受與處理驗收結論

只有使用者明確接受驗收結論後，協調者才更新 GitHub issue：

- `PASS`：勾選目前 Gate，並在 issue 內文記錄通過時的最新 commit。
- `TRIM`／`REWORK`：Gate 保持未勾選，把已接受的問題寫成 issue 留言。

更新後停止。開始下一個 Gate 或處理 `TRIM`／`REWORK` 都要等使用者再次明確指示。

開發者處理非 PASS 結論時，先核對問題是否確實屬於目前 Gate。合理就只處理 issue 留言列出的
問題，完成適用驗證、commit 與交接後停止，等待重新驗收；若不合理，回報理由後
停止。

## 5. 完成本機 issue

最後一個 Gate 記錄 PASS 後先停止。只有使用者明確要求「完成本機 issue」時才執行：

1. 開發者更新本次行為真正影響的專案文件；沒有影響就不製造文件變更。執行最後一次適用
   驗證並 commit，確認 issue worktree 乾淨。
2. 協調者確認預設 branch worktree 也乾淨，再把 issue branch 合併回預設 branch。合併衝突或
   驗證失敗就停止並回報。
3. 確認預設 branch 正確後，移除乾淨的 issue worktree，並安全刪除本機 issue branch。
4. 回報本機 merge commit、驗證結果、文件變更、預設 branch 狀態與未完成事項。GitHub issue
   保持開啟，不 push。

## 6. 發布並關閉 issue

只有使用者明確要求「push 並關閉 issue」時，協調者才確認本機預設 branch 狀態、push 預設
branch，並在 push 成功後關閉 GitHub issue。Push 失敗時保留 issue 開啟並回報。

推送 issue branch、force-push、建立 PR 或刪除 remote branch 不包含在這項授權內，仍須另行
取得使用者明確許可。
