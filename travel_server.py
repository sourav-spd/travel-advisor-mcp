"""travel_server.py - Travel Advisor MCP Server with stdio, SSE and Streamable HTTP."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import sys
import traceback
from collections.abc import AsyncIterator, Sequence
from typing import Any, Dict

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from tools.travel_tools import (
    TravelConnectToolHandler,
    SearchDestinationsToolHandler,
    GetDestinationDetailsToolHandler,
    FindAttractionsToolHandler,
    SearchHotelsToolHandler,
    GetTravelTipsToolHandler,
    GetTravelItineraryToolHandler,
)
from tools.toolhandler import ToolHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("travel-advisor-mcp")

app = Server("travel-advisor-mcp")

_tool_handlers: Dict[str, ToolHandler] = {}


def add_tool_handler(handler: ToolHandler) -> None:
    _tool_handlers[handler.name] = handler
    logger.info("Registered tool: %s", handler.name)


def get_tool_handler(name: str) -> ToolHandler | None:
    return _tool_handlers.get(name)


def register_all_tools() -> None:
    # Connection
    add_tool_handler(TravelConnectToolHandler())
    
    # Destination search and information
    add_tool_handler(SearchDestinationsToolHandler())
    add_tool_handler(GetDestinationDetailsToolHandler())
    add_tool_handler(FindAttractionsToolHandler())
    
    # Accommodations
    add_tool_handler(SearchHotelsToolHandler())
    
    # Travel planning
    add_tool_handler(GetTravelTipsToolHandler())
    add_tool_handler(GetTravelItineraryToolHandler())

    logger.info("Total tools registered: %d", len(_tool_handlers))
    logger.info("Tools available: %s", list(_tool_handlers.keys()))


@app.list_tools()
async def list_tools() -> list[Tool]:
    tools = [h.get_tool_description() for h in _tool_handlers.values()]
    logger.info("list_tools -> %d tool(s) returned", len(tools))
    return tools


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    if arguments is None:
        arguments = {}
    elif not isinstance(arguments, dict):
        try:
            arguments = dict(arguments)
        except Exception:
            logger.error("arguments is not dict-like: %s", type(arguments))
            raise RuntimeError("Tool arguments must be a dictionary")

    handler = get_tool_handler(name)
    if not handler:
        logger.error("Unknown tool requested: %s", name)
        raise ValueError(f"Unknown tool: '{name}'")

    logger.info("Executing tool '%s' with keys: %s", name, list(arguments.keys()))
    try:
        result = await handler.run_tool(arguments)
        logger.info("Tool '%s' completed successfully", name)
        return result
    except Exception as exc:
        logger.error("Tool '%s' failed: %s", name, exc, exc_info=True)
        raise


def create_sse_starlette_app() -> Starlette:
    """Create Starlette app for SSE transport."""
    sse = SseServerTransport("/messages/")

    async def _handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    async def _handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    async def _health_endpoint(_request):
        return JSONResponse({"status": "ok"})

    async def _root_endpoint(_request):
        return JSONResponse({"status": "ok", "transport": "sse"})

    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/", _root_endpoint, methods=["GET"]),
            Route("/health", _health_endpoint, methods=["GET"]),
            Route("/sse", _handle_sse, methods=["GET"]),
            Route("/messages/", _handle_messages, methods=["POST"]),
        ],
    )

    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return starlette_app


def create_streamable_http_app() -> Starlette:
    """Create Starlette app for Streamable HTTP transport."""
    mcp_server = app
    session_manager = StreamableHTTPSessionManager(
        server=mcp_server,
        app=mcp_server,
        event_store=None,
        json_response=False,
        stateless=False,
    )

    class _StreamableHTTPRoute:
        async def __call__(self, scope, receive, send) -> None:
            await session_manager.handle_request(scope, receive, send)

    async def _health_endpoint(_request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    async def _root_endpoint(_request) -> JSONResponse:
        return JSONResponse({"status": "ok", "transport": "streamable-http"})

    @contextlib.asynccontextmanager
    async def _lifespan(_starlette_app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            yield

    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/", _root_endpoint, methods=["GET"]),
            Route("/health", _health_endpoint, methods=["GET"]),
            Mount("/mcp", app=_StreamableHTTPRoute()),
        ],
        lifespan=_lifespan,
    )

    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return starlette_app


async def run_server(mode: str = "stdio", host: str = "0.0.0.0", port: int = 8011) -> None:
    """Run the server in the specified mode."""
    logger.info("Travel Advisor MCP Server starting up")
    logger.info("Python %s", sys.version)

    register_all_tools()

    if mode == "stdio":
        logger.info("Starting in stdio mode")
        from mcp.server.stdio import stdio_server

        async with stdio_server() as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    elif mode == "sse":
        logger.info("Starting in SSE mode on http://%s:%d", host, port)
        config = uvicorn.Config(
            create_sse_starlette_app(),
            host=host,
            port=port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    elif mode == "streamable-http":
        logger.info("Starting in Streamable HTTP mode on http://%s:%d", host, port)
        config = uvicorn.Config(
            create_streamable_http_app(),
            host=host,
            port=port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    else:
        logger.error("Unknown mode: %s", mode)
        sys.exit(1)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Travel Advisor MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Server transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8011,
        help="Port to bind to (default: 8011)",
    )
    args = parser.parse_args()

    try:
        await run_server(mode=args.mode, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as exc:
        logger.error("Server crashed: %s", exc, exc_info=True)
        sys.exit(1)


def cli_main() -> None:
    """CLI entry point for the travel-advisor-mcp command."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli_main()
