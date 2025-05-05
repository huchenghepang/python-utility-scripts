import json
from pathlib import Path
from typing import Dict, Any
import os
# 映射 JSON Schema 类型到 TypeScript 类型
type_map = {
    "string": "string",
    "number": "number",
    "integer": "number",
    "boolean": "boolean",
    "array": "Array",
    "object": "Record<string, any>",
}


def generate_jsdoc(prop: Dict[str, Any], indent: str = "  ") -> str:
    """
    根据 JSON Schema 属性生成 JSDoc 注释，并添加缩进对齐格式。

    Args:
        prop (Dict[str, Any]): JSON Schema 属性定义。
        indent (str): 每一行前添加的缩进字符，默认为两个空格。

    Returns:
        str: 缩进后的 JSDoc 注释字符串。
    """
    lines = []
    description = prop.get("description")
    example = prop.get("example")

    if description or example:
        lines.append(f"{indent}/**")
        if description:
            lines.append(f"{indent} * {description}")
        if example is not None:
            lines.append(f"{indent} * 示例: {json.dumps(example, ensure_ascii=False)}")
        lines.append(f"{indent} */")
    return "\n".join(lines)




def parse_property(name: str, prop: Dict[str, Any], required_fields: list) -> str:
    ts_type = "any"

    # 🧠 枚举类型优先处理
    if "enum" in prop:
        enum_values = prop["enum"]
        # 用 TypeScript 联合类型表示 enum
        ts_type = " | ".join(json.dumps(v, ensure_ascii=False) for v in enum_values)

    elif "$ref" in prop:
        ref_name = prop["$ref"].split("/")[-1]
        ts_type = ref_name

    elif prop.get("type") == "array":
        items = prop.get("items", {})
        if "$ref" in items:
            ref_name = items["$ref"].split("/")[-1]
            ts_type = f"{ref_name}[]"
        else:
            item_type = type_map.get(items.get("type", "any"), "any")
            ts_type = f"{item_type}[]"

    elif prop.get("type") == "object":
        additional_props = prop.get("additionalProperties")
        if additional_props:
            if (
                additional_props.get("type") == "array"
                and additional_props.get("items", {}).get("type") == "string"
            ):
                ts_type = "string[]"
            else:
                val_type = type_map.get(additional_props.get("type", "any"), "any")
                ts_type = f"{{ [key: string]: {val_type} }}"
        else:
            ts_type = "Record<string, any>"

    else:
        ts_type = type_map.get(prop.get("type", "any"), "any")

    is_required = name in required_fields
    jsdoc = generate_jsdoc(prop,indent="  ")
    return f"{jsdoc}\n  {name}{'' if is_required else '?'}: {ts_type};"



def convert_schema_to_ts(name: str, schema: Dict[str, Any]) -> str:
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    lines = [f"export interface {name} {{"]

    for prop_name, prop in properties.items():
        lines.append(parse_property(prop_name, prop, required))

    lines.append("}\n")
    return "\n".join(lines)


def create_or_append_export(output_file: str):
    """
    在同目录下的 index.d.ts 中追加 export * from "./xxx"，避免重复添加。
    """
    dir_path = os.path.dirname(os.path.abspath(output_file))
    print(f"📁 目录路径: {dir_path}")
    index_path = os.path.join(dir_path, "index.d.ts")

    # 生成相对路径，例如 output.d.ts => ./output
    base_name = os.path.splitext(os.path.basename(output_file))[0]
    export_line = f'export type * from "./{base_name}";'

    # 如果 index.d.ts 不存在，创建它
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(export_line + "\n")
        print(f"✅ 创建 index.d.ts 并添加导出语句: {export_line}")
    else:
        # 检查是否已包含该导出
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        if export_line not in content:
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(export_line + "\n")
            print(f"✅ 路径 {output_file}")    
            print(f"✅ 向 index.d.ts 添加导出语句: {export_line}")
        else:
            print(f"☑️ 已存在导出语句，无需重复添加: {export_line}")

def generate_typescript_from_swagger(swagger_file: str, output_file: str):
    with open(swagger_file, "r", encoding="utf-8") as f:
        swagger = json.load(f)

    schemas = swagger.get("components", {}).get("schemas", {})
    output = []

    for name, schema in schemas.items():
        output.append(convert_schema_to_ts(name, schema))

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"✅ TypeScript 类型定义已生成: {output_file}")
    # 添加 index.d.ts 中的 export 语句
    create_or_append_export(output_file)


# 示例执行
if __name__ == "__main__":
    generate_typescript_from_swagger("swagger.json", "src/types/api/output.d.ts")
