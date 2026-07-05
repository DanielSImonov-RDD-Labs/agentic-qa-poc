"""QA Orchestrator: a LangGraph agent that runs the Playwright suite
for demo-app and self-heals failing tests using Claude.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TypedDict

import anthropic
from langgraph.graph import StateGraph, START, END

DEMO_APP_DIR = Path(__file__).parent / "demo-app"
TEST_FILE = DEMO_APP_DIR / "tests" / "login.spec.ts"
MAX_RETRIES = 3

client = anthropic.Anthropic()


class QAState(TypedDict):
    test_status: str
    error_logs: str
    retry_count: int


def run_playwright_test(state: QAState) -> QAState:
    """Run the Playwright E2E suite in demo-app and report the outcome."""
    # shell=True is required because `npx` resolves to a .cmd shim on Windows,
    # which Python's subprocess cannot exec directly without going through a shell.
    # The command is a fixed string with no user input, so this is not injectable.
    result = subprocess.run(
        "npx playwright test",
        cwd=DEMO_APP_DIR,
        capture_output=True,
        text=True,
        shell=True,
    )

    if result.returncode == 0:
        return {**state, "test_status": "passed", "error_logs": ""}

    return {
        **state,
        "test_status": "failed",
        "error_logs": (result.stdout + result.stderr).strip(),
    }


def analyze_failure_agent(state: QAState) -> QAState:
    """Ask Claude to self-heal the failing Playwright test from its error logs."""
    current_code = TEST_FILE.read_text()

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=(
            "You are a self-healing QA agent. You are given the current contents of a "
            "Playwright test file and the error output from its most recent failing run. "
            "Respond with ONLY the corrected, complete TypeScript test file content that "
            "fixes the failure — no markdown code fences, no explanations, no text other "
            "than the raw file contents."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Current test file ({TEST_FILE.name}):\n\n{current_code}\n\n"
                    f"Playwright error output from the failing run:\n\n{state['error_logs']}\n\n"
                    "Fix the test so it passes."
                ),
            }
        ],
    )

    corrected_code = next(
        (block.text for block in response.content if block.type == "text"), ""
    ).strip()
    corrected_code = _strip_code_fences(corrected_code)

    if corrected_code:
        TEST_FILE.write_text(corrected_code + "\n")

    return {**state, "retry_count": state["retry_count"] + 1}


def _strip_code_fences(text: str) -> str:
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)
    return text


def route_after_test(state: QAState) -> str:
    """Retry a failed test via self-healing, up to MAX_RETRIES, otherwise stop."""
    if state["test_status"] == "passed":
        return END
    if state["retry_count"] < MAX_RETRIES:
        return "analyze_failure_agent"
    return END


def build_graph():
    graph = StateGraph(QAState)
    graph.add_node("run_playwright_test", run_playwright_test)
    graph.add_node("analyze_failure_agent", analyze_failure_agent)

    graph.add_edge(START, "run_playwright_test")
    graph.add_conditional_edges(
        "run_playwright_test",
        route_after_test,
        {"analyze_failure_agent": "analyze_failure_agent", END: END},
    )
    graph.add_edge("analyze_failure_agent", "run_playwright_test")

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    initial_state: QAState = {
        "test_status": "pending",
        "error_logs": "",
        "retry_count": 0,
    }

    final_state = app.invoke(initial_state)

    print(f"test_status: {final_state['test_status']}")
    print(f"retry_count: {final_state['retry_count']}")
    if final_state["error_logs"]:
        print("error_logs:")
        print(final_state["error_logs"])
