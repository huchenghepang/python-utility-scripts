import json
import os
import re
from googletrans import Translator
from generate_ts_from_swagger import create_or_append_export
import textwrap
from parse_ts import run_parse_ts
# 假设 Swagger 文件名为 swagger.json


current_dir = os.path.dirname(os.path.abspath(__file__))
SWAGGER_FILE = os.path.join(current_dir,'swagger.json')
OUTPUT_DIR = os.path.join(current_dir,'src/api')

# 全局储存的响应ts类型对应字典
response_ts_type_dict = {}

type_map = {
    "string": "string",
    "number": "number",
    "integer": "number",
    "boolean": "boolean",
    "array": "Array",
    "object": "Record<string, any>",
}


# 查询参数的类型数组 之后遍历生成到一个文件，并且在顶部导入对应的query参数
global_query_params_set = set()
# body对应的data参数，之后如果是不为空的话，会在顶部导入对应的请求参数DTO
global_body_params_set = set()


# 保存接口信息的字典
api_info = {}

def map_type(type_str: str) -> str:
    """
    根据类型映射表返回对应的类型
    :param type_str: 输入的类型字符串
    :return: 映射后的类型字符串
    """
    # 查找并返回映射的类型，如果没有匹配则返回原类型
    return type_map.get(type_str, type_str)


def generate_ts_interface_from_query_params(query_params: list[dict], query_params_name: str = "QueryParams") -> str:
    """
    生成 TypeScript 接口，表示所有查询参数，处理类型、必填、描述信息。
    :param query_params: Swagger 参数列表，每个元素是 dict，包含 name/schema/required/description 等
    :param query_params_name: 接口名称，默认 QueryParams
    :return: TypeScript 接口定义字符串
    """
    # 类型映射关系
    type_map = {
        "string": "string",
        "number": "number",
        "integer": "number",
        "boolean": "boolean",
        "array": "Array<any>",
        "object": "Record<string, any>",
    }

    def get_type(param_schema: dict) -> str:
        """
        将 Swagger 的 schema 映射为 TypeScript 类型
        """
        param_type = param_schema.get("type")
        if param_type == "array":
            item_type = param_schema.get("items", {}).get("type", "any")
            return f"Array<{type_map.get(item_type, item_type)}>"
        elif param_type == "object":
            return "Record<string, any>"
        else:
            return type_map.get(param_type, "any")

    # 拼接字段定义
    lines = [f"export interface {query_params_name} {{"]
    for p in query_params:
        name = p["name"]
        required = "" if p.get("required", False) else "?"
        ts_type = get_type(p.get("schema", {}))
        description = p.get("description", "")
        comment = f"  /** {description} */" if description else ""
        field = f"  {name}{required}: {ts_type};"
        if comment:
            lines.append(comment)
        lines.append(field)
    lines.append("}")

    return "\n".join(lines)





# 翻译文本
# 用于缓存翻译结果
translation_cache = {}


def translate_text(text: str, src='zh-cn', dest='en') -> str:
    """
    翻译文本
    :param text: 要翻译的文本
    :param src: 源语言
    :param dest: 目标语言
    :return: 翻译后的文本(类型为str)
    """

    # 如果翻译结果已经缓存，则直接返回缓存的结果
    if (text, src, dest) in translation_cache:
        print("从缓存中获取翻译：")
        return translation_cache[(text, src, dest)]
    translator = Translator()
    translation = translator.translate(text, src=src, dest=dest)

    # 将翻译结果缓存
    translation_cache[(text, src, dest)] = translation.text
    return translation.text

