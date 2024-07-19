import os
from ollama import Client


def summarize_code(code: str, detail_level: str, code_type: str, config: dict) -> str:
    client = Client()
    model = os.getenv("OLLAMA_MODEL", "llama3")

    prompt_template = config["prompts"].get(code_type, config["prompts"]["default"])
    prompt = prompt_template.format(detail_level=detail_level, code=code)

    response = client.generate(model=model, prompt=prompt)
    return response["response"]


def summarize_file(file_info: dict, config: dict) -> dict:
    summary = summarize_code(file_info["content"], "high", "file", config)
    file_info["summary"] = summary

    if "functions" in file_info:
        for func in file_info["functions"]:
            func_summary = summarize_code(func["body"], "high", "function", config)
            func["summary"] = func_summary

    if "classes" in file_info:
        for cls in file_info["classes"]:
            cls_summary = summarize_code(cls["body"], "high", "class", config)
            cls["summary"] = cls_summary
            for method in cls["methods"]:
                method_summary = summarize_code(
                    method["body"], "high", "method", config
                )
                method["summary"] = method_summary

    return file_info
