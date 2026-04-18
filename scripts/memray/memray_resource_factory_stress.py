#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Memray stress test for resource and variable factory hot paths."""

import os

os.environ["PLUGIN_LOG_LEVEL"] = "ERROR"

from pyvider.hcl.factories.resources import create_resource_cty
from pyvider.hcl.factories.variables import create_variable_cty

RESOURCE_CONFIGS = [
    {
        "r_type": "aws_instance",
        "r_name": "web",
        "attributes_py": {"ami": "ami-12345678", "instance_type": "t2.micro"},
        "attributes_schema_py": {"ami": "string", "instance_type": "string"},
    },
    {
        "r_type": "aws_s3_bucket",
        "r_name": "data",
        "attributes_py": {"bucket": "my-bucket", "acl": "private"},
        "attributes_schema_py": {"bucket": "string", "acl": "string"},
    },
    {
        "r_type": "aws_security_group",
        "r_name": "allow_ssh",
        "attributes_py": {"name": "allow_ssh", "description": "Allow SSH inbound"},
        "attributes_schema_py": {"name": "string", "description": "string"},
    },
    {
        "r_type": "aws_db_instance",
        "r_name": "primary",
        "attributes_py": {"engine": "postgres", "instance_class": "db.t3.micro", "allocated_storage": 20},
        "attributes_schema_py": {
            "engine": "string",
            "instance_class": "string",
            "allocated_storage": "number",
        },
    },
]

VARIABLE_CONFIGS = [
    {"name": "region", "type_str": "string", "default_py": "us-west-2", "description": "AWS region"},
    {"name": "instance_count", "type_str": "number", "default_py": 3, "description": "Number of instances"},
    {"name": "enable_logging", "type_str": "bool", "default_py": True, "description": "Enable logging"},
    {"name": "tags", "type_str": "map(string)", "default_py": {"env": "prod", "team": "platform"}},
    {"name": "allowed_cidrs", "type_str": "list(string)", "default_py": ["10.0.0.0/8", "172.16.0.0/12"]},
]


def main() -> None:
    # 5K resource creation calls
    for i in range(5_000):
        cfg = RESOURCE_CONFIGS[i % len(RESOURCE_CONFIGS)]
        create_resource_cty(
            r_type=cfg["r_type"],
            r_name=cfg["r_name"],
            attributes_py=cfg["attributes_py"],
            attributes_schema_py=cfg["attributes_schema_py"],
        )

    # 5K variable creation calls
    for i in range(5_000):
        cfg = VARIABLE_CONFIGS[i % len(VARIABLE_CONFIGS)]
        create_variable_cty(
            name=cfg["name"],
            type_str=cfg["type_str"],
            default_py=cfg.get("default_py"),
            description=cfg.get("description"),
        )

    print("resource_factory stress complete: 10K calls")


if __name__ == "__main__":
    main()
