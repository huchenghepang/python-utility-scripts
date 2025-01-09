import os
import time
import json
def split_file(input_file, chunk_size, output_dir):
    # 创建输出目录，如果不存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取文件的基本信息
    file_name = os.path.basename(input_file)
    create_time = int(time.time())  # 文件创建时间（UNIX时间戳）
    file_size = os.path.getsize(input_file)
    file_type = file_name.split('.')[-1]  # 获取文件扩展名作为文件类型
    total_chunk = 0  # 用于统计分块数量

    # 用于存储文件信息
    file_info = {
        "fileName": file_name,
        "createTime": create_time,
        "fileSize": file_size,
        "fileType": file_type,
        "TOTAL_CHUNK": total_chunk
    }

    # 进行文件分割
    with open(input_file, 'rb') as f:
        chunk_number = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            chunk_number += 1
            total_chunk += 1
            output_path = os.path.join(output_dir, f'{chunk_number}')
            with open(output_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
    # 将统计信息保存到 JSON 文件
    with open('file_info.json', 'w') as json_file:
        json.dump(file_info, json_file, indent=4)
    # 更新 TOTAL_CHUNK 信息
    file_info["TOTAL_CHUNK"] = total_chunk

    return file_info

# 使用示例，输出文件到当前目录下的 output 文件夹
file_info = split_file('input.pdf', 5 * 1024 * 1024, './output')

# 输出统计信息
print(file_info)
