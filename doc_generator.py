import os
import networkx as nx
from typing import Dict, List, Any
from summarizer import summarize_code


def generate_mermaid_diagram(file_info: Dict[str, Any]) -> str:
    graph = nx.DiGraph()

    for func in file_info.get("functions", []):
        graph.add_node(func["name"], type="function")

    for cls in file_info.get("classes", []):
        graph.add_node(cls["name"], type="class")
        for method in cls["methods"]:
            graph.add_node(f"{cls['name']}.{method['name']}", type="method")
            graph.add_edge(cls["name"], f"{cls['name']}.{method['name']}")

    mermaid = "graph TD\n"
    for node, data in graph.nodes(data=True):
        shape = "((*))" if data["type"] == "function" else "[{}]"
        mermaid += f"    {node}{shape}\n"
    for edge in graph.edges():
        mermaid += f"    {edge[0]} --> {edge[1]}\n"

    return mermaid


def generate_external_docs(file_info: Dict[str, Any], config: Dict) -> str:
    markdown = f"# {os.path.basename(file_info['file_path'])}\n\n"

    if config.get("summarize", True):
        markdown += "## Summary\n\n"
        markdown += summarize_code(file_info["content"], "high", "file", config)
        markdown += "\n\n"

    if file_info.get("docstring"):
        markdown += f"{file_info['docstring']}\n\n"

    if file_info.get("functions") or file_info.get("classes"):
        markdown += "## Public Interface\n\n"
        for item in file_info.get("functions", []) + file_info.get("classes", []):
            if not item["name"].startswith("_"):
                markdown += f"- `{item['name']}`\n"
        markdown += "\n"

    return markdown


def generate_internal_docs(file_info: Dict[str, Any], config: Dict) -> str:
    markdown = (
        f"# Internal Documentation: {os.path.basename(file_info['file_path'])}\n\n"
    )

    if config.get("summarize", True):
        markdown += "## Detailed Summary\n\n"
        markdown += summarize_code(file_info["content"], "low", "file", config)
        markdown += "\n\n"

    if file_info.get("functions"):
        markdown += "## Functions\n\n"
        for func in file_info["functions"]:
            markdown += f"### `{func['name']}`\n\n"
            if func["docstring"]:
                markdown += f"{func['docstring']}\n\n"
            markdown += f"Arguments: {', '.join(func['args'])}\n\n"
            markdown += f"Returns: {func['returns']}\n\n"
            markdown += "Function body:\n```python\n"
            markdown += func["body"]
            markdown += "\n```\n\n"

    if file_info.get("classes"):
        markdown += "## Classes\n\n"
        for cls in file_info["classes"]:
            markdown += f"### {cls['name']}\n\n"
            if cls["docstring"]:
                markdown += f"{cls['docstring']}\n\n"
            for method in cls["methods"]:
                markdown += f"#### `{method['name']}`\n\n"
                if method["docstring"]:
                    markdown += f"{method['docstring']}\n\n"
                markdown += f"Arguments: {', '.join(method['args'])}\n\n"
                markdown += "Method body:\n```python\n"
                markdown += method["body"]
                markdown += "\n```\n\n"

    return markdown


def generate_documentation(
    code_info: List[Dict[str, Any]], src_dir: str, output_dir: str, config: Dict
):
    for file_info in code_info:
        try:
            relative_path = os.path.relpath(file_info["file_path"], src_dir)
            doc_dir = os.path.join(output_dir, os.path.dirname(relative_path))
            os.makedirs(doc_dir, exist_ok=True)

            if config["generate_external"]:
                external_doc_path = os.path.join(
                    doc_dir,
                    f"{os.path.splitext(os.path.basename(relative_path))[0]}.md",
                )
                with open(external_doc_path, "w") as f:
                    f.write(generate_external_docs(file_info, config))

            if config["generate_internal"]:
                internal_doc_path = os.path.join(
                    doc_dir,
                    f"{os.path.splitext(os.path.basename(relative_path))[0]}_internal.md",
                )
                with open(internal_doc_path, "w") as f:
                    f.write(generate_internal_docs(file_info, config))

                if file_info.get("functions") or file_info.get("classes"):
                    mermaid_path = os.path.join(
                        doc_dir,
                        f"{os.path.splitext(os.path.basename(relative_path))[0]}_diagram.mmd",
                    )
                    with open(mermaid_path, "w") as f:
                        f.write(generate_mermaid_diagram(file_info))

            print(f"Generated documentation for {file_info['file_path']}")
        except Exception as e:
            print(
                f"Error generating documentation for {file_info['file_path']}: {str(e)}"
            )
