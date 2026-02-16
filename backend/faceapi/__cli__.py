"""Command Line Interface for Face Recognition System API.

This module provides the main entry points for running the server
through command line arguments.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import uvicorn
from loguru import logger
import textwrap
from pathlib import Path



def generate_env_file(output_path: str = ".env") -> None:
    """
    設定項目を含む.envファイルを生成します。

    Args:
        output_path (str): 出力ファイルのパス。デフォルトは".env"
    """
    
    from faceapi.core import Config, CONFIGURABLE_FIELDS

    env_lines = [
        "# Face Recognition System Environment Configuration",
        "# Generated automatically - feel free to modify",
        "",
    ]

    for field_name in CONFIGURABLE_FIELDS:
        field_info = Config.model_fields[field_name]
        description = field_info.description or ""
        default_value = getattr(Config(), field_name)

        # コメントとして説明を追加
        if description:
            wrapped_desc = textwrap.fill(description, width=70)
            for line in wrapped_desc.split("\n"):
                env_lines.append(f"# {line}")

        # デフォルト値のフォーマット
        if isinstance(default_value, str) and default_value:
            formatted_value = f'{field_name}="{default_value}"'
        elif isinstance(default_value, list):
            formatted_value = f'{field_name}={",".join(map(str, default_value))}'
        else:
            formatted_value = f"{field_name}={default_value}"

        env_lines.append(formatted_value)
        env_lines.append("")

    # ファイルに書き込み
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines))

    print(f"Environment file generated successfully: {output_file.absolute()}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Face Recognition System API Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--host", default="0.0.0.0", help=f"Host to bind to")

    parser.add_argument("--port", type=int, default=8000, help=f"Port to bind to")

    parser.add_argument(
        "--reload",
        "--debug",
        action="store_true",
        help="Enable auto-reload for development",
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

    parser.add_argument(
        "--gen-env", type=str, default="", help="Generate .env file"
    )

    return parser


def main(args: Optional[list] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.gen_env:
        generate_env_file(output_path=parsed_args.gen_env)
        logger.info(f"Generated .env file at {parsed_args.gen_env}")
        return

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
    main(["--reload"])


def prod() -> None:
    """Production server entry point with multiple workers."""
    main()


if __name__ == "__main__":
    main()
