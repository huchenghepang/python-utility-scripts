import os

from generate_api_requests import generate_api
from generate_ts_from_swagger import generate_typescript_from_swagger

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    swagger_path = os.path.join(current_dir, 'swagger.json')
    output_file = os.path.join(current_dir, 'src/types/api/output.d.ts')
    output_dir = os.path.join(current_dir,'src/api')
    res_type_path = os.path.join(current_dir, 'src/types/api/res_output.ts')
    # 生成 TypeScript 类型定义
    generate_typescript_from_swagger(
        swagger_path,
        output_file
    )
    # 请求路径
    request_client_import_path = '#/api/request'
    # 请求实例
    request_client_name = 'requestClient'
    # 生成api接口
    generate_api(
        swagger_path,
        output_dir,
        res_type_path,
        request_client_import_path,
        request_client_name
    )




