---
name: orca-clean-orphan-workspace
description: Safely diagnose and remove orphaned Orca sidebar workspaces or projects such as Unknown entries when Orca no longer recognizes them, using metadata-only forget-local cleanup while preserving the underlying folder. Do not use for deleting a valid Git worktree or project from disk.
---

# Orca 孤兒工作區安全清理

清除 Orca 側邊欄的 `Unknown`／孤兒工作區，但保留底層資料夾與 Git 資料。先讀取並遵循本機的 `orca-cli` 與 `computer-use` skill；前者負責查詢 Orca 管理狀態，後者負責檢查與操作 Orca 桌面介面。

## 安全界線

- 必須確認唯一的目標 worktree ID、execution host ID 與絕對路徑；不可只靠 `Unknown` 樞紐文字判斷。
- 操作前記錄目標路徑的檔案類型與 inode，並把精確的 Orca 資料檔複製成有時間戳的備份。
- 只可執行 metadata-only 的 `forget-local`；此處的 metadata-only 是指不修改或刪除目標 worktree／repo 的檔案系統內容，但允許更新 Orca 自有 metadata 與 transient state。不可呼叫 `orca worktree rm`、側邊欄 `Delete`、`window.api.worktrees.remove`、`window.api.repos.remove`，也不可用任何檔案系統刪除命令。
- `forget-local` 保護的是底層資料夾與 Git 資料；它可能關閉或清除該孤兒項目綁定的 Orca transient session、PTY、terminal history 或 snapshot。若仍有需要保留的 active session，先停止並告知使用者。
- `/Users/<user>`、`/Users/<user>/dev`、repository 集合目錄或其他廣泛路徑，一律視為高風險保護目標，不可遞迴刪除或交給一般 worktree removal。
- Orca 執行中不可直接手改 live config；renderer 可能覆寫修改或重新建立孤兒項目。

## 診斷

1. 查詢目前 Orca 與環境：

   ```sh
   orca status --json
   orca environment list --json
   ```

2. 對 local 與目前 active／saved environment 分別比對：

   ```sh
   orca project list --environment '<environment>' --json
   orca worktree list --environment '<environment>' --json
   orca terminal list --environment '<environment>' --limit 200 --json
   ```

3. 用 Computer Use 讀取 Orca 側邊欄，確認畫面上的孤兒項目與顯示路徑。再以精確 selector 查詢 `orca worktree show`：若回傳 `selector_not_found`，且有效 project/worktree 清單沒有該目標，才可視為孤兒；若 catalog 仍能辨識它，立即停止，因為它可能是有效工作區。
4. 檢查目前 profile 的資料檔（通常是 `/Users/<user>/Library/Application Support/orca/profiles/local-default/orca-data.json`）。使用 `rg -a -F` 與 `jq` 尋找完整 worktree key、repo UUID、絕對路徑及 host ID，不要只搜尋泛用名稱。

## 優先清理方式

先檢查 Orca 的 Resource Manager／workspace cleanup。只有在介面明確提供「Remove from Orca」或等價的 metadata-only `forget-local`，並明確表示保留磁碟內容時才可使用。

若 cleanup 顯示 0 個候選項目，或側邊欄只提供 `Delete`，不可嘗試 Delete。改讀取並遵循 [renderer-forget-local.md](references/renderer-forget-local.md)，從 Orca renderer 呼叫經版本驗證的 `forget-local` 路徑。

## 驗證

清理後必須全部成立：

- Orca 側邊欄的 `Unknown`／孤兒列已消失。
- live config 不再包含完整 worktree key 或目標絕對路徑。
- 有效 project/worktree 清單與操作前一致。
- 目標路徑仍存在，檔案類型與 inode 與操作前一致。
- Console／API 結果明確為成功（renderer fallback 應為 `{ok: true}`）。

若只剩 `terminalTopologyRevisionByRepoId[repoId]` 的數字 revision marker，且不再含完整 worktree key 或路徑，保留它。這個 marker 用來阻止舊 terminal topology 重新注入孤兒工作區，不是待刪除的 workspace 記錄。備份檔保留舊值也是預期行為；不要為了清除搜尋結果而刪除備份、log、terminal history、LevelDB 或整個 profile。

## 停止條件

遇到任一情況便停止並回報，不要猜測或降級成刪除操作：

- 無法唯一確認目標、host 或絕對路徑。
- Orca catalog 仍把目標辨識為有效 worktree/project。
- 當前 Orca 版本無法證明 `forget-local` 會對應到 `window.api.worktrees.forgetLocal`。
- 無法確認 DevTools Console 的焦點與待執行命令。
- 無法證明清理不會修改或刪除目標 worktree／repo 的檔案系統內容。
