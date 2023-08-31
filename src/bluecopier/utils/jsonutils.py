JSONObject = bool | int | float | str | list["JSONObject"] | dict[str, "JSONObject"] | None


def merge_json_documents(a: JSONObject, b: JSONObject) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key, b_value in b.items():
            if key in a:
                a_value = a.get(key)
                if isinstance(a_value, dict) and isinstance(b_value, dict):
                    merge_json_documents(a_value, b_value)
                elif isinstance(a_value, list) and isinstance(b_value, list):
                    a_value = a_value + b_value
                a[key] = a_value
            else:
                a[key] = b_value
