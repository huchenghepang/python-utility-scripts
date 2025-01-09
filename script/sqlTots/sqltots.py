import re
import os


def parse_sql_to_ts(sql_file, output_file):
    # 提取文件名并确保输出文件后缀为 .d.ts
    file_name = os.path.basename(output_file)
    if not file_name.endswith('.d.ts'):
        output_file = os.path.splitext(file_name)[0] + '.d.ts'

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 匹配 CREATE TABLE 的表结构和字段
    table_pattern = r'CREATE TABLE `(\w+)`\s+\((.*?)\)\s+ENGINE'
    field_pattern = r'^\s*`(\w+)`\s+(\w+.*?)(?:\((.*?)\))?(.*?COMMENT\s+\'(.*?)\')?,?'

    # 匹配主键的结构
    primary_key_pattern = r"PRIMARY KEY\s*\(\s*`([^`]+)`\s*\)"

    # 匹配NOT NULL 是存在的正则表达式
    NOT_NULL_PATTERN = r'\bNOT NULL\b'
    # 处理NOT NULL 如果有NOT NULL '‘ 没有则 ？
    has_NOTNULL_str = ''

    # 是否必填
    isRequired_str = True


    # 记录所有的表名
    table_names = []
    primary_key_field = ''
    matches = re.findall(table_pattern, sql_content, re.S)
    ts_interfaces = []
    ts_mysql2_interfaces = ['import { RowDataPacket } from "mysql2";']

    for table_name, fields in matches:
        # 转换表名为大驼峰命名
        ts_table_name = to_camel_case(table_name, capitalize=True)
        print('1-'+fields)

        # 匹配主键
        primary_key_match = re.search(primary_key_pattern, fields)
        if primary_key_match:
            primary_key_field ='主键：' +primary_key_match.group(1)
            print('2-'+primary_key_field)
        else:
            primary_key_field = '主键：无'



        # 记录表名
        table_names.append(ts_table_name)

        ts_interface = f"export interface {ts_table_name} {{\n  // 源表名称: {table_name} - {primary_key_field}\n"
        ts_mysql2_interface = f"export interface {ts_table_name} extends RowDataPacket {{\n  // 源表名称: {table_name} - {primary_key_field}\n"

        for line in fields.splitlines():
            line = line.strip()
            if line.startswith(('PRIMARY KEY', 'INDEX', 'CONSTRAINT')):
                continue

            # 使用正则表达式忽略大小写查找 NOT NULL
            # 使用正则表达式忽略大小写查找 NOT NULL
            if re.search(r'\bNOT NULL\b', line, re.IGNORECASE):
                has_NOTNULL_str = ''
                isRequired_str = True
            else:
                has_NOTNULL_str = '?'
                isRequired_str = False



            field_match = re.match(field_pattern, line)
            if field_match:
                field_name, field_type, enum_values, other, comment = field_match.groups()





                # 处理字段类型
                if 'enum' in field_type.lower() and enum_values:
                    ts_type = parse_enum_type(enum_values)
                else:
                    ts_type = map_sql_type_to_ts_type(field_type)


                # 字段注释
                comment_text = f"{comment.strip()}" if comment else "无描述"

                # 为空时 注释字段表明 是必填的
                if isRequired_str == True:
                    comment_text = f"{comment_text} 必填"
                else:
                    comment_text = f"{comment_text} 可选"


                ts_comment = f"/** {comment_text} */"


                field_name += has_NOTNULL_str


                # 生成字段定义
                ts_interface += f"  {ts_comment}\n  {field_name}: {ts_type};\n"
                ts_mysql2_interface += f"  {ts_comment}\n  {field_name}: {ts_type};\n"

        ts_interface += "}\n"

        # 定义所有表名类型  Tables



        ts_mysql2_interface += "}\n"

        ts_interfaces.append(ts_interface)
        ts_mysql2_interfaces.append(ts_mysql2_interface)

    tables_str = 'export type Tables = ' + ' | '.join(f"'{table}'" for table in table_names) + ';\n'

    ts_interfaces.insert(0,tables_str)
    ts_mysql2_interfaces.insert(1,tables_str)
    # 写入主接口文件
    with open(output_file, 'w', encoding='utf-8') as f:

        f.write("\n".join(ts_interfaces))

    # 写入 MySQL2 接口文件
    ts_mysql2_file = output_file.replace('.d.ts', '_mysql2.d.ts')
    with open(ts_mysql2_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(ts_mysql2_interfaces))

    print(f"TypeScript interfaces have been written to {output_file}")
    print(f"MySQL2 interfaces have been written to {ts_mysql2_file}")
    print(f"typescript 接口已经写入到 {output_file}")
    print(f"typescript mysql2接口已经写入到 {ts_mysql2_file}")


def map_sql_type_to_ts_type(sql_type):
    sql_type = sql_type.lower()
    if 'int' in sql_type or 'tinyint' in sql_type or 'bigint' in sql_type:
        return 'number'
    if 'varchar' in sql_type or 'text' in sql_type or 'char' in sql_type:
        return 'string'
    if 'datetime' in sql_type or 'timestamp' in sql_type:
        return 'Date'
    if 'float' in sql_type or 'double' in sql_type or 'decimal' in sql_type:
        return 'number'
    if 'boolean' in sql_type or 'bit' in sql_type:
        return 'boolean'
    return 'any'


def parse_enum_type(enum_values):
    values = enum_values.split(',')
    enum_values = [value.strip().strip("'") for value in values]
    return ' | '.join(f"'{value}'" for value in enum_values)


def to_camel_case(name, capitalize=False):
    parts = name.split('_')
    if capitalize:
        return ''.join(word.capitalize() for word in parts)
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])


# 示例用法
sql_file = 'navicat_export.sql'
output_file = 'interfaces.ts'

if os.path.exists(sql_file):
    parse_sql_to_ts(sql_file, output_file)
else:
    print(f"SQL file '{sql_file}' not found.")
