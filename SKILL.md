---
name: gate-workflow
description: 以人工核准 issue 啟動與結案，並由使用者指定 Agent B，在 Gate 內自動編排 branch／worktree、開發、獨立驗收與返工。當使用者以 backlog、issue 或 Gate 管理工作，或要求草擬／核准 issue、implement／實作 issue、開始／續作 Gate、處理 PASS／TRIM／REWORK、合併、push 或關閉 issue 時使用；開始或續作目前 Gate 後自動接力至最後 PASS 或停止條件。
---
# Ticket／Gate 自動驗收接力

先讀目前 repo 的 agent instructions、GitHub issue 與本次 Gate 直接相關的文件。專案指令決定
命名、必要測試、驗收判準與 Git 邊界；未規定的部分才使用本技能的預設值。

使用者提到 backlog、issue 或 Gate 時使用本流程。使用者要求「直接做」時當成一般單次任務；
若範圍無法安全地一次完成，先回報並等待使用者決定是否改走 Gate，不自行建立 issue。

一張 issue 使用同一個 branch／worktree 完成所有 Gates。GitHub issue 是 Gate 進度的唯一紀錄。
協調者管理 issue 狀態與接力，開發者只實作目前 Gate，驗收者只驗收。驗收者必須是未參與
該 Gate 開發的另一種 agent 且使用另一個 session；不同 model 或不同 session 的同一種 agent
不算獨立，例如 Codex 不得同時擔任 Agent A 與 Agent B。使用者開始或續作目前 Gate 後，開發、
獨立驗收、合理退件修正與下一 Gate 自動接力；只有本技能列明的停止條件需要使用者決定。

## 1. 從需求到 issue

1. 仍有會改變方案的未決事項時，使用可用的需求釐清技能，如 `$grilling`；若無相關技能，
   只詢問必要問題。需求尚未釐清時不建立 issue。
2. 使用者要求草擬 issue 後，只草擬：要達成的結果、依序排列的 Gates，以及每個 Gate 的
   test cases。每個 Gate 應是一個完整成果，不是實作手段或模糊範圍。
3. Issue 內文以 checkbox 記錄各 Gate；預留 PASS commit。只有使用者明確核准後才建立
   GitHub issue。建立後停止。

已有 issue 時，讀取 issue 與留言，找出第一個未勾選的 Gate 及上一個 PASS commit。若使用者
只要求準備或查詢狀態，回報後停止；若同時要求 `implement issue #<編號>`、實作、開始或續作，
視為明確開始目前 Gate，直接進入下節，不在狀態回報後停止。

## 2. 開始或續作 Gate

使用者明確要求開始或續作目前 Gate 時，必須同時指定 Agent B。可指定 agent 類型（例如
Codex／Claude；每次驗收開新 session）或可唯一辨識的既有 agent session／Orca terminal。
Agent B 的類型必須與 Agent A 不同；指定既有目標時也先確認其 agent 類型。未指定或類型相同時，
只請使用者指定另一種 Agent B 並停止，不開始開發。把 A、B 類型及 B 的指定方式記錄為 issue
留言，並沿用至整張 issue 完成；除非使用者另行指定，不自行更換 B。

開始 Gate 1 同時授權建立或沿用該 issue 的 branch／worktree；不再為 worktree 另問一次。
開始前先確認預設 branch、既有 worktree、同名 branch／路徑與未提交變更，保留使用者或來源
不明的變更，不帶入 issue。

專案未指定命名時，預設使用：

```sh
git worktree add "../<repo 名稱>-issue-<編號>" \
  -b "issue/<編號>-<英文簡稱>" "<預設 branch>"
git -C "../<repo 名稱>-issue-<編號>" submodule update --init --recursive
```

新 worktree 缺少 runtime 時，依專案文件建立。後續 Gates 沿用同一個 branch／worktree。

