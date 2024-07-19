import os
import ast
from typing import Dict, List, Any, Tuple
from tqdm import tqdm
import fnmatch
from summarizer import summarize_file
from doc_generator import generate_documentation


def should_ignore(file_path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False


def parse_file(file_path: str) -> Tuple[ast.Module, str]:
    with open(file_path, "r") as file:
        content = file.read()
    tree = ast.parse(content)
    return tree, content


def extract_docstring(node: ast.AST) -> str:
    return ast.get_docstring(node) or ""


def extract_function_info(node: ast.FunctionDef) -> Dict[str, Any]:
    return {
        "name": node.name,
        "args": [arg.arg for arg in node.args.args],
        "docstring": extract_docstring(node),
        "returns": (
            node.returns.id if hasattr(node, "returns") and node.returns else None
        ),
        "body": ast.unparse(node),
    }


def extract_class_info(node: ast.ClassDef) -> Dict[str, Any]:
    methods = [
        extract_function_info(n) for n in node.body if isinstance(n, ast.FunctionDef)
    ]
    return {
        "name": node.name,
        "docstring": extract_docstring(node),
        "methods": methods,
        "body": ast.unparse(node),
    }


def analyze_file(file_path: str) -> Dict[str, Any]:
    _, ext = os.path.splitext(file_path)
    if ext == ".py":
        tree, content = parse_file(file_path)
        functions = [
            extract_function_info(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        classes = [
            extract_class_info(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        return {
            "file_path": file_path,
            "docstring": extract_docstring(tree),
            "functions": functions,
            "classes": classes,
            "content": content,
        }
    else:
        with open(file_path, "r") as file:
            content = file.read()
        return {"file_path": file_path, "content": content}


def analyze_and_document_directory(
    directory: str, output_dir: str, ignore_patterns: List[str], config: dict
) -> None:
    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not should_ignore(file_path, ignore_patterns):
                all_files.append(file_path)

    file_limit = config.get("file_limit")
    if file_limit:
        all_files = all_files[:file_limit]

    for file_path in tqdm(all_files, desc="Analyzing and documenting files"):
        try:
            file_info = analyze_file(file_path)
            summarized_info = summarize_file(file_info, config)
            generate_documentation([summarized_info], directory, output_dir, config)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
