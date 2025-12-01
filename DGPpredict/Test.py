import json
json_text = '{"mean": 30.1, "lower_bound": 27.5, "upper_bound": 32.2}'

print(json_text, type(json_text),"\n")

data = json.loads(json_text)
print(data, type(data))