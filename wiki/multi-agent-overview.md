
# Multi-Agent Systems

Networks of specialised agents collaborating to solve tasks too large or complex for a single context window. Each agent owns a bounded slice of the problem — a tool set, a domain, or a step in a workflow.

## When to Use Multi-Agent

Three legitimate reasons to go multi-agent (LangChain):

1. **Context management** — load specialised knowledge selectively instead of stuffing everything into one context window.
2. **Distributed development** — independent teams own separate agents with clear interfaces.
3. **Parallelisation** — spawn multiple workers for concurrent subtasks, reducing latency.

> "Not every complex task requires this approach — a single agent with the right tools and prompt can often achieve similar results."

## Five Architectural Patterns

See [Agent Orchestration Patterns](concepts/agent-orchestration-patterns.md) for full detail on each pattern's tradeoffs, selection guidance, and performance data.

## Subagents Deep Dive

The Subagents pattern has two implementation variants and two execution modes — see dedicated pages:

- [Subagent Implementation Patterns](concepts/subagent-implementation.md) — Tool-per-agent vs Single Dispatch, state/checkpointing, LangGraph limitations
- [Agent Execution Modes](concepts/agent-execution-modes.md) — sync, async (3-tool pattern), parallel
- [Agent Discovery](concepts/agent-discovery.md) — system prompt, enum, or `list_agents` tool

## Central Design Principle

> "At the center of multi-agent design is **context engineering** — deciding what information each agent sees."

See [Context Engineering](concepts/context-engineering.md).

## Performance

No pattern dominates all workloads. See [Multi-Agent Performance Tradeoffs](concepts/multi-agent-performance-tradeoffs.md) for model-call and token cost comparisons.

## Related

- [ReAct Agents](react-agents.md) — single-agent reasoning pattern that multi-agent systems build on
- [Agent Orchestration Patterns](concepts/agent-orchestration-patterns.md)
- [Context Engineering](concepts/context-engineering.md)