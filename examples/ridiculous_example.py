from pyvider.hcl import parse_hcl_to_cty, pretty_print_cty

hcl_string = """
  # This is a ridiculously complicated HCL file.

  provider "aws" {
    region = "us-west-2"
  }

  variable "my_map" {
    type = map(object({
      name = string
      age  = number
    }))
    default = {
      "jules" = {
        name = "Jules"
        age  = 30
      }
      "vincent" = {
        name = "Vincent"
        age  = 40
      }
    }
  }

  resource "aws_instance" "my_instance" {
    ami           = "ami-0c55b159cbfafe1f0"
    instance_type = "t2.micro"
    count         = 2

    tags = {
      Name = "HelloWorld"
    }

    dynamic "ebs_block_device" {
      for_each = var.my_map
      content {
        device_name = "/dev/sdh"
        volume_size = ebs_block_device.value.age
        volume_type = "gp2"
      }
    }
  }

  output "my_output" {
    value = {
      "instance_ids" = aws_instance.my_instance.*.id
      "instance_ages" = [
        for instance in aws_instance.my_instance : instance.ebs_block_device.0.volume_size
      ]
      "jules_age" = var.my_map["jules"].age
      "is_vincent_old" = var.my_map["vincent"].age > 35
      "nested_list" = [
        [1, 2, 3],
        [4, 5, 6],
      ]
      "nested_map" = {
        "a" = {
          "b" = {
            "c" = "d"
          }
        }
      }
    }
  }
"""

cty_value = parse_hcl_to_cty(hcl_string)

pretty_print_cty(cty_value)
