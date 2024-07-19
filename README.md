# Documentizer

Creates documentation from code.

## Use

Run `pip install -r requirements`

Navigate to the directory where you want the documentation to be generated.

Run `python /path/to/documentizer/main.py /path/to/codebase`

Can run on a subdirectory of a project to only document those files.

## Configuration

Update prompts, ignored files, and summariation in `config.json`.

## Flags

`--internal` - Generates docs that are intended for internal use. Higher fidelity and explans functions.

`--external` - Generates docs that are intended for external use. Lower fidelity and explains how to interact with the software.

`--limit` - Limits the number of files to be processed.
