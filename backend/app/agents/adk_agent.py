
import os
import re
import ast
from typing import Any, Dict, Optional

from dotenv import load_dotenv, find_dotenv

from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.genai.types import Content
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from .prompts import ROUTER_SYSTEM_PROMPT
from .tools import (
    create_customer_tool,
    read_customers_tool,
    update_customer_tool,
    delete_customer_tool,
)

# ---------------- env ----------------
env_path = find_dotenv()
load_dotenv(env_path)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set in .env")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
APP_NAME = "customer_crud_demo"

# ---------------- agent & runner ----------------
agent = Agent(
    name="customer_crud_agent",
    model=MODEL_NAME,
    tools=[
        create_customer_tool,
        read_customers_tool,
        update_customer_tool,
        delete_customer_tool,
    ],
)

session_service = InMemorySessionService()
runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

# ---------------- tiny tool executor fallback ----------------

# Map "function name in text" -> actual ADK tool instance
TOOL_MAP = {
    "create_customer_tool": create_customer_tool,
    "read_customers_tool": read_customers_tool,
    "update_customer_tool": update_customer_tool,
    "delete_customer_tool": delete_customer_tool,
    # common mistakes we'll normalize:
    "add_customer": create_customer_tool,
    "create_customer": create_customer_tool,
    "delete_customer": delete_customer_tool,
    "update_customer": update_customer_tool,
    "read_customer": read_customers_tool,
    "read_customers": read_customers_tool,
}

# Which args, and in what order, each tool expects (positional fallback)
POSITIONAL_ARG_ORDER = {
    "create_customer_tool": ["name", "phone", "address"],
    "add_customer": ["name", "phone", "address"],  # alias fix
    "create_customer": ["name", "phone", "address"],

    "read_customers_tool": ["id"],
    "read_customers": ["id"],
    "read_customer": ["id"],

    "update_customer_tool": ["id", "name", "phone", "address"],
    "update_customer": ["id", "name", "phone", "address"],

    "delete_customer_tool": ["id"],
    "delete_customer": ["id"],
}

TOOL_CODE_RE = re.compile(
    r"```tool_code\s*([\w_]+)\s*\((.*?)\)\s*```",
    re.DOTALL | re.IGNORECASE,
)

def _safe_literal_eval(val: str):
    try:
        return ast.literal_eval(val)
    except Exception:
        return val.strip('"').strip("'")

def _parse_tool_from_llm(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse the tool_code line the model returned.
    Supports both named args (name="A") and positional ("A", "+91...", "Delhi").
    Returns:
        dict like {"tool_name": "...", "args": {...}} or None
    """
    m = TOOL_CODE_RE.search(text)
    if not m:
        return None

    fn = m.group(1).strip()
    args_src = m.group(2).strip()

    # Try to parse named args first
    named_args: Dict[str, Any] = {}
    if "=" in args_src:
        # split by commas at top level (no nested)
        parts = [p.strip() for p in args_src.split(",") if p.strip()]
        for p in parts:
            if "=" not in p:
                continue
            k, v = p.split("=", 1)
            named_args[k.strip()] = _safe_literal_eval(v.strip())
    else:
        # positional only
        # split commas, strip, then map using POSITIONAL_ARG_ORDER
        parts = [p.strip() for p in args_src.split(",") if p.strip()]
        # remove surrounding quotes safely
        parts = [_safe_literal_eval(p) for p in parts]
        order = POSITIONAL_ARG_ORDER.get(fn, [])
        named_args = {k: parts[i] if i < len(parts) else None for i, k in enumerate(order)}

    return {"tool_name": fn, "args": named_args}

def _execute_tool(parsed: Dict[str, Any]) -> str:
    tool_name = parsed["tool_name"]
    args = parsed["args"] or {}
    tool = TOOL_MAP.get(tool_name)
    if not tool:
        return f"❌ Unknown tool '{tool_name}'."

    # Let ADK tool validate via its Pydantic schema
    try:
        input_schema = tool.get_input_schema()
        typed_args = input_schema(**args)
    except Exception as e:
        return f"❌ Invalid arguments for {tool_name}: {e}"

    try:
        return tool.run(typed_args)
    except Exception as e:
        return f"❌ Tool {tool_name} crashed: {e}"

def _llm_call(message: str) -> str:
    new_message = Content(
        role="user",
        parts=[{"text": ROUTER_SYSTEM_PROMPT + "\n\nUser: " + message}],
    )

    last_event = None
    for event in runner.run(
        user_id="demo_user",
        session_id="demo_session",
        new_message=new_message,
        run_config=RunConfig(),
    ):
        last_event = event

    # event may have .output / .result / etc.
    for attr in ("output", "result", "message", "content", "text"):
        if hasattr(last_event, attr) and getattr(last_event, attr):
            return str(getattr(last_event, attr))

    return str(last_event)

def run_agent(message: str) -> str:
    # ensure session
    try:
        session_service.create_session(
            app_name=APP_NAME, user_id="demo_user", session_id="demo_session"
        )
    except Exception:
        pass

    # 1) Ask LLM
    raw = _llm_call(message)

    # 2) Try to parse & run tool
    parsed = _parse_tool_from_llm(raw)
    if parsed:
        return _execute_tool(parsed)

    # 3) If we’re still here, force it with extra hint
    raw = _llm_call(message + "\n\nReturn ONLY a valid tool_code call.")
    parsed = _parse_tool_from_llm(raw)
    if parsed:
        return _execute_tool(parsed)

    return f"❌ The model did not return a valid tool call.\nRaw response:\n{raw}"
