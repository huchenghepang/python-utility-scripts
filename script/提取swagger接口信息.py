import json
import csv

def extract_paths_and_modules(swagger_file, output_file="api_paths.csv"):
    with open(swagger_file, "r", encoding="utf-8") as f:
        swagger = json.load(f)

    result = []

    paths = swagger.get("paths", {})

    for path, methods in paths.items():
        for method, detail in methods.items():
            tags = detail.get("tags", [])
            module = tags[0] if tags else "unknown"
            result.append({
                "method": method.upper(),  # 提取方法并转为大写（如 GET、POST）
                "path": path,
                "module": module
            })

    # 输出为 CSV 文件
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "path", "module"])
        writer.writeheader()
        writer.writerows(result)

    print(f"✅ 已成功提取 {len(result)} 条 API 路径，保存至: {output_file}")

if __name__ == "__main__":
    extract_paths_and_modules("swagger.json")
