service "my_app_from_file" {
  image    = "nginx:latest"
  ports    = ["80:80", "443:443"]
  replicas = 3
}
resource "local_file" "foo" {
  content  = "foo!"
  filename = "/tmp/foo.bar"
}
