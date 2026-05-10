"""
command_parser.py - Parse FRIDAY command strings

Command language:
  -func1("arg1") then func2(42) then tts("Done.")

Rules:
  - Responses starting with '-' are command chains
  - Responses NOT starting with '-' are plain text → speak directly
  - Commands are separated by ' then '
  - Each command: function_name(args...)
"""

import re


def is_command(response: str) -> bool:
    """Returns True if the AI response is a command string."""
    return response.strip().startswith("-")


def parse_commands(response: str) -> list[tuple[str, list]]:
    """
    Parse a command string into a list of (function_name, args) tuples.

    Example:
        Input:  -open_file("C:/notes.txt") then wait(1) then tts("Done.")
        Output: [("open_file", ["C:/notes.txt"]), ("wait", [1]), ("tts", ["Done."])]
    """
    raw   = response.strip().lstrip("-").strip()
    parts = re.split(r'\s+then\s+', raw, flags=re.IGNORECASE)

    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        parsed = _parse_single_call(part)
        if parsed:
            result.append(parsed)
        else:
            print(f"[Parser Warning] Could not parse: '{part}'")

    return result


def _parse_single_call(text: str) -> tuple[str, list] | None:
    match = re.match(r'^(\w+)\s*\((.*)\)$', text.strip(), re.DOTALL)
    if not match:
        return None
    func_name = match.group(1)
    args      = _parse_args(match.group(2).strip())
    return (func_name, args)


def _parse_args(args_str: str) -> list:
    if not args_str:
        return []

    args      = []
    current   = ""
    in_quote  = False
    quote_char = None

    for char in args_str:
        if in_quote:
            if char == quote_char:
                in_quote = False
            current += char
        else:
            if char in ('"', "'"):
                in_quote   = True
                quote_char = char
                current   += char
            elif char == ',':
                args.append(_coerce(current.strip()))
                current = ""
            else:
                current += char

    if current.strip():
        args.append(_coerce(current.strip()))

    return args


def _coerce(raw: str):
    if not raw:
        return ""
    if (raw.startswith('"') and raw.endswith('"')) or \
       (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        pass
    return raw
