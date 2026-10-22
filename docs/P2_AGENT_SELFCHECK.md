# P2 Agent 自检差异报告（对照 DeepSeek Flash 基线 × DeepSeek Pro）

> 作者：算法｜执行环境：`/workspace/chainscope`｜时区：Asia/Hong_Kong  
> 生成时间：2026-10-21T23:37:03.730108+08:00（Asia/Hong_Kong）  
> **Finance 三项落地**：A 单一真源 / B model_registry（flash+Pro）/ C Pro 在线自检重跑  
> **本轮追加（Finance 拍板）**：收紧 Pro tool 相位 + 只重跑失败阶段；仍不过则诚实停止  
> 联调真源（public）：`research_version=2026-10-21.p2.deep.b1d`（DeepSeek flash 深核）  
> Pro 对照所用 flash 编排基线快照曾为 `p2.deep.b1c`（见附录）；**demo/联调以 b1d 为准**  
> Pro 在线：`CHAINSCOPE_MODEL_PROFILE=deepseek-pro` → API id `deepseek-v4-pro`  
> 冻结闸门：`docs/CONCEPT_GRADES.md` revision `align-cas14-wind` / `concept_grades_version=2026-10-21.p0`  
> 机器事实附录：`artifacts/qa/p2_agent_selfcheck_facts.json`  
> **本报告不喊验收、不喊盲测；不 push；未改前端视觉；禁止口头通过。**

---

## 0. 结论（先看）

| 项 | 结果 |
|---|---|
| **A. public 单一真源** | **已落地**：`frontend/public/data/snapshot.json` = **`2026-10-21.p2.deep.b1d`**（sha16 `e816a7b2a776a401`）；Pro 残稿**未**接受为 public；Finance 拍板联调以 **b1d** 为准 |
| **B. model_registry** | **已落地** flash + `deepseek-pro` |
| **C. DeepSeek Pro 完整在线同一编排** | **仍未跑通**：首轮 14/15 → 工具相位修补后失败子集重跑 **24 success / 5 failed**；**禁止写「通过」** |
| **本轮动作** | 关工具后动态指令禁止再调 search/read；`ToolOutput.max_retries` 1→3；**只重跑失败缓存**（VERSION/BASE 未改，成功命中 cache） |
| **是否继续刷** | **停止**。剩余 5 个失败主因已变为闸门校验耗尽 / `UsageLimitExceeded`（total_tokens>95000），不是「再刷一轮相位」能诚实宣称解决的 |

**一句话**：tool 相位收紧有效（15→5 失败）；编排仍不完整；**Pro 闸诚实停**；联调真源 **flash b1d**；下一步全力四硬深核，不开 Pro 全量。

**状态标签**：`registry_landed` + `public_ssot_p2_b1d` + `pro_online_incomplete_24of29` + `tool_phase_tightened` + `stopped_no_infinite_retry` + `no_verbal_pass`

---

## 1. A — 单一真源（export）

| 路径 | 角色 |
|---|---|
| `frontend/public/data/snapshot.json` | **唯一 UIUX 真源**；仅 `scripts/export_p2_joinable.py`（含 `--sync-public`）覆盖 |
| `artifacts/frontend/snapshot.p2.joinable.json` | 与 public 同字节的备份 |
| `artifacts/frontend/snapshot.round2.p1.json` | 旧 p1/round2 编辑集备份；`export_frontend.py` **只写这里** |

本轮核对：

1. public `meta.research_version=2026-10-21.p2.deep.b1c`，sha16 `4d3a2c68dcd34ac4`  
2. Pro 重跑写入 `data/round2/agent_research.json` 后**已恢复** flash 工作树；QA 副本在 `artifacts/qa/agent_research.deepseek-pro.json`  
3. 重跑窗口内 public 曾被误回 `b1c`；**已重新 `export_p2_joinable` 恢复并校验为 `p2.deep.b1d`**（Finance 拍板联调真源）。Pro 残稿从未作为 demo 真源。

---

## 2. B — model_registry

（同前轮，未改）`config/model_registry.json`：`deepseek`→`deepseek-flash`；`deepseek-pro`→`deepseek-v4-pro`。env：`CHAINSCOPE_MODEL_PROFILE=deepseek-pro`。

---

## 3. C — DeepSeek Pro 在线重跑记录

### 3.1 首轮（历史）

