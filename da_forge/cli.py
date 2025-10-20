"""
Command-line interface for DA-Forge.
"""

import argparse
import sys

from da_forge import __version__
from da_forge.core import deploy_agent, list_agents


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="da-forge",
        description="Forge Declarative Agents with Microsoft 365 grounding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  da-forge deploy my-agent
  da-forge deploy my-agent --description "Email assistant" --instruction "Help with emails"
  da-forge deploy my-agent --skip-sideload
  da-forge list

Workflow:
  1. Create socket file: sockets/<name>.json (see examples/)
  2. Run: da-forge deploy <name>
  3. Agent is deployed to Teams!

For more information: https://github.com/yourusername/da-forge
        """,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Deploy command
    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Deploy a Declarative Agent",
        description="Deploy a DA from socket file to Teams",
    )
    deploy_parser.add_argument(
        "name", type=str, help="Name of the DA (matches socket file without .json)"
    )
    deploy_parser.add_argument(
        "--description", type=str, default="-", help='Description for the DA (default: "-")'
    )
    deploy_parser.add_argument(
        "--instruction", type=str, default="-", help='Instructions for the DA (default: "-")'
    )
    deploy_parser.add_argument(
        "--skip-sideload",
        action="store_true",
        help="Skip sideloading to Teams (just create package)",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list", help="List available agents", description="List all socket files in sockets/ folder"
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "deploy":
        success = deploy_agent(
            name=args.name,
            description=args.description,
            instruction=args.instruction,
            skip_sideload=args.skip_sideload,
        )
        sys.exit(0 if success else 1)

    elif args.command == "list":
        list_agents()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
