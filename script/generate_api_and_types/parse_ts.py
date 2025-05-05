import os
from typing import Dict
import re
import pprint
def read_file_content(file_path:str)->str:
    with open(file_path,'r',encoding='utf-8') as f:
        return f.read()


def parse_multiple_ts_interfaces(ts_code: str) -> Dict[str, Dict[str, str]]:
    interfaces = {}

    # 提取所有 interface 块：interface 名 和内部内容
    pattern = r'export\s+interface\s+(\w+)\s*\{([^}]+)\}'
    matches = re.findall(pattern, ts_code, re.DOTALL)

    for interface_name, body in matches:
        kv_pattern = r"'([^']+)'\s*:\s*([^;]+);"
        kv_matches = re.findall(kv_pattern, body)
        interface_dict = {k: v.strip() for k, v in kv_matches}
        interfaces[interface_name] = interface_dict
    return interfaces


def run_parse_ts(path:str):
    """
    解析ts文件，返回一个字典，key为interface名，value为interface的内容
    :param path:
    :return:
    """
    content = read_file_content(path)
    return parse_multiple_ts_interfaces(content).get('MergedJson')

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = r'./src/types/api/res_output.ts'
    if not os.path.exists(path):
        path = os.path.join(current_dir,path)
    data = run_parse_ts(path)
    pprint.pprint(data)



