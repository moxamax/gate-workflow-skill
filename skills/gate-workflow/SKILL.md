---
name: gate-workflow
description: 以人工核准 issue 啟動與結案，並由使用者指定 Agent B，在 Gate 內自動編排 branch／worktree、開發、獨立驗收與返工。當使用者以 backlog、issue 或 Gate 管理工作，或要求草擬／核准 issue、implement／實作 issue、開始／續作 Gate、處理 PASS／TRIM／REWORK、合併、push 或關閉 issue 時使用；開始或續作目前 Gate 後自動接力至最終整合 PASS 或停止條件。
---
# Ticket／Gate 自動驗收接力工作流程

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
只要求準備或查詢狀態，回報後停止；若所有 Gate 已勾選，先核對第 4 節的最終整合驗收紀錄。
若同時要求 `implement issue #<編號>`、實作、開始或續作，視為明確開始目前 Gate，直接進入
下節；沒有未完成 Gate 時，尚無有效最終 PASS 就接續第 4 節的整合驗收，已有則進入第 5 節。

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
   issue worktree，取得其完整 id 與絕對路徑。當 Orca 的建立介面無法同時滿足專案指定的
   branch 與路徑時，先依專案命名規則以 `git worktree add` 建立，再讓 Orca 以 branch 或
   絕對路徑解析它；這是同一次自動流程，不另外請使用者操作。
2. 開始開發前，以該絕對路徑核對 Git worktree 根目錄與 branch，確認與 Orca 解析的
   issue worktree 一致。每次開發與驗證命令明確指定工具的工作目錄，或先 `cd` 到該路徑；
   Git 操作可用 `git -C`，檔案編輯使用該 worktree 內的絕對路徑。

Agent A 的對話／terminal 可以留在原 worktree；實作、驗證、stage 與 commit 的目標都必須
是 issue worktree。這已包含在開始 Gate 的授權內，不需要搬移或重開 session，也不另問
使用者是否允許從原位置操作。Gate 開發期間，主要 worktree 保持在預設 branch 且不承接
本 Gate 的修改。若無法確認或指定正確的操作目標，在修改檔案前停止並回報。後續 Gate 與
返工都沿用同一個 issue worktree。

開發者接著：

1. 只實作目前 Gate，不預做後續 Gate；最終整合返工的範圍依第 4 節。
2. 執行 issue 所列且與改動相稱的測試。改到可執行行為且有適用的真實環境 E2E 時，E2E
   必須成功；已證實的行為錯誤或測試失敗就找出根因、修正並重跑。必要驗證無法完成或證據
   不足時，依第 4 節記錄「驗收受阻」並停止；不適用的驗證則記錄理由，完成其餘適用檢查。
3. 最後 Gate 交接前，完成本次行為真正影響的必要文件與適用驗證；沒有影響就不製造文件變更。
   只 stage 本 Gate 的明確路徑並 commit。Gate 可以有多個 commits；交接前 worktree 必須乾淨。
4. 建立驗收交接資料：issue／Gate 與目標、diff base 完整 SHA、受驗 head 完整 SHA、worktree
   id／絕對路徑、改動檔案、驗收條件對應的驗證證據（執行方式、結果與可核對來源），以及
   **交給驗收者的一句話 prompt**。B 就位時補齊其 agent 類型與 session／terminal 識別。
   最後 Gate 另備妥第 4 節的最終整合驗收範圍與證據。
5. 立即依第 3 節把交接資料交給獨立驗收者並等待結論，不再要求使用者下達驗收指示。

Gate 1 的 diff 起點是 issue branch 的起點；後續 Gate 是上一個 PASS commit。將起點解析為
固定 SHA，不以會移動的 branch 名稱代替。交接後至結論核對完成，A 暫停修改受驗 worktree。

## 3. 獨立驗收

每次開發或返工交接完成後，自動啟動使用者指定的 Agent B 驗收目前 Gate。若使用者指定 agent
類型，每次驗收建立該類型的新 session；若指定既有 session／terminal，使用該唯一目標。若 B
與 A 是同一種 agent、曾參與目前 Gate 開發、無法取得、目標不再唯一，或指定的既有目標不在
該 issue worktree，回報後停止並請使用者重新指定，不自行替換。