若 terminal 本身已在 Orca 內，但第一次 `orca status`／RPC 回報 `not_running`、
`stale_bootstrap` 或 `runtime_unavailable`，先把它視為執行環境權限或連線未通，不足以證明
Orca 沒開。依目前 sandbox／GUI 規則，以可連到桌面 runtime 的權限重跑同一個已選定的 Orca
CLI；只有這次核對仍確認沒開，才依 `$orca-cli` 指引啟動 Orca。啟動後也用相同權限再確認。
核對完成前不要求使用者手動開啟或重開 Orca，也不改用另一個 Orca executable。

若目前環境是 Orca，建立或沿用 worktree 後必須完成以下動作，才算開始 Gate：

1. 使用 `$orca-cli` 的即時指引，以專案規定的 branch 與路徑建立或解析 Orca 管理的
   issue worktree，並讓目前 session 切換到該 worktree 擔任 Agent A。當 Orca 的建立介面
   無法同時滿足專案指定的 branch 與路徑時，先依專案命名規則以 `git worktree add` 建立，
   再讓 Orca 以 branch 或絕對路徑解析它；這是同一次自動流程，不另外請使用者操作。
2. 開始開發前核對目前 session 的 worktree id、工作目錄與 branch 都是這張 issue 的
   worktree。

若目前 session 不在正確的 issue worktree，在修改檔案前停止並回報。後續 Gate 與
返工都沿用同一個 Orca worktree，不建立第二個 issue worktree。

開發者接著：

1. 只實作目前 Gate，不預做後續 Gate。
2. 執行 issue 所列且與改動相稱的測試。改到可執行行為且有適用的真實環境 E2E 時，E2E
   必須成功；失敗就找出根因、修正並重跑。外部阻礙使適用驗證無法完成時，明確回報尚未完成。
3. 只 stage 本 Gate 的明確路徑並 commit。Gate 可以有多個 commits；交接前 worktree 必須乾淨。
4. 建立驗收交接資料：Gate 目標、diff 起點、受驗 commit、改動檔案、實際驗證與結果，以及
   **交給驗收者的一句話 prompt**。
5. 立即依第 3 節把交接資料交給獨立驗收者並等待結論，不再要求使用者下達驗收指示。

Gate 1 的 diff 起點是 issue branch 的起點；後續 Gate 是上一個 PASS commit。

## 3. 獨立驗收

每次開發或返工交接完成後，自動啟動使用者指定的 Agent B 驗收目前 Gate。若使用者指定 agent
類型，每次驗收建立該類型的新 session；若指定既有 session／terminal，使用該唯一目標。若 B
與 A 是同一種 agent、曾參與目前 Gate 開發、無法取得、目標不再唯一，或指定的既有目標不在
該 issue worktree，回報後停止並請使用者重新指定，不自行替換。

若目前環境是 Orca，開發交接完成後，依 `$orchestration` 的即時指引建立 review Task，
並以目前這個 issue worktree 的完整 id／絕對路徑啟動獨立的 Agent B。
派送前核對 Agent B terminal 所屬的 worktree 與目前 session 相同。
啟動成功（含 input 已寫入或 TUI idle）只表示終端與交接文字已就位。
接著讀 Agent B 畫面，確認它已開始處理這次交接；停在未送出的輸入框時，依
`$orca-cli` 送出該則交接並再核對一次。確認開始後才等待 `worker_done`，並依
即時指引釋放 Agent B worker。交接已寫入但無法送出時（例如 terminal 已被使用
者接管），回報後停止並請使用者重新指定 Agent B。
不得用非 Orca 的協作工具冒充 Orca orchestration。其他環境使用其可用的獨立
agent／session 機制，同樣要確認 B 已開始處理交接後才等待結論。無法取得獨立
驗收者時回報後停止，不得由開發者切換身份驗收自己。

