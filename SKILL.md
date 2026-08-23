---
name: gate-workflow
description: 以人工核准編排需求釐清、GitHub issue、Gate branch／worktree、開發、獨立驗收與結案。當使用者以 backlog、issue 或 Gate 管理工作，或要求草擬／核准 issue、開始／續作／驗收 Gate、處理 PASS／TRIM／REWORK、合併、push 或關閉 issue 時使用；PASS 後自動接續下一 Gate，最後一個 PASS 後詢問是否完整收尾。
---
# Ticket／Gate 人工接力

先讀目前 repo 的 agent instructions、GitHub issue 與本次 Gate 直接相關的文件。專案指令決定
命名、必要測試、驗收判準與 Git 邊界；未規定的部分才使用本技能的預設值。

使用者提到 backlog、issue 或 Gate 時使用本流程。使用者要求「直接做」時當成一般單次任務；
若範圍無法安全地一次完成，先回報並等待使用者決定是否改走 Gate，不自行建立 issue。

一張 issue 使用同一個 branch／worktree 完成所有 Gates。GitHub issue 是 Gate 進度的唯一紀錄。
協調者管理 issue 狀態與接力，開發者只實作目前 Gate，驗收者只驗收。驗收者必須是未參與
該 Gate 開發的另一個 agent／session。除 PASS 後的自動接續外，一次只處理目前接力點；需要
使用者決定時停止。

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

驗收者只讀 issue、issue 留言、目前 Gate、這次 diff 與必要的相關代碼，並依 repo 的專案現實、使用者要求、實際風險、成本與效益判斷是否已是合理實作。可以重跑必要的針對性驗證；不必重跑開發者的全部測試，也不預設重跑會登入外部服務或寫入正式資料的 E2E。

驗收者不修改檔案、不 stage、不 commit，也不更新 GitHub issue。最後只給一個結論：

- `PASS`：目前 Gate 已滿足需求。
- `TRIM`：目前 Gate 做太多；明確指出超出範圍、應刪除或簡化的部分。
- `REWORK`：必要行為缺少、錯誤或驗證失敗；明確指出問題與證據，不提供實作方案。

一個結論可以列出多個直接相關的問題。忽略 nice-to-have、未來重構與無關觀察。回報後停止；
`PASS` 回報本身授權協調者依下一節記錄結果並接續；`TRIM`／`REWORK` 不自動觸發 issue 寫入
或修正。

## 4. 記錄結論與接續 Gate

協調／開發 agent（Agent A）收到可明確對應目前 Gate 與受驗 commit 的獨立驗收結論後：

- `PASS`：直接勾選目前 Gate，並在 issue 內文記錄通過時的受驗 commit，不再等待使用者接受。
  Issue 更新失敗時停止並回報；更新成功且仍有未完成 Gate 時，立即把第一個未勾選 Gate
  當成目前 Gate，沿用同一 branch／worktree，依第 2 節開始開發；完成、驗證、commit 與交接
  後才停止等待驗收，不另問使用者是否開始。
  若這是最後一個 Gate，詢問使用者是否執行第 5 節的完整結案收尾，然後停止等待答覆。
- `TRIM`／`REWORK`：先回報結論並停止。只有使用者明確接受後，Gate 才保持未勾選，且把
  已接受的問題寫成 issue 留言。

開發者處理非 PASS 結論時，先核對問題是否確實屬於目前 Gate。合理就只處理 issue 留言列出的
問題，完成適用驗證、commit 與交接後停止，等待重新驗收；若不合理，回報理由後
停止。

## 5. 結案收尾

最後一個 Gate 記錄 PASS 後，使用以下問題一次列明授權範圍：

> 所有 Gate 已 PASS。是否執行結案收尾（更新文件與最終驗證、合併回預設 branch、清除 issue
> worktree／本機 branch、push 預設 branch、關閉 issue）？

只有使用者明確同意後才依序執行：

1. 開發者更新本次行為真正影響的專案文件；沒有影響就不製造文件變更。執行最後一次適用
   驗證並 commit，確認 issue worktree 乾淨。
2. 協調者確認預設 branch worktree 也乾淨，再把 issue branch 合併回預設 branch。合併衝突就
   停止並回報。
3. 在合併後的預設 branch 執行適用驗證；成功後 push 預設 branch。Push 失敗就保留 issue
   開啟及 issue worktree／branch，停止並回報。
4. 確認 push 成功且 issue worktree 乾淨後，移除該 worktree，並安全刪除已合併的本機 issue
   branch。清理未完整成功時保留 GitHub issue 開啟並回報實際狀態。
5. 前述步驟全數成功後關閉 GitHub issue，回報 merge commit、push、驗證、文件變更、清理與
   issue 狀態。

推送 issue branch、force-push、建立 PR 或刪除 remote branch 不包含在這項授權內，仍須另行
取得使用者明確許可。
