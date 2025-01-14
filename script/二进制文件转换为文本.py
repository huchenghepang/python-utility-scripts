import yaml


def convert_binary_yaml_to_text(binary_file_path, text_file_path):
    # 读取二进制文件
    with open(binary_file_path, 'rb') as binary_file:
        # 读取二进制内容
        binary_content = binary_file.read()

    # 由于是纯二进制，尝试直接解析二进制内容
    try:
        # 使用yaml的方式对内容解析（注意：yaml.safe_load会根据文件格式解析）
        data = yaml.safe_load(binary_content)

        # 将解析的内容写入文本格式的yaml文件
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            yaml.dump(data, text_file, default_flow_style=False, allow_unicode=True)

        print("文件已成功转换为文本格式 YAML！")

    except Exception as e:
        print(f"处理过程中出错: {e}")

# 示例用法
convert_binary_yaml_to_text('pnpm-lock.yaml', 'text_output.yaml')
