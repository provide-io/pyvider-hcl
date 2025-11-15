# GEMINI.md: Your AI Assistant for the `pyvider-hcl` Project

This document provides context and instructions for interacting with the `pyvider-hcl` project. It is intended to be used by the Gemini AI assistant to help you with your development tasks.

## Project Overview

`pyvider-hcl` is a Python library for parsing HCL (HashiCorp Configuration Language) into `pyvider.cty` types. It acts as a wrapper around the `python-hcl2` library, providing seamless integration with the `pyvider` ecosystem. The library simplifies working with HCL data by offering a streamlined API, automatic type inference, and validation against `CtyType` schemas.

## Core Components

The `pyvider-hcl` project consists of the following core components:

*   **`parser.py`**: This module contains the primary functions for parsing HCL strings and files. `parse_hcl_to_cty` is the main entry point, which can validate against a provided `CtyType` schema or automatically infer the types.
*   **`factories.py`**: This module provides factory functions for creating complex `CtyValue` objects, such as Terraform variables and resources, from Python data.
*   **`exceptions.py`**: This module defines custom exception types for handling parsing and factory errors.

## Building and Running

The `pyvider-hcl` project is built and tested using a combination of `setuptools`, `pytest`, `ruff`, and `mypy`. The `wrkenv.toml` file defines a number of useful environments for managing the project.

*   **Build**: `pyvider-hcl` is built using `setuptools`. You can build the project by running `python -m build`.
*   **Test**: The tests are in the `tests` directory and can be run with `pytest`. You can also use the `test` profile in `wrkenv.toml` by running `wrkenv test`.
*   **Lint**: The code is linted with `ruff check`. You can also use the `lint` profile in `wrkenv.toml` by running `wrkenv lint`.
*   **Format**: The code is formatted with `ruff format`.
*   **Type Check**: Type checking is done with `mypy`. You can also use the `typecheck` profile in `wrkenv.toml` by running `wrkenv typecheck`.

## Development Conventions

The `pyvider-hcl` project uses the following development conventions:

*   **Coding Style**: The code is formatted with `ruff format` and linted with `ruff check`.
*   **Testing**: The project is tested with `pytest`.
*   **Type Checking**: Type checking is done with `mypy`.
*   **Dependencies**: Dependencies are managed with `uv` and specified in the `pyproject.toml` file.
*   **Virtual Environments**: The project is developed in virtual environments, which can be managed with `wrkenv`.
