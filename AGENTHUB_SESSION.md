# Seven RPG — AgentHub Session Template
# Directive: agenthub — N parallel competing agents in isolated worktrees; coordinator evaluates and merges winner.

## Session lifecycle: INIT → DISPATCH → MONITOR → EVALUATE → MERGE

### 1. Init
Command: `/hub:hub-init`
- Task: "Build Seven RPG MVP-0 vertical slice"
- Agent count: 3 (competing implementations of the same slice)
- Eval criteria: test pass rate, code simplicity, deterministic state integrity

### 2. Dispatch
Command: `/hub:spawn`
- Agent 1: LangGraph + Python (this reference implementation)
- Agent 2: Alternative stack (to be selected after ADR-0001)
- Agent 3: Minimal Rust/Python hybrid
All agents work in isolated git worktrees; no cross-communication; write results to board only.

### 3. Monitor
Command: `/hub:hub-status`
- Check `.agenthub/board/progress/` for agent updates
- `dag_analyzer.py --status --session {id}` for branch state

### 4. Evaluate
Command: `/hub:eval`
- Metric mode: pytest pass rate in each worktree
- Judge mode: coordinator reads diffs, ranks by correctness/simplicity/quality
- Hybrid: metric first, LLM judge for ties within 10%

### 5. Merge
Command: `/hub:merge`
- `git merge --no-ff` winner into base branch
- Archive losers: `git tag hub/archive/{session}/agent-{i}`
- Clean up worktrees

### Board channels
| Channel | Writer | Reader | Purpose |
|---------|--------|--------|---------|
| dispatch/ | Coordinator | Agents | Task assignments |
| progress/ | Agents | Coordinator | Status updates |
| results/ | Agents + Coordinator | All | Final results + merge summary |

### Agent prompt template
```
You are agent-{i} in hub session {session-id}.
Your task: {task description}
1. Read assignment at .agenthub/board/dispatch/{seq}-agent-{i}.md
2. Work in your worktree — make changes, run tests, iterate
3. Commit all changes with descriptive messages
4. Write result to .agenthub/board/results/agent-{i}-result.md
5. Exit when done
```