# 读取 Swagger 文件
def read_swagger(file_path):
    print(f"正在读取 Swagger 文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 提取路径中的占位符
def extract_path_params(path:str):
    """
    提取路径中的占位符，例如：/users/{id} -> ['id']
    :param path:
    :return: list
    """
    return re.findall(r'\{(\w+)}', path)

# 处理函数名
def process_function_name(name:str,method_name:str):
    """
    处理函数名，将下划线替换为空格，并加上前缀
    :param name:
    :return: str
    """
    # 替换下划线为空格
    function_name = f"{name.replace('Controller_', '').replace('_', '')}".capitalize()
    method_name = method_name.capitalize()
    # 加上前缀
    function_name = f"req{function_name}"
    return function_name


def generate_common_query_params_file(global_query_params_set, output_path: str):
    """
    根据全局 query 参数集合生成通用参数定义文件
    :param global_query_params_set: 全局 query 参数集合，类型为 set[str]
    :param output_path: 输出文件路径（含文件名），如 './output/common_query_params.py'
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for param in sorted(global_query_params_set):
            f.write(f"{param} \n")

    print(f"✅ 通用 query 参数定义文件已生成: {output_path}")



def generate_ts_type_from_query_params(query_params,query_name:str = "QueryParams"):
    """
    生成一个 TypeScript 类型，表示所有查询参数
    :param query_params: 查询参数列表，包含每个参数的 `name` 和 `schema.type`
    :return: TypeScript 类型字符串
    """
    # 构建每个查询参数的 name: type 字符串
    query_code = ', '.join([f"{p['name']}: {map_type(p['schema']['type'])}" for p in query_params]) if query_params else ""

    # 如果查询参数不为空，生成 TypeScript 类型接口
    if query_code:
        return f"type {query_name} = {{ {query_code} }};"
    else:
        return ""

# 根据请求方法生成对应的请求函数
def generate_request_function(path:str, method:str, operation_id:str, parameters, response_schema,origin_text_tag, body_ref=None,summary=None):
    req_method = method.lower()  # get/post/patch/delete
    # 处理函数名
    req_function_name = process_function_name(operation_id,method)

    # 提取路径参数
    path_params = extract_path_params(path)

    # 构建参数列表
    query_params = [p for p in parameters if p['in'] == 'query']
    body_param = [p for p in parameters if p['in'] == 'body']

    # 解析operation_id 字符串 方便匹配全局的响应类型
    operation_arr = operation_id.split('Controller_')
    operation_controller = operation_arr[0]
    handler_name = operation_arr[1]

    target_response_type = f"{operation_controller}-{handler_name}-res"
    response_type = response_ts_type_dict.get(target_response_type)
    if(response_type):
        api_info[origin_text_tag]["body_params"].add(response_type)

    # 生成 query 和 path 参数的处理代码
    # query参数类型

    # Query参数类型名称
    query_params_type_name = f"{req_function_name}Query".capitalize()
    query_code = generate_ts_interface_from_query_params(query_params,query_params_type_name) if (query_params and len(query_params)>0) else None
    path_code = ', '.join([f"{param}: string" for param in path_params]) if (path_params and len(path_params)>0) else ""
    if query_code:
        api_info[origin_text_tag]["query_params"].add(query_params_type_name)
        global_query_params_set.add(query_code)
    # 生成 body 参数处理代码
    body_temp_type = ""
    body_code = ""
    if body_ref:
        body_temp_type = body_ref.split('/')[-1]
        api_info[origin_text_tag]["body_params"].add(body_temp_type)
        global_body_params_set.add(body_temp_type)
        body_code = f"  data: {body_ref.split('/')[-1]}"  # 如果有请求体引用，直接关联 DTO 类型
    elif body_param:
        body_temp_type = body_param[0]['schema']['type']
        body_code = f"  data: {body_temp_type}"  # 没有引用则直接使用类型
        api_info[origin_text_tag]["body_params"].add(body_temp_type)
        global_body_params_set.add(body_temp_type)

    # 生成响应代码
    response_code = f"response: {response_schema}"

    # 处理路径中的占位符，并替换为 ${} 格式
    formatted_path = path
    for param in path_params:
        formatted_path = formatted_path.replace(f"{{{param}}}", f"${{{param}}}")

    query_str = f"{'query:' + query_params_type_name if query_code else ''}"
    all_str = ", ".join(s for s in [query_str, path_code, body_code] if s.strip())
    # 使用模板字符串生成函数代码，注意路径和参数部分使用 ${} 格式
    query_valid = query_code and query_code.strip()
    body_valid = body_code and body_code.strip()

    options_lines = []
    if query_valid:
        options_lines.append("params: query")


    # 组装 options 代码
    if options_lines:
        options_code = ",\n    ".join(options_lines)
        request_args = f"`{formatted_path}`, {"data," if body_valid else ""} {{\n    {options_code}\n  }}"
    else:
        request_args = f"`{formatted_path}` {",data" if body_valid else ""}"

    summary_str = f"/**\n*{summary}\n*/" if summary else ""
    # 生成完整函数代码
    function_code = textwrap.dedent(f"""{summary_str.strip()}
export const {req_function_name} = async ({all_str}):Promise<{response_type if response_type else "any"}> => {{
    return await request.{req_method}({request_args});
}};
    """).strip()
    return function_code.strip()
# 生成目录
def generate_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

# 根据 tags 生成分类文件
def generate_tag_files(tags, functions):
    for tag in tags:
        tag_file = os.path.join(OUTPUT_DIR, f'{tag}.ts')
        with open(tag_file, 'w', encoding='utf-8') as f:
            f.write('import { request } from \'../utils/request\';\n\n')
            for func in functions:
                if func['tag'] == tag:
                    f.write(func['code'] + '\n\n')


def generate_import_statement(query_params: set, body_params: set, import_path: str = '@/types/api') -> str:
    """
    合并 query 和 body 参数集合，生成导入语句字符串

    :param query_params: 查询参数集合
    :param body_params: 请求体参数集合
    :param import_path: 导入路径，默认 '@/types/api'
    :return: 完整的 import 语句字符串
    """
    # 合并两个集合，去重
    all_params_set = query_params.union(body_params)

    # 排序并拼接成字符串
    all_params_str = ", ".join(sorted(all_params_set))

    # 生成 import 语句
    import_statement = f"import {{ {all_params_str} }} from '{import_path}'"

    return import_statement

# 根据Api 信息生成分类文件
def generate_api_info_files(api_info):
    for origin_text_tag,info in api_info.items():
        # 英文名称
        en_name:str = info['en'].strip().replace(" ","")
        functions = info['functions']

        # 合并两个集合
        query_params_set = info['query_params']
        body_params_set = info['body_params']


        # 生成导入字符串
        all_params_set_str = ""
        if(len(query_params_set)>0 or len(body_params_set)>0):
            all_params_set_str = generate_import_statement(query_params_set,body_params_set,import_path='../types/api')




        api_file = os.path.join(OUTPUT_DIR, f'{en_name}.ts')
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write('import { request } from \'../utils/request\';\n\n')
            f.write(f'{all_params_set_str}\n\n')
            for func in functions:
                    f.write(func + '\n\n')

# 主函数：解析 Swagger 文档并生成请求文件
def generate_api_requests(swagger_data):
    paths = swagger_data['paths']
    functions = []

    tags = set()

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            # 操作的ID 比如：ProductsController_findAll 实际上对应着定义接口的方法名称
            operation_id = operation['operationId']
            # 请求的参数体规则
            parameters = operation.get('parameters', [])
            # 响应体规则
            responses = operation.get('responses', {})
            response_schema = responses.get('200', {}).get('content', {}).get('application/json', {}).get('schema', {}).get('type', 'any')
            # 方法的总结描述
            summary = operation.get('summary', None)
            # 获取请求体的 schema
            body_ref = None
            if 'requestBody' in operation:
                body_ref = operation['requestBody'].get('content', {}).get('application/json', {}).get('schema', {}).get('$ref', None)

            # 处理标签 对应的中文可能需要转为英文
            origin_text_tag =operation.get('tags', [])[0]

            if(origin_text_tag not in tags):
                api_info.setdefault(origin_text_tag, {
                    'en': translate_text(origin_text_tag),
                    'query_params': set(),
                    'body_params': set(),
                    "origin_text": origin_text_tag,
                    "functions": []
                })


            tags.add(origin_text_tag)
            # 生成请求函数
            function_code = generate_request_function(path, method,
            operation_id, parameters,
            response_schema, origin_text_tag,body_ref,summary)
            functions.append({
                'tag': origin_text_tag,
                'code': function_code
            })

            # 添加函数到api_info
            api_info[origin_text_tag]["functions"].append(function_code)

    # 生成目录
    generate_directory()

    # 根据 tags 生成分类文件
    # generate_tag_files(tags, functions)

    # 遍历query类型生成对应的ts文件

    # 当前文件运行目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 生成的文件路径
    output_path = os.path.join(current_dir,'src/types/api/common_query_params.ts')

    generate_common_query_params_file(global_query_params_set, output_path)

    # 根据api_info 生成分类文件
    generate_api_info_files(api_info)

    print("✅ API 请求文件生成完毕！")

    create_or_append_export(output_path)


def generate_api(swagger_file, output_dir,res_type_path:str):
    # 获取全局的ts响应类型
    global response_ts_type_dict
    response_ts_type_dict = run_parse_ts(res_type_path)
    # 获取response_ts_type_dict 有多少个key并提醒打印
    print(f"成功获取到了响应ts,全局响应类型有: {len(response_ts_type_dict)}个")
    swagger_data = read_swagger(swagger_file)
    global OUTPUT_DIR
    OUTPUT_DIR = output_dir
    generate_api_requests(swagger_data)

if __name__ == '__main__':
    res_type_path = os.path.join(current_dir,'src/types/api/res_output.ts')
    generate_api(SWAGGER_FILE, OUTPUT_DIR,res_type_path)