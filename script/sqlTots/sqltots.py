import os
import re

def parse_sql_to_ts(sql_file, output_file, out_folder):
    # 提取文件名并确保后缀为 .d.ts
    file_name = os.path.basename(output_file)
    if not file_name.endswith('.d.ts'):
        output_file = os.path.splitext(file_name)[0] + '.d.ts'

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 匹配 CREATE TABLE 的表结构和字段
    table_pattern = r'CREATE TABLE `(\w+)`\s+\((.*?)\)\s+ENGINE'
    field_pattern = r'^\s*`(\w+)`\s+(\w+.*?)(?:\((.*?)\))?(.*?COMMENT\s+\'(.*?)\')?,?'

    # 匹配主键的结构
    primary_key_pattern = r"PRIMARY KEY\s*\(\s*(.*?)\s*\)"

    # 匹配到AUTO_INCREMENT 的正则表达式
    AUTO_INCREMENT_PATTERN = r'\bAUTO_INCREMENT\b'
    # 匹配 DEFAULT 的正则表达式
    DEFAULT_PATTERN = r'\bDEFAULT\b'

    # 匹配 NOT NULL AUTO_INCREMENT DEFAULT 的正则表达式
    NOT_NULL_PATTERN = r'\bNOT NULL\b(?!.*\b(AUTO_INCREMENT|DEFAULT)\b)'


    # 记录所有的表名
    table_names = []
    matches = re.findall(table_pattern, sql_content, re.S)
    ts_interfaces = []
    ts_mysql2_interfaces = ['import { RowDataPacket } from "mysql2";']

    for table_name, fields in matches:
        # 转换表名为大驼峰命名
        ts_table_name = to_camel_case(table_name, capitalize=True)

        # 匹配主键
        primary_key_match = re.search(primary_key_pattern, fields)
        primary_key_field = primary_key_match.group(1) if primary_key_match else '无'

        # 记录表名
        table_names.append(table_name)

        ts_interface = f"export interface {ts_table_name} {{\n  // 源表名称: {table_name} - 主键: {primary_key_field}\n"
        ts_mysql2_interface = f"export interface {ts_table_name} extends RowDataPacket {{\n  // 源表名称: {table_name} - 主键: {primary_key_field}\n"

        for line in fields.splitlines():
            line = line.strip()
            if line.startswith(('PRIMARY KEY', 'INDEX', 'CONSTRAINT')):
                continue

            # 检查是都包含自增长字段
            is_auto_increment = bool(re.search(AUTO_INCREMENT_PATTERN, line, re.IGNORECASE))
            # 检查是否包含默认字段
            is_default = bool(re.search(DEFAULT_PATTERN, line, re.IGNORECASE))

            is_required = bool(re.search(NOT_NULL_PATTERN, line, re.IGNORECASE))
            field_match = re.match(field_pattern, line)
            if field_match:
                field_name, field_type, enum_values, _, comment = field_match.groups()
                ts_type = parse_enum_type(enum_values) if 'enum' in field_type.lower() and enum_values else map_sql_type_to_ts_type(field_type)
                field_name += '' if is_required else '?'
                # 自增长描述注释
                auto_increment_str = '- 自增长' if is_auto_increment else ''
                # 默认描述注释
                default_str = '- 默认' if is_default else ''
                # 默认描述注释
                comment_text = f"{comment.strip()}" if comment else "无描述"
                ts_comment = f"/** {comment_text} {'必填' if is_required else '可选'} {auto_increment_str} {default_str} */"
                ts_interface += f"  {ts_comment}\n  {field_name}: {ts_type};\n"
                ts_mysql2_interface += f"  {ts_comment}\n  {field_name}: {ts_type};\n"

        ts_interface += "}\n"
        ts_mysql2_interface += "}\n"

        ts_interfaces.append(ts_interface)
        ts_mysql2_interfaces.append(ts_mysql2_interface)

    tables_str = format_tables_str(table_names)

    ts_interfaces.insert(0, tables_str)
    ts_mysql2_interfaces.insert(1, tables_str)

    # 确保输出目录存在
    create_file_folder(out_folder)

    # 写入主接口文件
    output_path = os.path.join(out_folder, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(ts_interfaces))

    # 写入 MySQL2 接口文件
    ts_mysql2_file = output_file.replace('.d.ts', '_mysql2.d.ts')
    mysql2_output_path = os.path.join(out_folder, ts_mysql2_file)
    with open(mysql2_output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(ts_mysql2_interfaces))

    print(f"TypeScript interfaces have been written to {output_path}")
    print(f"MySQL2 interfaces have been written to {mysql2_output_path}")


def create_file_folder(folder_path):
    # 创建文件夹（如果不存在）
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")

def format_tables_str(table_names, max_line_length=80):
    formatted_lines = []
    current_line = "export type Tables = "
    for table in table_names:
        table_entry = f"'{table}' | "
        if len(current_line) + len(table_entry) > max_line_length:
            # 如果当前行的长度超出限制，保存当前行并换行
            formatted_lines.append(current_line.strip())
            current_line = "  " + table_entry  # 下一行缩进两个空格
        else:
            current_line += table_entry

    # 添加最后一行
    formatted_lines.append(current_line.rstrip('| ').strip() + ';')

    # 合并为最终结果
    return '\n'.join(formatted_lines)

def map_sql_type_to_ts_type(sql_type):
    sql_type = sql_type.lower()
    if 'int' in sql_type or 'tinyint' in sql_type or 'bigint' in sql_type:
        return 'number'
    if 'varchar' in sql_type or 'text' in sql_type or 'char' in sql_type:
        return 'string'
    if 'datetime' in sql_type or 'timestamp' in sql_type:
        return 'string'
    if 'float' in sql_type or 'double' in sql_type or 'decimal' in sql_type:
        return 'number'
    if 'boolean' in sql_type or 'bit' in sql_type:
        return 'boolean'
    return 'any'


def parse_enum_type(enum_values):
    values = enum_values.split(',')
    return ' | '.join(["'{}'".format(value.strip().strip("'")) for value in values])


def to_camel_case(name, capitalize=False):
    parts = name.split('_')
    return ''.join(word.capitalize() for word in parts) if capitalize else parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


# 示例用法
sql_file = 'navicat_export.sql'
output_file = 'output/interfaces.ts'

if os.path.exists(sql_file):
    out_folder = os.path.dirname(output_file)  # 提取 output 文件夹
    parse_sql_to_ts(sql_file, os.path.basename(output_file), out_folder)
else:
    print(f"SQL file '{sql_file}' not found.")
