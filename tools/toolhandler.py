"""Abstract base class for travel advisor tool handlers."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool


class ToolHandler(ABC):
    """Abstract base class for all travel advisor tool handlers."""

    def __init__(self, tool_name: str) -> None:
        """Initialize the tool handler.
        
        Args:
            tool_name: The name of the tool.
        """
        self.name = tool_name

    @abstractmethod
    def get_tool_description(self) -> Tool:
        """Return the MCP Tool description for this handler.
        
        Returns:
            Tool object with name, description, and input schema.
        """
        pass

    @abstractmethod
    async def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Execute the tool with the given arguments.
        
        Args:
            args: Dictionary of arguments for the tool.
            
        Returns:
            Sequence of content items (text, image, or embedded resource).
        """
        pass

    def validate_required_args(self, args: dict, required: list[str]) -> None:
        """Validate that all required arguments are present.
        
        Args:
            args: Dictionary of arguments to validate.
            required: List of required argument names.
            
        Raises:
            ValueError: If any required argument is missing.
        """
        missing = [arg for arg in required if arg not in args]
        if missing:
            raise ValueError(
                f"Missing required arguments for {self.name}: {', '.join(missing)}"
            )
