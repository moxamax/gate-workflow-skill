# Renderer `forget-local` fallback

只在 Orca 內建 cleanup 看不到孤兒項目，但 renderer 仍把它顯示在側邊欄時使用。這是高風險、版本敏感的 fallback；每次都要重新驗證目前安裝的 Orca，不可把既有實作當成永久契約。

## 1. 證明目前版本的安全呼叫鏈

在當前 `/Applications/Orca.app/Contents/Resources/app.asar` 中確認下列兩段語意仍存在：

```sh
strings '/Applications/Orca.app/Contents/Resources/app.asar' | rg -F 'if (forgetLocalOnly) return window.api.worktrees.forgetLocal'
strings '/Applications/Orca.app/Contents/Resources/app.asar' | rg -F 'options?.mode === "forget-local"'
```

任一證據不存在就停止，先檢查當前版本的 renderer/store 實作。不要假設舊版 hashed asset 名稱或 API 行為仍相同。

## 2. 建立可回復基線

- 用 `stat` 記錄目標絕對路徑的類型與 inode。
- 對精確的 live data file 建立明確命名的備份，例如：

  ```sh
  cp -p '<live-orca-data.json>' '<explicit-timestamped-backup-path>'
  ```

- 保存操作前有效的 project/worktree 清單，供清理後比對。
- 確認目標沒有仍需保留的 active Orca terminal／PTY session；`forget-local` 可能丟棄這些 transient 狀態，但不得刪除底層資料夾。

不要使用未解析的環境變數、glob 或廣泛路徑作為任何修改目標。

## 3. 從 DevTools 呼叫 renderer store

透過 Orca UI 的 `Toggle Developer Tools` 開啟 DevTools，切換到 Console，確認 JavaScript context 是 Orca renderer 的 `top`。

Computer Use 操作 Console 時：

- 在新的 `Console prompt` 上用 `set-value` 設定完整程式；不要用 `type-text`，它可能重複輸入。
- 按 Return 前重新讀取 accessibility state，確認程式完整出現在 `Console prompt, Value: ...`，而不是 `Terminal input`。
- 焦點或內容不正確時絕不可按 Return。

將下列 placeholder 換成已經交叉驗證的精確值後執行。此程式會從實際載入的 resource 尋找 store，不依賴固定的 hashed asset 檔名：

```js
(async () => {
  const targetId = "<repo-uuid>::<absolute-path>";
  const executionHostId = "<normalized-host-id>";
  const expectedPath = "<absolute-path>";
  const urls = [...new Set(
    performance.getEntriesByType("resource")
      .map(entry => entry.name)
      .filter(name => /\/assets\/store-[^/]+\.js$/.test(name))
  )];
  const modules = await Promise.all(urls.map(url => import(url)));
  const appStore = modules
    .flatMap(module => Object.values(module))
    .find(value =>
      typeof value?.getState === "function" &&
      typeof value.getState()?.removeWorktree === "function"
    );
  if (!appStore) throw new Error("Orca app store not found");
  const target = appStore.getState().allWorktrees()
    .find(worktree =>
      worktree.id === targetId &&
      worktree.hostId === executionHostId
    );
  if (!target) throw new Error("Exact orphan target not found in renderer state");
  if (target.path !== expectedPath) throw new Error("Orphan path mismatch");
  const result = await appStore.getState().removeWorktree(
    { id: targetId, executionHostId },
    false,
    { mode: "forget-local" }
  );
  console.log("FORGET_LOCAL_RESULT", result);
})().catch(error => console.error("FORGET_LOCAL_ERROR", error));
```

只有 Console 顯示 `FORGET_LOCAL_RESULT` 且結果為 `{ok: true}` 才算成功。若找不到 store、精確目標或路徑不符，停止且不要嘗試其他 remove API。

## 4. 關閉 DevTools 並驗證

關閉 DevTools，重新讀取側邊欄與 live config，再比對目標路徑的類型/inode及有效 project/worktree 清單。套用主 `SKILL.md` 的全部驗證條件。

不要把 `window.api.repos.removeForHost` 當作最終修復：它沒有同步拆除 renderer state，孤兒列或部分 key 可能被重新建立。也不要直接從外部呼叫 `window.api.worktrees.forgetLocal` 而略過 renderer store teardown。
