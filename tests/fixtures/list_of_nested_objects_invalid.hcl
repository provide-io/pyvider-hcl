item_group {
  items = [
    {
      id = "item1_valid"
      value = 100
      spec = {
        feature_a = "enabled"
        feature_b = true
      }
    },
    {
      id = "item2_invalid"
      value = 200
      spec = {
        feature_a = "disabled"
        feature_b = "not_a_bool" # Invalid type
      }
    }
  ]
  group_name = "my_invalid_items"
}