驗收者只讀 issue、issue 留言、目前 Gate、這次 diff 與必要的相關代碼，並依 repo 的專案現實、使用者要求、實際風險、成本與效益判斷是否已是合理實作。可以重跑必要的針對性驗證；不必重跑開發者的全部測試，也不預設重跑會登入外部服務或寫入正式資料的 E2E。

驗收者不修改檔案、不 stage、不 commit，也不更新 GitHub issue。最後只給一個結論：

- `PASS`：目前 Gate 已滿足需求。
- `TRIM`：目前 Gate 做太多；明確指出超出範圍、應刪除或簡化的部分。
- `REWORK`：必要行為缺少、錯誤或驗證失敗；明確指出問題與證據，不提供實作方案。

一個結論可以列出多個直接相關的問題。忽略 nice-to-have、未來重構與無關觀察。回報後停止；
`PASS`、`TRIM`、`REWORK` 都授權協調／開發 agent 依下一節記錄並接續。使用 Orca 時，三種
結論都代表 review Task 已成功完成，`worker_done` 的 outcome 應為 `succeeded`；結論寫在訊息
主旨或內文，不把 `REWORK` 誤報成 worker 執行失敗。

## 4. 記錄結論與接續 Gate

協調者收到可明確對應目前 Gate 與受驗 commit 的獨立驗收結論後：

- `PASS`：直接勾選目前 Gate，並在 issue 內文記錄通過時的受驗 commit，不再等待使用者接受。
  Issue 更新失敗時停止並回報；更新成功且仍有未完成 Gate 時，立即把第一個未勾選 Gate
  當成目前 Gate，沿用同一 branch／worktree，依第 2 節開始開發；完成、驗證、commit 與交接
  後自動再次驗收，不另問使用者是否開始。
  若這是最後一個 Gate，詢問使用者是否執行第 5 節的完整結案收尾，然後停止等待答覆。
- `TRIM`／`REWORK`：Gate 保持未勾選，把結論、受驗 commit、直接問題與證據寫成 issue 留言，
  接著依下列退件迴圈處理，不等待使用者接受。

開發者處理非 PASS 結論時，先核對問題是否確實屬於目前 Gate。若不合理，回報理由後停止。
合理就只處理 issue 留言列出的問題。處理 `REWORK` 前，先判定問題的直接原因、影響範圍及
既有驗證未攔截的原因，並在下一次交接中附上判定證據；證據不足時，明確回報尚未確定之處。

若問題涉及高風險或嚴重缺陷（如安全、資安、資料損失、正式環境或核心功能）、顯示流程性
缺口、與既有問題相似，或同一 Gate 收到第二次連續且確認合理的 `REWORK`，則在再次修改前
進行無責備的根因分析，並把已確認的原因與促成因素、證據、既有驗證漏接原因及預防再發措施
記錄為 issue 留言。分析深度與實際風險、成本及效益相稱。

根因分析不擴大目前 Gate 的實作範圍；新增的預防措施若超出 issue 留言列出的問題，回報並等待
使用者決定。完成適用驗證、commit 與交接後，自動重新驗收。

### 連續 REWORK 熔斷

協調者按同一 Gate 的驗收順序記錄連續 `REWORK` 次數；`PASS`、`TRIM` 或進入下一 Gate 後歸零。
`TRIM` 與未達熔斷條件的 `REWORK` 都自動接受、記錄、處理並重新驗收：

- 第一次 `REWORK`：依前述規則自動處理。
- 第二次連續 `REWORK`：完成前述根因分析後，允許一次有證據支持的修正與重新驗收。
- 第三次連續 `REWORK`：立即停止自動返工。回報每次受驗 commit、退件問題、已做修正、驗證、
  根因分析與仍未確定之處，等待使用者決定是修改 Gate／issue、指定處理方向或終止工作。

同一問題在根因分析後再次出現，視為已達停止條件，不以改寫程式、換驗收者或拆成新問題重置
計數。驗收結論無法明確對應目前 Gate 與受驗 commit 時也停止，不把不確定結論帶入自動返工。

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