14 success / 15 failed；根因见旧节：关工具后仍调 `search_evidence`/`read_evidence` → Unknown tool → 耗尽 `max_retries=1`。

日志：`artifacts/qa/pro_run/stdout.log`

### 3.2 代码收紧（本轮）

文件：`scripts/round2_agents.py`（**未改** `VERSION` / `BASE`，故成功阶段 cache 仍命中）

1. **关工具**：`prepare=within_budget` 在 `tool_events>=6` 时仍返回 `None`（schema 仅剩 `final_result`）  
2. **相位指令**：`@agent.instructions` 在关工具后追加「禁止再调 search/read/…；立即 `final_result`」  
3. **略增 output retry**：`ToolOutput(..., max_retries=3)`（原 1）

### 3.3 失败子集重跑

```text
# Asia/Hong_Kong 2026-10-21T23:25:26+0800 → 2026-10-21T23:36:14+0800
set -a; source ../API及接口/.env; set +a
export CHAINSCOPE_MODEL_PROFILE=deepseek-pro PYDANTIC_AI_NO_BANNER=1
.venv/bin/python scripts/round2_agents.py
# → finished=true; failed_stages=5; model=deepseek-v4-pro; profile=deepseek-pro
# 成功阶段 status=cached；原失败阶段重跑
```

日志：`artifacts/qa/pro_run_retry/stdout.log`  
产物：`artifacts/qa/agent_research.deepseek-pro.json`

| 状态 | 首轮 | 本轮重跑后 |
|---|---:|---:|
| success | 14 | **24** |
| failed | 15 | **5** |

剩余失败：

| role | subject | error |
|---|---|---|
| business_evidence | cohr | UnexpectedModelBehavior |
| business_evidence | vrt | UnexpectedModelBehavior |
| adversarial_review | inspur_smci | UsageLimitExceeded |
| research_editor | inspur_smci | UsageLimitExceeded |
| adversarial_review | envicool_vrt | UsageLimitExceeded |

迹内细分（诚实）：

- `business_evidence.cohr` / `vrt`：仍出现关工具后 Unknown tool 与闸门 `ModelRetry`（未接地数字），在 `max_retries=3` 下仍耗尽  
- `adversarial_review.inspur_smci` / `research_editor.inspur_smci` / `adversarial_review.envicool_vrt`：`UsageLimitExceeded`（`total_tokens_limit=95000` 被突破，约 109k–116k）——属用量上限，不是再刷相位能宣称修好的

### 3.4 稳定性 / 准确性

- **稳定性**：相对首轮 Pro 明显改善（15→5），仍显著差于可交付完整稿的 flash 基线。  
- **准确性**：整体编排仍有 5 个空位；**不得**评为准确性通过。可比较子集未做新的全量 grade 审计。

---

## 4. Flash 基线（未因 Pro 重跑改写）

public / 工作树 `data/round2/agent_research.json` 已回到 flash；unittest `tests.test_round2` 本轮 8 ok（含 tool-before-output）。

---

## 5. 改动文件清单（本轮追加）

| 文件 | 变更 |
|---|---|
| `scripts/round2_agents.py` | 关工具后相位指令；`ToolOutput.max_retries` 1→3 |
| `docs/P2_AGENT_SELFCHECK.md` | 本文件 |
| `artifacts/qa/p2_agent_selfcheck_facts.json` | 机器附录 |
| `artifacts/qa/pro_run_retry/*` | 失败子集重跑日志与前后备份 |
| `artifacts/qa/agent_research.deepseek-pro.json` | 更新后的 Pro 产物 |

**未改**：前端视觉 / 不 push / Pro 残稿不盖 public（联调真源已对齐 b1d）。

---

## 6. 通过标准对照（本轮自评）

| Finance 要求 | 本轮 |
|---|---|
| 收紧 Pro tool 相位；关工具后禁再调 search/read；可略增 output retry | ✅ |
| `CHAINSCOPE_MODEL_PROFILE=deepseek-pro` **只重跑失败阶段** | ✅（成功 cached） |
| 更新本报告；仍不过诚实停、不无限刷 | ✅ **停止于 5 failed** |
| Pro 残稿不准盖 public；demo 真源 flash `p2.deep.b1d` | ✅ 已恢复核对 |
| 不 push；不改前端视觉 | ✅ |

**最终标签：`A_done` + `B_done` + `C_pro_tool_phase_improved_still_incomplete_5of29` + `stopped_honest` — 禁止「通过」。**
