#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generate the API reference pages for mkdocs.

This script is executed automatically by the gen-files plugin during the
mkdocs build process. It walks through all Python files in the source
directory and creates corresponding markdown documentation pages.
"""

from pathlib import Path
import mkdocs_gen_files

# Initialize navigation builder
nav = mkdocs_gen_files.Nav()

# Source code root
src_root = Path("src")

# Walk through all Python files
for path in sorted(src_root.rglob("*.py")):
    # Skip __pycache__ directories
    if "__pycache__" in str(path):
        continue

    # Convert source file path to module path
    module_path = path.relative_to(src_root).with_suffix("")
    doc_path = Path("reference") / module_path.with_suffix(".md")
    full_doc_path = doc_path

    # Extract module path parts for navigation
    parts = tuple(module_path.parts)

    # Skip private modules (starting with _), except __init__
    if any(part.startswith("_") and part != "__init__" for part in parts):
        continue

    # Handle __init__.py files → index.md
    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    # Skip if no parts left
    if not parts:
        continue

    # Add to navigation (strip "reference/" prefix)
    nav_path = str(doc_path)
    if nav_path.startswith("reference/"):
        nav_path = nav_path[10:]
    nav[parts] = nav_path

    # Create the markdown file with mkdocstrings directive
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print(f"::: {identifier}", file=fd)

    # Set edit path to original source file
    mkdocs_gen_files.set_edit_path(full_doc_path, path)

# Generate SUMMARY.md for literate-nav
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
