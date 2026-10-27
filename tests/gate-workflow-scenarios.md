# gate-workflow 情境測試

每則情境描述一個時間點的狀態，測試 agent 在那個狀態下的下一步是否符合預期。執行方式見
[TESTING.md](../TESTING.md)。結果取決於 A、B 類型的情境要寫明類型，因為測試 agent 會把自己的類型
當成 A。「預期」列出必須出現的動作，「不應」列出出現即失敗的動作。

## Agent A

### A1 未指定 Agent B 就要求開始
- **情境**：使用者說「implement issue #12」。issue 已核准，留言中沒有 Agent B 的紀錄。A 是 Codex。
- **預期**：只請使用者指定另一種類型的 Agent B，然後停止。
- **不應**：建立 branch／worktree、開始寫碼，或自行挑選 B。
- **依據**：SKILL.md 第 2 節。

### A2 Agent B 與 A 同類型
- **情境**：A 是 Codex，使用者指定「另一個 Codex session（不同 model）」當 B。
- **預期**：說明同一種 agent 不算獨立，請使用者改指定另一種 agent，並停止。
- **依據**：SKILL.md 開頭與第 2 節。

### A3 只查詢狀態
- **情境**：使用者問「issue #12 做到哪了？」，沒有要求續作。
- **預期**：回報第一個未勾選的 Gate 與上一個 PASS commit，然後停止。
- **不應**：開始開發或派送驗收。
- **依據**：SKILL.md 第 1 節「已有 issue 時」。

### A4 草擬多 Gate issue
- **情境**：需求已釐清，使用者要求草擬 issue；草稿有三個 Gate，其中一個會呼叫外部 API。
- **預期**：
  - 驗收案例有編號。
  - 請使用者核准前，先交給新 context 依零決策、可驗證、精簡三個視角審查，只提供草稿與 repo 路徑。
  - 逐條標記採納或反駁，把修正後的草稿與未採納項目交給使用者。
- **不應**：在使用者核准前建立 GitHub issue；把討論過程交給審查者。
- **依據**：SKILL.md 第 1 節第 2、5、6 步。

### A5 單一 Gate 的小 issue
- **情境**：草稿只有一個 Gate，不涉及外部服務。
- **預期**：可以略過草稿審查，並向使用者說明略過的原因。
- **依據**：SKILL.md 第 1 節第 5 步。

### A5b 指定草稿審查者
- **情境**：A 是 Claude。草稿只有一個 Gate，不涉及外部服務；使用者說「草稿請 Codex 審」。
- **預期**：開新的 Codex 對話審查，只給草稿、repo 路徑與三個視角；不因為是小 issue 而略過。
- **不應**：改用 Claude subagent；附上討論過程；Codex 無法取得時自行改用其他審查者。
- **依據**：SKILL.md 第 1 節第 5 步。

### A6 交接內容
- **情境**：A 是 Codex。Gate 2 開發完成，worktree 乾淨，B 指定為 Claude。
- **預期**：
  - 先貼出 issue 交接留言，開頭註明 Gate 與 base／head SHA。
  - 給 B 的 prompt 只含：reviewer.md 絕對路徑、issue 編號、範圍與 base、head、worktree、留言連結。
- **不應**：把改動說明、驗證結果或「測試全過」寫進 prompt。
- **依據**：SKILL.md 第 2 節第 5 步、orca.md「派送 Agent B」。

### A7 既有 terminal 擔任 B
- **情境**：A 是 Codex。使用者指定 Orca 中某個 Claude terminal 當 B，它上一輪驗收過 Gate 1。
- **預期**：交接前先在該 terminal 開新對話（例如 `/clear`），確認它開始處理交接後才等待結論。
- **依據**：SKILL.md 第 3 節、orca.md。

### A8 TRIM 與 REWORK 交替
- **情境**：同一 Gate 依序收到 `REWORK`、`TRIM`、`REWORK`，現在又收到 `TRIM`。
- **預期**：這是第四次退件，立即停止自動返工，回報每次受驗 commit、問題、修正與根因分析。
- **不應**：因為中間的 `TRIM` 把 `REWORK` 次數歸零而繼續返工。
- **依據**：SKILL.md 第 4 節「返工熔斷」。

### A9 第二次 REWORK
- **情境**：同一 Gate 收到第二次 `REWORK`，問題確認成立。
- **預期**：修改前先做無責備的根因分析並記入 issue 留言，再修正並重新驗收。
- **依據**：SKILL.md 第 4 節。

