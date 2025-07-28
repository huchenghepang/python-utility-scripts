import requests
from pprint import pprint
from googletrans import Translator
import stringcase
import re
# 定义变量

cookie = '''
isg=BA8PWJZatHEdzrEZNXUwCWpynqMZNGNW4tWRGCEQr37N8CbyJgWcpD-p8iDOiDvO; locale=zh-cn; EGG_SESS_ICONFONT=dzIFRF6UFHpWicZx2_bPclFotPadI3FgvwtBcNVNJBUVc-1MvhhLOhMuG6sdkf8naS0hzZYVOCDQhLdF6iQ4KzFPsnbSYDGbEz6QHB6mYnTTVzSVB_DFI6DPPTiZT4a2BLB1z5uR1tO5UkBs9L5i_A==; ctoken=ad8cvf78Ju9QetLgYzPtETZN; u=13943308; u.sig=s3Qvg77Ls_K7ruQiR7LMTPOxJpYbhSnI7sHDv28Wtrs; tfstk=g9KIIPwWCWVBtQPMKXHNhVTAhPsWOQiqN86JnLEUeMILw7pA_p-FYLzWNC9AyHJPv3sW1QOe8MLePTO2pQ_oK_5RNQJJ8Aoq0pvhqgFSgmoVoTVuUH18agIhXCF0LViq0pvLL9H2Bm-rYkqGO_IRJaQTB1X5e7d82NH1eTPLykdJBA1GFuedwueOXtBQpgIJwdH1E1BKpyNVFY5BdvA7SWNmy_vd1uEJf0bCGpUz2uK1dwOMp19eLh6CRsQabSU6vCJJYHbiGSIkQEOWyQ04SM9JJMB2KDZ1DpLwVO-rUz1pth99XNw40gTpOUQD5m4cJa1BWHQ_eupGVFQvPBGQ-6Le1ZXOW8icQI59KHLsE5ppg6sdBNoxhdQJ7HbDYfECDEvFYUdouPjBeeI14qrVG9w_PR_0VO1qCAaurWlb8dSYw2tVJOXCfAM_OGQdIO1qCAaurwBGQPMsCWsO.
'''.strip()

# 定义请求头
headers = {
    'Cookie': cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
}

# 定义请求的url地址
url = "https://www.iconfont.cn/api/user/myprojects.json"


# 项目详情地址 query参数为pid
project_url = "https://www.iconfont.cn/api/project/detail.json"

# 下载地址 query参数为pid
download_url ='https://www.iconfont.cn/api/project/download.zip'

# 发起请求

response = requests.get(url, headers=headers)

# 解析响应数据
data = response.json()

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
    if (text, src, dest) in translation_cache:
        return translation_cache[(text, src, dest)]

    try:
        translator = Translator()
        translation = translator.translate(text, src=src, dest=dest)
        translation_cache[(text, src, dest)] = translation.text
        return translation.text
    except Exception as e:
        print(f"翻译失败：{text}，错误信息：{e}")
        return text  # 原样返回以避免中断



def to_pascal_case_v2(text: str) -> str:
    # 统一分隔符为空格
    normalized = re.sub(r'[\s_\-]+', ' ', text.strip())
    return stringcase.pascalcase(normalized)

# 提取iconfont的项目列表
projects = data.get('data', {}).get('ownProjects', [])



project_id_list = []
project_name_list = []


def get_project_detail(project_id:str)->dict:
    """
    获取项目详情
    :param project_id: 项目id
    :return: 项目详情
    """
    params = {
        'pid': project_id
    }
    response = requests.get(project_url, headers=headers, params=params)
    data = response.json()
    return data.get('data', {})

def build_type_union(project_name: str, font_class_list: list[str], max_line_length: int = 80) -> str:
    lines = [f"{project_name} ="]
    current_line = "  "
    parts = [f"'{cls}'" for cls in font_class_list]

    for i, part in enumerate(parts):
        next_part = part + " | " if i < len(parts) - 1 else part  # 末尾不加 |
        # 判断是否换行
        if len(current_line) + len(next_part) > max_line_length:
            lines.append(current_line.rstrip())
            current_line = "  " + next_part
        else:
            current_line += next_part

    if current_line.strip():
        lines.append(current_line.rstrip())

    return '\n'.join(lines)



def download_project(project_id):
    pass

type_str_list = []
online_url_list = []

# font_class_list = [] 生成type的联合类型
def generate_type(original_project_name:str,project_name:str, font_class_list,js_url:str,prefix:str = 'Icon'):
    """
    生成type的联合类型
    :param font_class_list: 字体类列表
    :return: 类型字符串
    """
    project_name =prefix+to_pascal_case_v2(project_name.replace(' ', ''))
    type_str = build_type_union(project_name, font_class_list, max_line_length=60)
    final_str = f"""
/**
* {original_project_name}
* {project_name}
* @see 在线链接 - https:{js_url}
*/
export type {type_str}\n
    """
    return final_str



for project in projects:
    project_id = project.get('id')
    project_id_list.append(project_id)
    original_project_name = project.get('name')
    project_name = translate_text(original_project_name)

    if len(project_name) !=0:
            project_name_list.append(project_name)

    # 获取项目详情
    project_detail = get_project_detail(project_id)
    # js文件在线访问地址
    js_url = (((project_detail or {}).get('font') or {}).get('js_file')) or ''
    if len(js_url) !=0:
        online_url_list.append("https"+js_url)
    # 获取iconfont的icon列表 (包含icon的名称和id,project_icon_name,font_class)
    icons = project_detail.get('icons', [])

    font_class_list = []
    for icon in icons:
        icon_name = icon.get('name')
        icon_id = icon.get('id')
        font_class ="icon-" + icon.get('font_class')
        font_class_list.append(font_class)

    # 生成type的联合类型
    type_str = generate_type(original_project_name,project_name,font_class_list,js_url)
    type_str_list.append(type_str)

# 生成type的文件
with open('type.d.ts', 'w', encoding='utf-8') as f:
    for type_str in type_str_list:
        f.write(type_str+'\n')
    temp_str=build_type_union("IconOnlineUrl",online_url_list,max_line_length=60)
    online_str = f"""
/**
* IconOnlineUrl
* @see 在线链接
*/
export type {temp_str}
    """
    f.write(online_str)






    

    





