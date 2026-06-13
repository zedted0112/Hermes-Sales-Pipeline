"""Application entry point."""

import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        from hermes_app.web.server import run

        port = 8765
        if len(sys.argv) > 2:
            port = int(sys.argv[2])
        print(f"Starting chat UI → http://127.0.0.1:{port}")
        print("Say hi in the browser — agent updates Report.json → Telegram watcher fires automatically.")
        run(port=port)
        return

    from hermes_app.agent.orchestrator import AgentOrchestrator

    agent = AgentOrchestrator()
    print(agent.run("ready"))
    print("tools:", ", ".join(agent.list_tools()))
    print("\nRun chat UI: PYTHONPATH=src python3 -m hermes_app.main chat")


if __name__ == "__main__":
    main()
