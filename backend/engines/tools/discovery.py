"""Tool discovery utilities."""

import importlib
import inspect
import pkgutil
from typing import Type

from engines.tools.base import BaseTool
from shared.logger import get_logger

logger = get_logger("tools.discovery")


class ToolDiscovery:
    """Discovers tool classes in a package."""

    @staticmethod
    def discover_tools(package_name: str) -> list[Type[BaseTool]]:
        """Discover all BaseTool subclasses in a package."""
        discovered: list[Type[BaseTool]] = []

        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.warning("Package not found for discovery: %s", package_name)
            return discovered

        if not hasattr(package, "__path__"):
            return discovered

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{module_name}")
            except ImportError:
                continue

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, BaseTool)
                    and obj is not BaseTool
                    and obj.__module__ == module.__name__
                ):
                    discovered.append(obj)
                    logger.info("Discovered tool: %s", obj.name)

        return discovered
