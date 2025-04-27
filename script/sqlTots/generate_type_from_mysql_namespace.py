import os
import pymysql
import re

# 1. 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',  # 改成你的
    'user': 'jeff',       # 改成你的
    'password': '123456', # 改成你的
    'database': 'my_store', # 改成你的
    'charset': 'utf8mb4',
}

# 2. 类型映射
def db_type_to_ts(db_type):
    db_type = db_type.lower()
    if 'enum' in db_type:
        # 提取枚举值
        enum_values = re.findall(r'enum\((.*?)\)', db_type)
        if enum_values:
            values = enum_values[0].replace("'", "").split(',')
            return ' | '.join([f'"{value.strip()}"' for value in values])
    if any(t in db_type for t in ['int', 'decimal', 'float', 'double']):
        return 'number'
    if any(t in db_type for t in ['char', 'text', 'set']):
        return 'string'
    if 'bool' in db_type:
        return 'boolean'
    if any(t in db_type for t in ['date', 'time', 'year']):
        return 'string'
    if 'json' in db_type:
        return 'any'
    return 'any'

# 3. 小工具函数：驼峰转大驼峰
def to_pascal_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

# 4. 生成TypeScript命名空间接口
if __name__ == "__main__":
    output_folder = './types/db/mysql'
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    # 查询数据库中所有表名
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    connection.close()

    module_prefix = to_pascal_case(DB_CONFIG['database'])
    namespace_lines = [f'export namespace {module_prefix} {{']

    for table in tables:
        table_name = table[0]
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = f"""
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_COMMENT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION;
        """

        cursor.execute(sql)
        columns = cursor.fetchall()

        interface_name = to_pascal_case(table_name)

        interface_lines = [
            f"  /**",
            f"   * 自动生成：{table_name}表对应的TypeScript类型定义",
            f"   */",
            f"  export interface {interface_name} {{"
        ]

        for col in columns:
            ts_type = db_type_to_ts(col['COLUMN_TYPE'])
            nullable = '?' if col['IS_NULLABLE'] == 'YES' else ''
            comment = col['COLUMN_COMMENT'] if col['COLUMN_COMMENT'] else ''
            if nullable:
                if comment:
                    comment += '（可选）'
                else:
                    comment = '（可选）'
            if comment:
                interface_lines.append(f"    /** {comment} */")
            interface_lines.append(f"    {col['COLUMN_NAME']}{nullable}: {ts_type};" )

        interface_lines.append("  }" )
        namespace_lines.extend(interface_lines)

        cursor.close()
        connection.close()

    namespace_lines.append('}')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, f'{module_prefix}.d.ts')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(namespace_lines))

    print(f"✅ 成功生成命名空间文件: {output_path}")