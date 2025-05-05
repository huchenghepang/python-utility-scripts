import json
import csv

def extract_paths_and_modules(swagger_file, output_file="api_paths_detailed.csv"):
    with open(swagger_file, "r", encoding="utf-8") as f:
        swagger = json.load(f)

    result = []

    paths = swagger.get("paths", {})

    for path, methods in paths.items():
        for method, detail in methods.items():
            tags = detail.get("tags", [])
            module = tags[0] if tags else "unknown"

            # 提取参数（parameters: path + query）
            path_params = []
            query_params = []

            parameters = detail.get("parameters", [])
            for param in parameters:
                param_in = param.get("in")
                param_name = param.get("name")
                if param_in == "path":
                    path_params.append(param_name)
                elif param_in == "query":
                    query_params.append(param_name)

            # 提取 body 参数
            body_params = []
            request_body = detail.get("requestBody")
            if request_body:
                content = request_body.get("content", {})
                json_schema = content.get("application/json", {}).get("schema", {})
                properties = json_schema.get("properties", {})
                body_params = list(properties.keys())

            result.append({
                "method": method.upper(),
                "path": path,
                "module": module,
                "path_params": ", ".join(path_params),
                "query_params": ", ".join(query_params),
                "body_params": ", ".join(body_params)
            })

    # 输出为 CSV 文件
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "method", "path", "module", "path_params", "query_params", "body_params"
        ])
        writer.writeheader()
        writer.writerows(result)

    print(f"✅ 已成功提取 {len(result)} 条 API 信息，保存至: {output_file}")

if __name__ == "__main__":
    extract_paths_and_modules("swagger.json")
