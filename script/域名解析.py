from datetime import datetime
import os
import sys
import subprocess
import asyncio
import re
from cloudflare import Cloudflare
import chardet  # 导入chardet

# Cloudflare API 配置
API_TOKEN = 'assaa'  # 替换为你的 Cloudflare API Token
ZONE_NAME = 'baidu.com'  # 替换为你的域名

# 需要获取解析的域名列表
domain_list = ['www.baidu.site','www.baidu.site']

# 目标 hosts 文件路径
HOSTS_FILE_PATH = 'hosts.txt'  # 在 Windows 上可以使用 'C:\\Windows\\System32\\drivers\\etc\\hosts'


def is_valid_ip(ip_address):
    """
    判断给定的 IP 地址是否有效，并排除回环地址
    :param ip_address: IP 地址
    :return: 是否有效
    """
    # 检查是否为有效的 IPv4 地址
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_address):  # 简单的 IPv4 地址检查
        return True
    # 检查是否为有效的 IPv6 地址
    elif re.match(r'^[0-9a-fA-F:]+$', ip_address):  # 简单的 IPv6 地址检查
        # 排除回环地址和本地链接地址
        if ip_address == "::1" or ip_address.startswith("fe80::"):
            return False
        # 检查是否是以数字开头的 IPv6 地址
        if ip_address[0].isdigit():
            return True
        return False
    return False

def resolve_local_dns_with_ping(domain):
    """
    使用 ping 命令解析域名的 IP 地址
    :param domain: 域名
    :return: 解析到的 IP 地址或 None
    """
    try:
        # 在 Windows 上使用 'ping' 命令来解析
        result = subprocess.run(
            ["ping", "-n", "1", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            # 从 ping 的输出中提取 IP 地址
            for line in result.stdout.splitlines():
                if "TTL" in line:
                    ip_address = line.split(' ')[2]
                    if is_valid_ip(ip_address):
                        return ip_address
        return None
    except Exception as e:
        print(f"解析失败: {e}")
        return None


def resolve_local_dns_with_nslookup(domain):
    """
    使用 nslookup 命令解析域名的 IP 地址
    :param domain: 域名
    :return: 解析到的 IP 地址或 None
    """
    try:
        result = subprocess.run(
            ["nslookup", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            # 遍历 nslookup 输出的每一行，寻找包含 "Address:" 的行
            for line in result.stdout.splitlines():
                if "Address:" in line:
                    print(line)
                    ip_address = line[10:]
                    # 如果是有效的 IP 地址，返回该地址
                    if is_valid_ip(ip_address):
                        return ip_address
        return None
    except Exception as e:
        print(f"解析失败: {e}")
        return None


def parse_zone_data(zone_data):
    """
    解析 DNS 区域数据，提取域名、解析类型和解析值
    :param zone_data: DNS 区域数据（字符串）
    :return: 一个包含域名、解析类型和解析值的字典列表
    """
    # 正则表达式提取域名、类型和解析值
    pattern = re.compile(r"(?P<domain>[^\s]+)\s+\d+\s+IN\s+(?P<type>[A-Z]+)\s+(?P<value>[^\s]+)")

    # 匹配所有记录
    matches = pattern.findall(zone_data)

    # 结果列表
    records = []

    # 处理每一条记录
    for match in matches:
        domain, record_type, value = match
        # 如果域名结尾有点.则去掉
        if domain.endswith("."):
            domain = domain[:-1]
        record = {
            "domain": domain,
            "type": record_type,
            "value": value
        }
        records.append(record)

    return records


async def fetch_dns_records_from_cloudflare(api_token,domain_list):
    """
    从 Cloudflare 获取 DNS 记录
    :param api_token: Cloudflare API Token
    :param zone_name: 域名
    :return: DNS 记录列表
    """
    DNS_RECORDS = []

    client = Cloudflare(api_token=api_token)
    try:
        # 获取所有域名的 Zone 列表
        page = client.zones.list()
        zone_id = page.result[0].id
        if zone_id:
            # 获取 Zone 下的所有 DNS 记录
            response = client.dns.records.export(
                zone_id=zone_id,
            )
            records =  parse_zone_data(response)
            if(len(records) >0):

                # 遍历域名找到与domin_list相符的记录
                for record in records:
                    if record["domain"] in domain_list:
                        # 拼接解析到的记录值为hosts格式的字符串
                        record_str = f"{record['value']} {record['domain']}"
                        DNS_RECORDS.append(record_str)
            else:
                print("没有找到记录")
            return DNS_RECORDS
        else:
            print("没有找到Zone")
            sys.exit(1)
    except Exception as e:
        print(f"从 Cloudflare 获取 DNS 记录失败: {e}")
        sys.exit(1)


def get_file_encoding(file_path):
    with open(file_path, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def update_hosts_file(records, hosts_file_path):
    """
    将有效 DNS 记录写入 hosts 文件
    :param records: 有效的 DNS 记录（字符串列表，每条格式为 'IP 域名'）
    :param hosts_file_path: hosts 文件路径
    """
    try:
        # 创建 hosts 文件路径（如果不存在）
        if not os.path.exists(hosts_file_path):
            print(f"{hosts_file_path} 文件不存在，正在创建新文件...")
            open(hosts_file_path, "w").close()

        # 读取现有内容
        with open(hosts_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            updated_records = lines.copy()

        # 正则模式匹配 IP 和域名
        record_pattern = re.compile(r"^\s*(\S+)\s+(\S+)\s*$")

        # 移除掉旧记录
        for line in lines:
            match = record_pattern.match(line)
            if match:
                ip, domain = match.groups()
                for record in records:
                    if record:
                        if record.endswith(domain):
                            updated_records.remove(line)
                            break
            # 如果行是时间戳则跳过
            if line.startswith("# Updated on"):
                updated_records.remove(line)


        # 添加新记录
        for record in records:
            if record:
                updated_records.append(record + "\n")


        # 添加新的更新时间
        updated_records.append(f"# Updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(updated_records)
        # 写回 hosts 文件
        with open(hosts_file_path, "w", encoding="utf-8") as file:
            file.writelines(updated_records)

        print(f"hosts 文件更新完成，保存在 {hosts_file_path}！")

    except Exception as e:
        print(f"更新 hosts 文件失败: {e}")
async def main(domain_list):
    resolved_records = []
    faild_domain = []
    for domain in domain_list:
        # 首先尝试用 ping 方法解析
        ip_address = resolve_local_dns_with_ping(domain)
        if ip_address:
            print(f"本地解析成功 (ping): {domain} -> {ip_address}")
            resolved_records.append(f"{ip_address} {domain}")
        else:
            print(f"ping 解析失败: {domain}")
            faild_domain.append(domain)

            # 如果 ping 失败，尝试用 nslookup 方法解析
            ip_address = resolve_local_dns_with_nslookup(domain)
            if ip_address:
                print(f"本地解析成功 (nslookup): {domain} -> {ip_address}")
                resolved_records.append(resolved_records.append(f"{ip_address} {domain}"))
            else:
                print(f"nslookup 解析失败: {domain}")
                faild_domain.append(domain)

    # 如果有未解析成功的域名，尝试从 Cloudflare 获取
    if len(faild_domain)>0:
        cloudflare_records = await fetch_dns_records_from_cloudflare(API_TOKEN,faild_domain)
        # 合并解析结果
        resolved_records = list(set(resolved_records + cloudflare_records))

    print(resolved_records)
    # 更新 hosts 文件
    update_hosts_file(resolved_records, HOSTS_FILE_PATH)


if __name__ == "__main__":
    asyncio.run(main(domain_list))

