"""Command Line Interface for Face Recognition System API.

This module provides the main entry points for running the server
through command line arguments.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from faceapi.core import _CONFIG_


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Face Recognition System API Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--host", default=_CONFIG_.LISTEN_HOST, help=f"Host to bind to")

    parser.add_argument(
        "--port", type=int, default=_CONFIG_.LISTEN_PORT, help=f"Port to bind to"
    )

    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    parser.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes"
    )

    parser.add_argument(
        "--log-level",
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Log level",
    )

    parser.add_argument("--env-file", type=str, help="Path to .env file")

    return parser


def main(args: Optional[list] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Configure uvicorn settings
    uvicorn_config = {
        "app": "faceapi.main:app",
        "host": parsed_args.host,
        "port": parsed_args.port,
        "reload": parsed_args.reload,
        "workers": parsed_args.workers,
        "log_level": parsed_args.log_level,
    }

    # Add env_file if specified
    if parsed_args.env_file:
        uvicorn_config["env_file"] = parsed_args.env_file

    # Run the server
    uvicorn.run(**uvicorn_config)


def dev() -> None:
    """Development server entry point with auto-reload enabled."""
    uvicorn.run(
        "faceapi.main:app",
        host=_CONFIG_.LISTEN_HOST,
        port=_CONFIG_.LISTEN_PORT,
        reload=True,
        log_level="debug",
    )


def prod() -> None:
    """Production server entry point with multiple workers."""
    uvicorn.run(
        "faceapi.main:app",
        host=_CONFIG_.LISTEN_HOST,
        port=_CONFIG_.LISTEN_PORT,
        workers=4,
        log_level="info",
    )


if __name__ == "__main__":
    main()
