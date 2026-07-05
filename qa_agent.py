"""QA Orchestrator: a LangGraph agent that runs the Playwright suite
for demo-app and reports the result as graph state.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

DEMO_APP_DIR = Path(__file__).parent / "demo-app"


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
        return {
            "test_status": "passed",
            "error_logs": "",
            "retry_count": state["retry_count"],
        }

    return {
        "test_status": "failed",
        "error_logs": (result.stdout + result.stderr).strip(),
        "retry_count": state["retry_count"] + 1,
    }


def build_graph():
    graph = StateGraph(QAState)
    graph.add_node("run_playwright_test", run_playwright_test)
    graph.add_edge(START, "run_playwright_test")
    graph.add_edge("run_playwright_test", END)
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
