import os
import pprint
import re
from typing import Dict


def read_file_content(file_path:str)->str:
    with open(file_path,'r',encoding='utf-8') as f:
        return f.read()


def parse_multiple_ts_interfaces(ts_code: str) -> Dict[str, Dict[str, str]]:
    interfaces = {}

    # 提取所有 interface 块
    interface_pattern = r'export\s+interface\s+(\w+)\s*\{([^}]+)\}'
    interface_matches = re.findall(interface_pattern, ts_code, re.DOTALL)

    for interface_name, body in interface_matches:
        # 匹配属性名（带双引号或不带引号）和类型
        prop_pattern = r'(?:"([^"]+)"|(\b\w+\b))\s*:\s*([^;]+);'
        prop_matches = re.findall(prop_pattern, body)

        interface_dict = {}
        for match in prop_matches:
            # match[0] 是带双引号的属性名，match[1] 是不带引号的属性名
            key = match[0] if match[0] else match[1]
            value = match[2].strip()
            interface_dict[key] = value

        interfaces[interface_name] = interface_dict

    return interfaces


def run_parse_ts(path:str):
    """
    解析ts文件，返回一个字典，key为interface名，value为interface的内容
    :param path:
    :return:
    """
    content = read_file_content(path)
    return parse_multiple_ts_interfaces(content)

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = r'./src/types/api/res_output.ts'
    if not os.path.exists(path):
        path = os.path.join(current_dir,path)
    data = run_parse_ts(path)
    pprint.pprint(data)



