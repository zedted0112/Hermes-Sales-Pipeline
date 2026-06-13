"""Default tool registration."""

from hermes_app.tools import builtin, report
from hermes_app.tools.base import ToolSpec
from hermes_app.tools.registry import ToolRegistry


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="ping",
            description="Health-check — returns pong and timestamp.",
            parameters={
                "type": "object",
                "properties": {"message": {"type": "string", "description": "Optional ping message"}},
            },
        ),
        builtin.ping,
    )

    registry.register(
        ToolSpec(
            name="read_report",
            description="Read the live Report.json project status file.",
            parameters={"type": "object", "properties": {}},
        ),
        lambda **_: builtin.read_report(),
    )

    registry.register(
        ToolSpec(
            name="file_info",
            description="Get metadata for a file or directory relative to project root.",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative path"}},
                "required": ["path"],
            },
        ),
        lambda path, **_: builtin.file_info(path),
    )

    registry.register(
        ToolSpec(
            name="list_tools_dir",
            description="List entries in a project subdirectory.",
            parameters={
                "type": "object",
                "properties": {
                    "subdir": {"type": "string", "description": "Relative directory path"},
                },
            },
        ),
        lambda subdir="tools/custom", **_: builtin.list_tools_dir(subdir),
    )

    registry.register(
        ToolSpec(
            name="system_info",
            description="Return Python version, platform, and project root.",
            parameters={"type": "object", "properties": {}},
        ),
        lambda **_: builtin.system_info(),
    )

    registry.register(
        ToolSpec(
            name="send_telegram",
            description="Send a message to Telegram via hermes send CLI.",
            parameters={
                "type": "object",
                "properties": {"message": {"type": "string", "description": "Text to send"}},
                "required": ["message"],
            },
        ),
        lambda message, **_: builtin.send_telegram(message),
    )

    registry.register(
        ToolSpec(
            name="update_report",
            description=(
                "Update Report.json with summary and a change note. "
                "Saving triggers the Hermes file watcher → Telegram automatically. "
                "Call after every user interaction."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "One-line project status headline"},
                    "change_note": {"type": "string", "description": "What happened this turn"},
                    "change_type": {
                        "type": "string",
                        "description": "Category: chat, feature, fix, test",
                        "enum": ["chat", "feature", "fix", "test"],
                    },
                },
                "required": ["summary", "change_note"],
            },
        ),
        lambda summary, change_note, change_type="chat", **_: report.update_report(
            summary, change_note, change_type
        ),
    )

    return registry