若目前環境是 Orca，開發交接完成後，依 `$orchestration` 的即時指引建立 review Task，
並以開發時核對的 issue worktree 完整 id／絕對路徑啟動獨立的 Agent B。
派送前核對 Agent B terminal 所屬的 worktree 是該 issue worktree；從原 worktree 發出
指令時，明確指定此目標，不以原 session 的 `active`／`current` 推測。
啟動成功（含 input 已寫入或 TUI idle）只表示終端與交接文字已就位。
接著讀 Agent B 畫面，確認它已開始處理這次交接；停在未送出的輸入框時，依
`$orca-cli` 送出該則交接並再核對一次。確認開始後才等待 `worker_done`，並依
即時指引釋放 Agent B worker。交接已寫入但無法送出時（例如 terminal 已被使用
者接管），回報後停止並請使用者重新指定 Agent B。
不得用非 Orca 的協作工具冒充 Orca orchestration。其他環境使用其可用的獨立
agent／session 機制，同樣要確認 B 已開始處理交接後才等待結論。無法取得獨立
驗收者時回報後停止，不得由開發者切換身份驗收自己。

B 在開始與結束驗收時核對交接的 issue／Gate、base／head SHA、worktree 及工作目錄狀態；
結論附上同一組識別與 B 的 agent 類型、session／terminal。必要測試產生的檔案須可辨識、
隔離於交付內容之外；只清理由本次測試明確產生的變動，來源不明者保留並釐清。驗收成果仍須
保持乾淨且與交接一致；head 相同不能取代內容核對。

驗收者只讀 issue、issue 留言、目前 Gate、這次 diff 與必要的相關代碼，依適用的 repo 指令，
逐項核對驗收條件與實際證據，確認測試能攔截相關錯誤，並檢查受影響的既有行為。依實際風險、
成本與效益選擇適用的錯誤路徑、邊界條件、相容性與安全性檢查，不擴大至無關重構或未來需求。
可以採用開發者的有效證據或重跑必要的針對性驗證；不必重跑全部測試，也不預設重跑會登入外部
服務或寫入正式資料的 E2E。「測試全過」的摘要或工具執行成功本身不足以證明驗收條件成立。

驗收者不修改受驗檔案、不 stage、不 commit，也不更新 GitHub issue。最後只給一個結論：

- `PASS`：目前 Gate 已滿足需求，必要驗證完成且證據充分；不適用的驗證已說明理由。
- `TRIM`：目前 Gate 做太多；明確指出超出範圍、應刪除或簡化的部分。
- `REWORK`：已證實的必要行為缺少、錯誤或測試失敗（含受影響既有行為的回歸）；明確指出
  問題與證據，不提供實作方案。
- `驗收受阻`：必要驗證未完成或證據不足，尚無法判定；列出缺少的驗證／證據、原因與恢復條件，
  不得 PASS，也不以尚未證實的程式缺陷回報 REWORK。

一個結論可以列出多個直接相關的問題。忽略 nice-to-have、未來重構與無關觀察。回報後停止；
協調／開發 agent 依下一節記錄並接續或停止。使用 Orca 時，完成審查並回報上述任一結論，代表
review Task 已完成，`worker_done` 的 outcome 為 `succeeded`；驗收結論寫在訊息主旨或內文。
這只表示審查工作完成，不等於 Gate PASS；worker 本身未能完成審查時才回報執行失敗。

## 4. 記錄結論與接續 Gate

協調者先核對結論與交接的 issue／Gate、base／head、B 身分及受驗 worktree 狀態。
任一不符（包括 head 相同卻有未提交的受驗內容變更），舊結論不得套用或接續；依下段記錄
差異並保留現況，釐清範圍與變更來源，完成適用修正／驗證後，以新交接重新驗收，不沿用舊 PASS。

每次結論（含 PASS、退件與受阻）皆先由協調者寫入 issue 留言：上述識別、B 的原始結論、
驗收條件與證據、重跑或採用的驗證及來源、未驗證／不適用項目與理由。必要驗證缺漏仍屬
驗收受阻，不能只列為「未驗證」便放行。A 在交接前發現受阻時，記錄當時版本與已有證據，
明示尚未交由 B 驗收，不虛構 B 的身分或結論。任何必要 issue 紀錄寫入失敗都停止接力。

識別核對及紀錄成功後，依結論接續：

- `PASS`：直接勾選目前 Gate，並在 issue 內文記錄通過時的受驗 commit，不再等待使用者接受。
  更新成功且仍有未完成 Gate 時，立即把第一個未勾選 Gate 當成目前 Gate，沿用同一 branch／
  worktree，依第 2 節開發、驗證、commit 與交接後自動再次驗收，不另問使用者是否開始。
  若這是最後一個 Gate，先完成本節的最終整合驗收；只有最終 PASS 紀錄完成才進入第 5 節。
