config {
  name = "my_app_invalid"
  owner = {
    name = "admin_user_invalid"
    contact = {
      email = "invalid@example.com"
      phone = true # Invalid type
    }
  }
  threshold = 543.21
  enabled = false
  tags = ["err_tag"]
}