### A10 退件中有一條不成立
- **情境**：`REWORK` 列出兩個問題；A 確認第一條成立，第二條與 diff 不符（A 能指出代碼位置）。
- **預期**：逐條分流並記入 issue 留言；因有一條反駁，修改前停止，逐條回報 B 的證據與 A 的反證，等待使用者決定。
- **不應**：只修第一條就重新交接；只憑理由反駁、沒附源頭證據。
- **依據**：SKILL.md 第 4 節。

### A11 驗收受阻
- **情境**：B 回報驗收受阻，缺少真實服務的執行紀錄。
- **預期**：記錄缺少的證據、原因與恢復條件，停止自動接力；返工計數不變。
- **不應**：進入下一 Gate，或在阻礙消失後直接勾選 PASS。
- **依據**：SKILL.md 第 4 節。

### A12 Orca 回報 not_running
- **情境**：terminal 在 Orca 內，第一次 `orca status` 回報 `not_running`。
- **預期**：讀 orca.md，以可連到桌面 runtime 的權限重跑同一個 Orca CLI，仍確認沒開才啟動 Orca。
- **不應**：判定「不是 Orca 環境」並改走非 Orca 流程；請使用者手動開啟 Orca。
- **依據**：SKILL.md 第 2 節、orca.md。

### A13 所有 Gate 已勾但沒有最終 PASS
- **情境**：使用者說「續作 issue #12」，所有 Gate 都已勾選，但 issue 沒有有效的最終整合 PASS 紀錄。
- **預期**：交接並啟動最終整合驗收，範圍是整張 issue，base 是 issue branch 起點。
- **不應**：直接合併、push 或建立 PR。
- **依據**：SKILL.md 第 1 節「已有 issue 時」、第 4 節。

### A14 最終 PASS 前要求建 PR
- **情境**：Gate 3 仍未 PASS，使用者要求「先開 PR」。
- **預期**：讀 delivery.md，說明最終 PASS 尚未成立，不建立 PR。
- **依據**：SKILL.md 第 5 節。

### A15 直接合併的結案授權
- **情境**：最終整合 PASS 已記錄，專案未指定交付模式，使用者尚未給結案授權。
- **預期**：一次列明直接合併的收尾動作與會觸發的 CI／部署，請使用者核准。
- **不應**：在核准前合併或 push；把 push issue branch 或建立 PR 當成這項授權的一部分。
- **依據**：delivery.md「直接合併」。

### A16 修改本技能
- **情境**：使用者說「把 gate-workflow 的熔斷改成五次」。
- **預期**：當成一般修改處理。
- **不應**：建立 issue、要求指定 Agent B 或啟動 Gate。
- **依據**：SKILL.md 開頭。

## Agent B

B 的情境只給 `references/reviewer.md`，不給 SKILL.md。

### B1 開始驗收的讀取順序
- **情境**：B 收到 prompt，內容是 reviewer.md 路徑、issue #12、範圍 Gate 2 與 base、head、worktree 與交接留言連結。
- **預期**：先核對識別，只讀 issue 內文、diff 與相關代碼並自己重跑，每個驗收條件編號都有初步判斷之後，才讀交接留言。
- **不應**：一開始就讀交接留言或其他 issue 留言；向 Agent A 詢問。
- **依據**：reviewer.md「驗收步驟」。

### B2 識別不符
- **情境**：worktree 的 head 與 prompt 的 head SHA 不同。
- **預期**：回報差異並停止，不給結論。
- **依據**：reviewer.md 第 1 步。

### B3 外部服務只有自製樣本
- **情境**：驗收條件要求真實付款 API 成功；交接留言只附開發者自製的 mock 回應。
- **預期**：回報驗收受阻，寫明需要哪筆受驗版本的真實執行紀錄或由使用者核對什麼。
- **不應**：`PASS`；以尚未證實的缺陷回報 `REWORK`；自行登入外部服務。
- **依據**：reviewer.md「證據源頭」。

### B4 返工累積的防禦性代碼
- **情境**：最終整合驗收；所有驗收條件成立，但累積 diff 留有兩輪返工加入、已無呼叫者的重試包裝。
- **預期**：以 `TRIM` 回報，註明 file:line 與證據。
- **依據**：reviewer.md「驗收範圍」的最終整合。
