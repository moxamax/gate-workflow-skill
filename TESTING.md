# 測試

修改 skill 後執行下面兩種檢查。

## 靜態檢查

```sh
python3 scripts/check_skills.py
```

這個檢查只用 Python 標準函式庫，核對三件事：

- 每個 `skills/*/SKILL.md` 的 frontmatter 有 `name`（須等於目錄名稱）與 `description`。
- SKILL.md body 不超過 24,000 bytes（Antigravity 的上限）。超過時，把只有部分情況需要的
  細節移到 `references/`，並在主檔寫明何時讀取。
- 所有 Markdown 的相對連結都指向存在的檔案。

## 情境測試

[情境](tests/gate-workflow-scenarios.md)用來檢查不帶脈絡的 agent 讀完 skill 後，在各種狀態下的
下一步是否符合預期。每則情境都開一個新 session 或 subagent，只給它 skill 檔案與這一則情境；
不要附上修改 skill 時的討論。

Agent A 情境的 prompt：

```text
只讀 <skill 絕對路徑>/SKILL.md，以及它在這個情境中指示你讀的 references。你是 Agent A。
以下是目前狀況。說明你接下來的動作，並引用依據的段落；不要執行任何指令。

<情境內容>
```

Agent B 情境改成只讀 `references/reviewer.md`，身分是 Agent B。

判定方式：回答包含所有「預期」動作，且沒有任何「不應」動作，才算通過。行為會因 agent
類型而不同，所以用實際擔任 A 與 B 的 agent 類型分別跑。修改某一段規則時，至少重跑以該段
為「依據」的情境；新增規則時，一併新增情境。

## 實測紀錄

每次跑情境測試或完整 Gate 流程後加一列。

| 日期 | Commit | A／B | 範圍 | 結果 | 備註 |
| --- | --- | --- | --- | --- | --- |
| 2026-10-27 | `8e9f5b5` | Claude Opus 5.5 subagent／同左 | A4、A6、A8、A10、A12、B1 | 6/6 通過 | 只測 Claude，Codex 未測。A6 初跑因情境沒寫 A 的類型而停止（測試題漏洞，已補 A 類型後重跑通過）。A8 指出熔斷時是否分流不明，已在熔斷規則寫明。 |
| 2026-10-27 | `feat/draft-reviewer` 的工作區 | Claude Opus 5.5 subagent | A5、A5b | 2/2 通過 | 新增「可指定草稿審查者」規則後重跑受影響情境；只測 Claude。 |