- `驗收受阻`：Gate 保持未勾選，在上述紀錄補上缺少的驗證／證據、原因與恢復條件，停止
  自動接力，不進入下一 Gate，也不增加或重置既有連續 REWORK 次數。恢復條件成立後，補齊
  必要驗證與交接，再由 B 驗收同一 Gate；不得因阻礙消失直接 PASS。
- `TRIM`／`REWORK`：Gate 保持未勾選，在上述紀錄列明直接問題與證據，
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

### 最終整合驗收

逐 Gate 驗收之外，最後自動啟動 B 驗收整張 issue。可與最後 Gate 的驗收合併，但交接與結論
須明列：全部 Gate 的驗收條件、從 issue branch 起點 SHA 到最終 head SHA 的累積 diff、
跨 Gate 互動與受影響的既有功能；不能只看最後 Gate 的增量。必要文件及相關 commits 都須
先完成。另記錄預計合併的預設 branch 與當時 SHA，供結案時核對目標變動。

整合驗收與後續補驗歸最後 Gate 管理，範圍是整張 issue；跨 Gate 回歸屬此次返工範圍，不能
因較早 Gate 曾 PASS 而排除。沿用本節的版本核對、證據紀錄、受阻／退件／根因分析與熔斷
流程及最後 Gate 的連續 REWORK 計數，不另開 Gate 重置次數。未通過時，最後 Gate 保持或
恢復未勾選，保留歷史 PASS 紀錄並標明目前最終 PASS 尚未成立／已失效；不得結案。
合理的 TRIM／REWORK 自動修正、驗證、commit 並重新交接；受阻則依恢復條件補證據再驗收。

最終 PASS 後，由協調者依本節保存整體驗收證據、累積 diff base、最終受驗 head 與目標
branch／SHA，並同步最後 Gate 的 PASS commit。其後若新增變更，先使最終 PASS 失效，
由 B 補驗變更及其影響範圍；影響較大時重新做適用整體驗收，不強制從頭重跑全部測試。
新的最終受驗 SHA 與 PASS 證據記錄成功後才能結案；收尾不能新增未驗收 commit 後直接合併。

## 5. 結案收尾

最終整合 PASS、必要文件與證據均已備妥可供檢視後，使用以下問題一次列明授權範圍：

> 所有 Gate 與最終整合驗收已 PASS。是否執行結案收尾（核對最終受驗版本與最新目標分支、
> 合併回預設 branch、合併後驗證、push 預設 branch、清除 issue worktree／本機 branch、關閉 issue）？

只有使用者明確同意後才依序執行。沒有新增問題時沿用既有結案授權，不重複確認；超出已核准
需求的工作仍先依原有範圍規則交由使用者決定。

1. 核對 issue head 等於紀錄的最終受驗 SHA，issue 與預設 branch worktree 都乾淨，且合併
   目標確為預設 branch。取得並核對該目標的最新遠端狀態（例如 fetch 後核對本機／遠端 SHA），
   不能只憑舊的 remote-tracking ref；合併目標須包含最新遠端內容。將目標與最終驗收記錄的
   目標 SHA 比對；若已變動，先檢查對本 issue 的影響並完成適用整合驗證、保存證據。如須更新 issue branch，依第 4 節重新
   交接與 B 驗收；若需補文件或其他修改也走相同流程。版本／遠端狀態無法確認、驗證受阻或
   失敗、有衝突時都停止交付並回報，不猜測安全。
2. 將已驗收的 issue branch 合併回已核對的預設 branch；合併衝突就停止並回報。以父提交／
   ancestry 與內容差異確認合併結果確實包含已驗收成果，並記錄 issue head 與合併結果 SHA。
   正常 merge commit 可有不同 SHA，不因此當作未驗收的開發 commit；除已核對的目標與
   受驗 issue 內容外，若另有修改，依第 4 節補驗，不得用合併掩蓋未驗收內容。
3. 在合併後的預設 branch 執行適用驗證，將結果記入 issue；成功後才 push 預設 branch。
   合併後驗證或 push 失敗時，保留 issue 開啟及 issue worktree／branch，停止並回報。
4. 確認 push 成功且 issue worktree 乾淨後，移除該 worktree，並安全刪除已合併的本機 issue
   branch。清理未完整成功時保留 GitHub issue 開啟並回報實際狀態。
5. 前述步驟全數成功後關閉 GitHub issue，回報最終受驗 SHA、合併結果 SHA、push、驗證、
   文件變更、清理與 issue 狀態。

推送 issue branch、force-push、建立 PR 或刪除 remote branch 不包含在這項授權內，仍須另行
取得使用者明確許可。
