"""
Command-line interface for Bastet Node
"""

import argparse
import sys
from .node import BastetNode


def main():
    """Main entry point for Bastet Node"""
    parser = argparse.ArgumentParser(
        description="Bastet Node - Security testing tool runner"
    )
    
    parser.add_argument(
        "--config",
        "-c",
        help="Path to configuration file",
        default=None
    )
    
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"Bastet Node v{__version__}")
        sys.exit(0)
    
    try:
        # Create and start node
        node = BastetNode(config_path=args.config)
        node.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
