"""Guard the Router -> Service -> Repository dependency boundaries."""

import ast
from pathlib import Path

from services.exceptions import (
    AuthenticationError,
    ConflictError,
    PermissionDeniedError,
    RepositoryError,
    ResourceNotFoundError,
    ValidationError,
)

def _python_files(directory: str) -> list[Path]:
    return [
        path
        for path in Path(directory).glob("*.py")
        if "__pycache__" not in path.parts
    ]


def test_services_and_repositories_do_not_import_fastapi() -> None:
    """Framework dependencies belong to the HTTP router layer only."""
    for path in _python_files("services") + _python_files("db"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imported.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert not any(name.startswith("fastapi") for name in imported), path


def test_routers_do_not_execute_database_operations_directly() -> None:
    """Routers may pass sessions down but must not query or mutate them."""
    forbidden = {"query", "execute", "add", "commit", "rollback", "delete"}
    for path in _python_files("router"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "db"
            )
        }
        assert calls.isdisjoint(forbidden), (path, calls & forbidden)


def test_all_service_errors_have_a_human_readable_message() -> None:
    """Every service exception must expose a non-empty public description."""
    error_types = (
        ValidationError,
        AuthenticationError,
        PermissionDeniedError,
        ResourceNotFoundError,
        ConflictError,
        RepositoryError,
    )
    for error_type in error_types:
        error = error_type()
        assert isinstance(error.detail, dict)
        assert isinstance(error.detail.get("message"), str)
        assert error.detail["message"].strip()
