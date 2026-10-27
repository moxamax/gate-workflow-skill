# 交付與結案

最終整合 PASS 紀錄完成後，Agent A 依本檔交付。版本核對、證據紀錄與補驗沿用
[SKILL.md](../SKILL.md) 第 4 節。

依專案規則與 issue 選定交付模式；未指定時預設「直接合併」。最終整合 PASS、必要文件與
證據備妥後，核對專案所需核准與既有授權。尚缺授權時，才按所選模式一次列明具體動作及
已知 CI／部署效果請使用者核准；已明確授權的相同範圍沿用，不重複確認。

兩種模式都先核對受驗 worktree 乾淨、head 等於最終受驗 SHA，並取得目標分支最新遠端狀態
（例如 fetch 後核對 SHA），不能只憑舊的 remote-tracking ref。將最新目標與最終驗收記錄
比對；若已變動，先完成影響檢查與適用驗證並保存證據。若需依專案規則同步目標分支、補文件
或修改 issue branch，依第 4 節使最終 PASS 失效並交由 B 補驗新 head，再更新紀錄。
版本無法確認、驗證受阻或失敗、有衝突時，保留現況並停止交付。

## 直接合併（預設）

尚未取得結案授權時，可用以下問題列明範圍，並補上實際會觸發的 CI／部署：

> 所有 Gate 與最終整合驗收已 PASS。是否執行結案收尾（核對最終受驗版本與最新目標分支、
> 合併回預設 branch、合併後驗證、push 預設 branch、清除 issue worktree／本機 branch、關閉 issue）？

取得明確授權後才依序執行；超出已核准需求的工作仍先交由使用者決定。

1. 核對預設 branch worktree 乾淨，合併目標確為預設 branch，且包含前述最新遠端內容。
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
取得使用者或專案規則的明確授權。

## PR 交付

此模式交由專案指定的人合併；所需的 issue branch push、建立／更新 PR 與預覽部署，沿用
專案或使用者已給的明確授權。未授權部分在操作前列明請求，不套用「直接合併」的結案問題。

1. 完成前述版本與目標核對後，push 已驗收的 issue branch，建立或更新同一張 PR。記錄
   PR 連結、最終受驗 SHA、目標分支與驗證證據，以及尚待指定決定者確認的事項。
2. 核對遠端 branch／PR head 與受驗版本一致；專案要求預覽時，確認對應受驗 head 的部署
   結果並提供連結。失敗時保留 issue、branch 與 worktree，回報實際狀態。
   PR 交付成功後，記錄「已交付，待合併」
   並附 PR 連結；issue 保持開啟，branch／worktree 保留供後續修正。
3. 合併由指定合併者執行；使用者要求代為合併時，該要求即授權這次合併。合併前核對 PR head
   仍等於最終受驗 SHA，依專案規則或 repo 既有慣例選合併方式，刪除 branch 留到第 4 步。
   合併後 fetch，核對 PR 已合併且合併結果包含受驗成果：merge commit 以 ancestry 核對，
   squash／rebase 以內容差異核對。在合併後的預設 branch 執行適用驗證，把 PR 連結、合併
   結果 SHA 與驗證結果記入 issue；受驗內容有變更時，依第 4 節補驗後才清理。
4. 清理需要結案授權；尚未取得時，列明會執行的動作請使用者核准，例如：

   > PR #<編號> 已合併並驗證。是否執行結案收尾（以 fast-forward 更新本機預設 branch、
   > 移除 issue worktree、刪除本機與遠端 issue branch、關閉 issue）？

   取得授權後依序執行；清理未完整成功時保留 GitHub issue 開啟並回報實際狀態。
   1. 本機預設 branch 乾淨時，以 fast-forward 更新到合併結果。
   2. issue worktree 乾淨時移除。
   3. 安全刪除本機 issue branch；squash／rebase 合併使安全刪除被拒時，保留 branch 並請
      使用者決定。
   4. 刪除遠端 issue branch；repo 設定合併後自動刪除時，只核對已刪除。
   5. issue 未被 PR 自動關閉時關閉它，回報合併結果 SHA、驗證、清理與 issue 狀態。

PR 建立、更新或技術 PASS 本身都不授權合併、push 預設 branch、force-push 或刪除 branch。
