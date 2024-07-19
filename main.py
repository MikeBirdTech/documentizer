import os
import sys
import argparse
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from code_analyzer import analyze_and_document_directory


def load_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation for Python projects"
    )
    parser.add_argument("directory", help="Directory containing files to document")
    parser.add_argument(
        "--config", default="config.json", help="Path to configuration file"
    )
    parser.add_argument(
        "--internal", action="store_true", help="Generate only internal documentation"
    )
    parser.add_argument(
        "--external", action="store_true", help="Generate only external documentation"
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of files to process"
    )
    args = parser.parse_args()

    if args.config == "config.json":
        config_path = os.path.join(script_dir, args.config)
    else:
        config_path = args.config

    config = load_config(config_path)
    output_dir = os.getcwd()

    config["generate_internal"] = args.internal or not args.external
    config["generate_external"] = args.external or not args.internal
    config["file_limit"] = args.limit

    analyze_and_document_directory(
        args.directory, output_dir, config["ignore_patterns"], config
    )

    print(f"Documentation generation complete. Output directory: {output_dir}")


if __name__ == "__main__":
    main()
