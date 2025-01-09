import re
import shutil

from jinja2 import Template
import os
def parse_typescript_interface(ts_content):
    """
    解析 TypeScript 接口内容为表字段结构。
    :param ts_content: TypeScript 接口定义内容
    :return: 解析后的字段字典
    """
    interfaces = {}
    current_interface = None

    for line in ts_content.splitlines():
        line = line.strip()
        # 匹配接口声明
        interface_match = re.match(r"export interface (\w+)", line)
        # // 源表名称: Permissions 匹配源表名
        table_name_match = re.match(r"// 源表名称: (\w+)", line)
        if interface_match:
            current_interface = interface_match.group(1)
            interfaces[current_interface] = {"table_name":"","fields":[]}
            continue

        if table_name_match:
            table_name = table_name_match.group(1).strip()
            interfaces[current_interface]["table_name"] = table_name
            continue

        # 匹配字段声明
        if current_interface and ":" in line:
            field_match = re.match(r"(\w+): ([\w<>|'\s]+);", line)
            if field_match:
                field_name, field_type = field_match.groups()
                field_info = {
                    "name": field_name,
                    "type": field_type
                }
                interfaces[current_interface]["fields"].append(field_info)

    return interfaces


# 读取文件内容的函数
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()



crud_template = Template("""
import pool from "../db/mysqlpool.js";
// import pool from "../mysql";
// const pool = require("../db/mysqlpool");
// {{table_name}} 数据表的 CRUD 操作

export const create{{class_name}} = async (data) => {
    const sql = "INSERT INTO {{table_name}} ({{fields}}) VALUES ({{placeholders}})";
    const params = [{{params}}];
    return pool.query(sql, params);
};

export const get{{class_name}}ById = async (id) => {
    const sql = "SELECT * FROM {{table_name}} WHERE {{id_field}} = ?";
    return pool.query(sql, [id]);
};

export const update{{class_name}}ById = async (id, data) => {
    const sql = "UPDATE {{table_name}} SET {{update_fields}} WHERE {{id_field}} = ?";
    const params = [...Object.values(data), id];
    return pool.query(sql, params);
};

export const delete{{class_name}}ById = async (id) => {
    const sql = "DELETE FROM {{table_name}} WHERE {{id_field}} = ?";
    return pool.query(sql, [id]);
};
""")


typescript_template = Template("""
import pool from "../db/mysqlpool.js";
import  {{NameSpace}}  from "../types/{{module_name}}"; // 引入类型定义

// {{NameSpace}} 模块的 {{table_name}} 数据表 CRUD 操作

export const create{{class_name}} = async (data: {{NameSpace}}.{{class_name}}): Promise<any> => {
    const sql = "INSERT INTO {{table_name}} ({{fields}}) VALUES ({{placeholders}})";
    const params = [{{params}}];
    return pool.query(sql, params);
};

export const get{{class_name}}ById = async (id: number): Promise<{{NameSpace}}.{{class_name}} | null> => {
    const sql = "SELECT * FROM {{table_name}} WHERE {{id_field}} = ?";
    const [rows] = await pool.query(sql, [id]);
    return rows.length > 0 ? (rows[0] as {{NameSpace}}.{{class_name}}) : null;
};

export const update{{class_name}}ById = async (id: number, data: Partial<{{NameSpace}}.{{class_name}}>): Promise<any> => {
    const sql = "UPDATE {{table_name}} SET {{update_fields}} WHERE {{id_field}} = ?";
    const params = [...Object.values(data), id];
    return pool.query(sql, params);
};

export const delete{{class_name}}ById = async (id: number): Promise<any> => {
    const sql = "DELETE FROM {{table_name}} WHERE {{id_field}} = ?";
    return pool.query(sql, [id]);
};
""")



def generate_crud_code(interface_name, fields, table_name, isTypescriptGenerate=True, module_name="mysql", NameSpace="DataBase"):
    """
    根据接口生成 CRUD 代码。
    :param interface_name: 接口名（表名）
    :param fields: 字段信息列表
    :return: CRUD 代码字符串
    """


    table_name = table_name
    class_name = interface_name
    id_field = "id"  # 假设主键为 id，可根据字段动态判断
    fields_list = ", ".join(f"`{field['name']}`" for field in fields)
    placeholders = ", ".join(["?"] * len(fields))
    params = ", ".join(f"data.{field['name']}" for field in fields)
    update_fields = ", ".join(f"`{field['name']}` = ?" for field in fields)

    if isTypescriptGenerate:
        return typescript_template.render(
            table_name=table_name,
            class_name=class_name,
            fields=fields_list,
            placeholders=placeholders,
            params=params,
            id_field=id_field,
            update_fields=update_fields,
            module_name=module_name, NameSpace=NameSpace
        )
    else:
        return crud_template.render(
            table_name=table_name,
            class_name=class_name,
            fields=fields_list,
            placeholders=placeholders,
            params=params,
            id_field=id_field,
            update_fields=update_fields,
        )


# 确保文件夹存在，如果不存在则创建
def ensure_directory_exists(directory_path, clear_old_files=False):
    """确保文件夹存在，如果不存在则创建，并可选择清空文件夹"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    elif clear_old_files:
        # 如果文件夹已存在且用户选择清空，则删除文件夹中的所有文件
        print(f"Warning: The directory '{directory_path}' already exists. Deleting all existing files.")
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除文件夹及其内容


def get_user_confirmation():
    """获取用户是否确认删除文件夹中的所有文件"""
    while True:
        user_input = input("Do you want to delete all files in the target directory? (y/n): ").strip().lower()
        if user_input in ['y', 'n']:
            return user_input == 'y'
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    # 目标文件夹
    output_folder = "generated_crud"  # 指定生成的文件夹路径

    # 提示用户是否删除旧文件
    clear_old_files = get_user_confirmation()

    # 确保文件夹存在，并在需要时清空旧文件
    ensure_directory_exists(output_folder, clear_old_files)

    # 读取 TypeScript 接口
    typescript_content = read_file_content('interfaces.d.ts')
    interfaces = parse_typescript_interface(typescript_content)

    # 是否是生成ts
    isTypescriptGenerate = True

    # 询问是否生成ts
    while True:
        user_input = input("Do you want to generate ts code? (y/n): ").strip().lower()
        if user_input in ['y', 'n']:
            isTypescriptGenerate = user_input == 'y'
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    # 为每个接口生成 CRUD 代码
    for interface_name, tableinfo in interfaces.items():
        crud_code = generate_crud_code(interface_name, tableinfo["fields"],tableinfo["table_name"],isTypescriptGenerate)

        # 确保文件夹存在
        ensure_directory_exists(output_folder)
        # 如果要生成ts
        if isTypescriptGenerate:
            output_file = os.path.join(output_folder, f"{interface_name.lower()}_crud.ts")
        else:
            output_file = os.path.join(output_folder, f"{interface_name.lower()}_crud.js")

        # 写入文件
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(crud_code)

        print(f"Generated CRUD code for {interface_name} in {output_file}")