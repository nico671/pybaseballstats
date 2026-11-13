"""Keep runnable guide snippets aligned with supported public names and signatures."""

import ast
import importlib
import inspect
import re
from pathlib import Path

from pybaseballstats import enums

ROOT = Path(__file__).resolve().parents[1]


def test_guide_code_uses_supported_public_names():
    for path in [ROOT / "README.md", *sorted((ROOT / "usage_docs").glob("*.md"))]:
        for code in re.findall(r"```python\n(.*?)```", path.read_text(), re.S):
            tree = ast.parse(code, filename=str(path))
            aliases = {}
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for item in node.names:
                        if item.name.startswith("pybaseballstats."):
                            aliases[item.asname or item.name] = importlib.import_module(
                                item.name
                            )
                elif (
                    isinstance(node, ast.ImportFrom)
                    and node.module == "pybaseballstats.enums"
                ):
                    for item in node.names:
                        aliases[item.asname or item.name] = getattr(enums, item.name)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(
                    node.func, ast.Attribute
                ):
                    continue
                receiver = node.func.value
                if not isinstance(receiver, ast.Name) or receiver.id not in aliases:
                    continue
                target = getattr(aliases[receiver.id], node.func.attr)
                if inspect.isfunction(target):
                    signature = inspect.signature(target)
                    signature.bind(
                        *([object()] * len(node.args)),
                        **{item.arg: object() for item in node.keywords if item.arg},
                    )
                elif inspect.isclass(target) and target in (
                    enums.BREFTeams,
                    enums.StatcastTeams,
                    enums.StatcastLeaderboardsTeams,
                    enums.UmpireScorecardTeams,
                ):
                    assert node.func.attr == "show_options"
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    enum = aliases.get(node.value.id)
                    if enum in (
                        enums.BREFTeams,
                        enums.StatcastTeams,
                        enums.StatcastLeaderboardsTeams,
                        enums.UmpireScorecardTeams,
                    ):
                        assert hasattr(enum, node.attr), (path, node.attr)
