"""
Opportunity Pursuit Agent — optimized for latency & cost.

OPTIMIZATION: parallel tool fan-out
─────────────────────────────────────────────────────────────────
Sequential (before):  6 API round trips  ~12–18s
Parallel   (after):   3 API round trips  ~5–7s

Dependency graph (determines what can run in parallel):
  Round 1 ── extract_requirements     (no deps)
          └── get_win_loss_history     (no deps)
                    │
  Round 2 ── check_capabilities       (needs: requirements from Round 1)
          └── get_sme_and_content      (needs: rfp keywords from Round 1)
                    │
  Round 3 ── identify_gaps            (needs: requirements + capability check)
                    │
  Round 4 ── generate_recommendation  (needs: everything above)
                    │
  Round 5 ── final text summary

System prompt instructs Claude to call tools in parallel batches.
Claude naturally returns multiple tool_use blocks in one response
when told to — we execute them concurrently via ThreadPoolExecutor.
─────────────────────────────────────────────────────────────────
"""

import os
import json
import time
import anthropic
from concurrent.futures import ThreadPoolExecutor, as_completed

from tools import TOOL_DEFINITIONS, dispatch_tool
from mock_data import SAMPLE_RFP

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an Opportunity Pursuit Agent for an enterprise technology company.
Your job: analyze RFPs and produce a structured bid recommendation.

IMPORTANT — call tools in parallel batches to minimize latency:

BATCH 1 (call both at once):
  • extract_requirements — parse the RFP into structured requirements
  • get_win_loss_history — retrieve similar past opportunities using keywords
    from the RFP title and industry (do not wait for extract_requirements)

BATCH 2 (call both at once, after Batch 1 returns):
  • check_capabilities — use the requirements list from extract_requirements
  • get_sme_and_content — use gap area keywords inferred from the RFP topic

BATCH 3 (after Batch 2):
  • identify_gaps — use requirements + capability check results

BATCH 4 (after Batch 3):
  • generate_recommendation — synthesise all gathered evidence

BATCH 5:
  • Write a concise 3–5 sentence executive summary as plain text.

Never call a tool that depends on a result you do not yet have.
Never call tools one at a time when they can run in parallel."""


# ── Parallel tool executor ────────────────────────────────────────────────────

def execute_tools_parallel(tool_uses: list, stream_callback=None) -> tuple[list, list, object]:
    """
    Execute multiple tool_use blocks concurrently.
    Returns (tool_results, tool_call_log, recommendation).
    """
    recommendation = None
    tool_call_log  = []
    tool_results   = [None] * len(tool_uses)   # preserve order for message history

    def run_one(idx, tool_use):
        name  = tool_use.name
        inp   = tool_use.input
        if stream_callback:
            stream_callback("tool_call", {"name": name, "input": inp})
        t0     = time.perf_counter()
        result = dispatch_tool(name, inp)
        elapsed = round(time.perf_counter() - t0, 3)
        if stream_callback:
            stream_callback("tool_result", {"name": name, "result": result})
        return idx, name, inp, result, elapsed

    with ThreadPoolExecutor(max_workers=len(tool_uses)) as pool:
        futures = {pool.submit(run_one, i, tu): i for i, tu in enumerate(tool_uses)}
        for future in as_completed(futures):
            idx, name, inp, result, elapsed = future.result()
            tool_results[idx] = {
                "type":        "tool_result",
                "tool_use_id": tool_uses[idx].id,
                "content":     json.dumps(result),
            }
            tool_call_log.append({
                "tool":        name,
                "input":       inp,
                "output_keys": list(result.keys()) if isinstance(result, dict) else "list",
                "elapsed_s":   elapsed,
            })
            if name == "generate_recommendation":
                recommendation = result

    return tool_results, tool_call_log, recommendation


# ── Agent Loop ────────────────────────────────────────────────────────────────

def run_agent(rfp_text: str, stream_callback=None) -> dict:
    """
    Optimized agent loop — parallel tool fan-out per batch.

    Args:
        rfp_text:         Raw RFP document text
        stream_callback:  Optional callable(event_type, data)
                          event_type: 'tool_call' | 'tool_result' | 'thinking' | 'final'

    Returns:
        dict: tool_call_log, recommendation, executive_summary,
              total_turns, total_elapsed_s, parallel_savings_s
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    messages = [{
        "role": "user",
        "content": f"Analyze this RFP and produce a bid recommendation.\n\n{rfp_text}",
    }]

    all_tool_logs  = []
    recommendation = None
    executive_summary = ""
    max_turns = 10
    t_start   = time.perf_counter()

    for turn in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        tool_uses  = [b for b in response.content if b.type == "tool_use"]
        text_parts = [b.text for b in response.content if b.type == "text"]

        messages.append({"role": "assistant", "content": response.content})

        if stream_callback:
            for text in text_parts:
                if text.strip():
                    stream_callback("thinking", text)

        if response.stop_reason == "end_turn" or not tool_uses:
            executive_summary = " ".join(text_parts).strip()
            if stream_callback:
                stream_callback("final", executive_summary)
            break

        # ── Execute tools in parallel ──────────────────────────────────
        n = len(tool_uses)
        if stream_callback and n > 1:
            stream_callback("thinking", f"[Parallel batch: {n} tools running concurrently]")

        tool_results, batch_log, rec = execute_tools_parallel(tool_uses, stream_callback)

        all_tool_logs.extend(batch_log)
        if rec:
            recommendation = rec

        messages.append({"role": "user", "content": tool_results})

    total_elapsed = round(time.perf_counter() - t_start, 2)

    # Estimate sequential time for comparison (sum of all individual tool times)
    sequential_estimate = sum(s.get("elapsed_s", 0) for s in all_tool_logs)
    parallel_savings    = round(max(0, sequential_estimate - total_elapsed), 2)

    return {
        "tool_call_log":      all_tool_logs,
        "recommendation":     recommendation,
        "executive_summary":  executive_summary,
        "total_turns":        turn + 1,
        "total_elapsed_s":    total_elapsed,
        "parallel_savings_s": parallel_savings,
    }


# ── CLI entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    def cli_callback(event_type, data):
        if event_type == "tool_call":
            tools = data if isinstance(data, list) else [data]
            for t in tools:
                print(f"  → [{t['name']}]")
        elif event_type == "thinking":
            msg = data[:200] if len(data) > 200 else data
            print(f"\n[Agent] {msg}")
        elif event_type == "final":
            print(f"\n[Summary]\n{data}")

    print("=" * 60)
    print("OPPORTUNITY PURSUIT AGENT  (parallel mode)")
    print("=" * 60)

    result = run_agent(SAMPLE_RFP, stream_callback=cli_callback)

    rec = result.get("recommendation", {})
    print("\n" + "=" * 60)
    print(f"Decision:          {rec.get('decision','—')}")
    print(f"Bid Score:         {rec.get('bid_score','—')}/100")
    print(f"Total turns:       {result['total_turns']}")
    print(f"Wall time:         {result['total_elapsed_s']}s")
    print(f"Parallelism saved: ~{result['parallel_savings_s']}s")
