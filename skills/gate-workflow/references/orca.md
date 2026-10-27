# Orca 環境的 Gate 操作

terminal 在 Orca 內時，Agent A 依本檔完成 runtime 核對、issue worktree 解析與 Agent B 派送。
其餘規則仍依 [SKILL.md](../SKILL.md)。

## 核對 Orca runtime

若 terminal 本身已在 Orca 內，但第一次 `orca status`／RPC 回報 `not_running`、
`stale_bootstrap` 或 `runtime_unavailable`，先把它視為執行環境權限或連線未通，不足以證明
Orca 沒開。依目前 sandbox／GUI 規則，以可連到桌面 runtime 的權限重跑同一個已選定的 Orca
CLI；只有這次核對仍確認沒開，才依 `$orca-cli` 指引啟動 Orca。啟動後也用相同權限再確認。
核對完成前不要求使用者手動開啟或重開 Orca，也不改用另一個 Orca executable。

## 開始 Gate：解析 issue worktree

建立或沿用 worktree 後必須完成以下動作，才算開始 Gate：

1. 使用 `$orca-cli` 的即時指引，以專案規定的 branch 與路徑建立或解析 Orca 管理的
   issue worktree，取得其完整 id 與絕對路徑。當 Orca 的建立介面無法同時滿足專案指定的
   branch 與路徑時，先依專案命名規則以 `git worktree add` 建立，再讓 Orca 以 branch 或
   絕對路徑解析它；這是同一次自動流程，不另外請使用者操作。
2. 開始開發前，以該絕對路徑核對 Git worktree 根目錄與 branch，確認與 Orca 解析的
   issue worktree 一致。

## 派送 Agent B

開發交接完成後，依 `$orchestration` 的即時指引建立 review Task，並以開發時核對的 issue
worktree 完整 id／絕對路徑啟動獨立的 Agent B。派送前核對 Agent B terminal 所屬的 worktree
是該 issue worktree；從原 worktree 發出指令時，明確指定此目標，不以原 session 的
`active`／`current` 推測。指定既有 terminal 時，交接前先在其中開新對話。

review Task 的 spec 與送給 Agent B 的訊息就是 SKILL.md 第 2 節的一句話 prompt（定位資料）；
改動說明、驗證結果與原因判定只放在 issue 交接留言，讓 B 先獨立判讀。

啟動成功（含 input 已寫入或 TUI idle）只表示終端與交接文字已就位。接著讀 Agent B 畫面，
確認它已開始處理這次交接；停在未送出的輸入框時，依 `$orca-cli` 送出該則交接並再核對一次。
確認開始後才等待 `worker_done`，並依即時指引釋放 Agent B worker。交接已寫入但無法送出時
（例如 terminal 已被使用者接管），回報後停止並請使用者重新指定 Agent B。

`worker_done` 的 outcome 為 `succeeded` 只表示審查工作完成，不等於 Gate PASS；結論從訊息
主旨或內文讀取。不得用非 Orca 的協作工具冒充 Orca orchestration。
