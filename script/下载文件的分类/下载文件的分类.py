import os
import shutil
import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ==================== 配置部分 ====================

# 设置下载目录（源目录）
DOWNLOAD_DIR = r"C:\Users\jeff\Downloads"  # 请替换下载目录路径

# 设置目标目录
TARGET_DIR = r"D:\OrganizedDownloads"  # 请替换为希望存放副本的目标目录路径

# 定义文件类型与目标子文件夹的映射
FILE_TYPES = {
    '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    '文档': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.pptx'],
    '视频': ['.mp4', '.mkv', '.avi', '.mov'],
    '音乐': ['.mp3', '.wav', '.aac', '.flac','.lrc'],
    '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    '可执行程序': ['.exe', '.msi', '.bat', '.sh'],
    '笔记':['.md'],
    '字幕':['.lrc','.srt']
}

# 定义需要排除的临时文件扩展名
EXCLUDED_EXTENSIONS = ['.crdownload', '.tmp', '.part', '.download']

# 配置日志记录
LOG_FILE = os.path.join(TARGET_DIR, 'organize_downloads.log')
os.makedirs(TARGET_DIR, exist_ok=True)  # 确保目标目录存在
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# ==================== 脚本逻辑部分 ====================

class DownloadEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 处理文件创建事件
        if not event.is_directory:
            file_path = event.src_path
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext in EXCLUDED_EXTENSIONS:
                logging.info(f"忽略临时文件创建: {file_path}")
                return
            if not self.is_extension_tracked(ext):
                logging.info(f"忽略未追踪的文件类型: {file_path}")
                return
            logging.info(f"检测到新文件创建: {file_path}")
            self.process_file_later(file_path)

    def on_moved(self, event):
        # 处理文件移动（重命名）事件
        if not event.is_directory:
            dest_path = event.dest_path
            _, ext = os.path.splitext(dest_path)
            ext = ext.lower()
            if ext in EXCLUDED_EXTENSIONS:
                logging.info(f"忽略临时文件移动/重命名: {dest_path}")
                return
            if not self.is_extension_tracked(ext):
                logging.info(f"忽略未追踪的文件类型: {dest_path}")
                return
            logging.info(f"检测到文件移动/重命名: {dest_path}")
            self.process_file_later(dest_path)

    def is_extension_tracked(self, ext):
        """检查文件扩展名是否在 FILE_TYPES 中定义"""
        for extensions in FILE_TYPES.values():
            if ext in extensions:
                return True
        return False

    def process_file_later(self, file_path, delay=5):
        """延迟处理文件，确保下载完成"""
        def delayed_process():
            logging.info(f"等待 {delay} 秒后开始检查文件: {file_path}")
            time.sleep(delay)
            if self.is_file_ready(file_path):
                self.copy_file(file_path)
            else:
                logging.warning(f"文件仍在使用中或未准备好，跳过: {file_path}")

        threading.Thread(target=delayed_process).start()

    def is_file_ready(self, file_path, stability_time=2, checks=3):
        """
        检查文件是否准备好被复制，通过文件大小稳定性
        :param file_path: 文件路径
        :param stability_time: 每次检查之间的等待时间（秒）
        :param checks: 检查次数
        :return: True 如果文件大小在连续的检查中保持不变，否则 False
        """
        try:
            # 尝试以读模式打开文件，确保文件不被锁定
            with open(file_path, 'rb'):
                pass
        except IOError:
            logging.info(f"文件被锁定，无法打开: {file_path}")
            return False

        try:
            previous_size = os.path.getsize(file_path)
            for _ in range(checks):
                time.sleep(stability_time)
                current_size = os.path.getsize(file_path)
                if current_size != previous_size:
                    logging.info(f"文件大小变化，从 {previous_size} 到 {current_size}，可能还在下载中")
                    previous_size = current_size
                else:
                    return True
            return False
        except Exception as e:
            logging.error(f"检查文件大小稳定性时出错 {file_path}: {e}")
            return False

    def copy_file(self, file_path):
        try:
            _, filename = os.path.split(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            target_folder = None
            for folder, extensions in FILE_TYPES.items():
                if file_ext in extensions:
                    target_folder = os.path.join(TARGET_DIR, folder)
                    break
            if target_folder:
                os.makedirs(target_folder, exist_ok=True)
                target_path = os.path.join(target_folder, filename)
                target_path = self.get_unique_path(target_path)
                shutil.copy2(file_path, target_path)
                logging.info(f"复制: {filename} 到 {folder}/")
            else:
                # 理论上不会到达这里，因为只处理 FILE_TYPES 中的文件
                logging.warning(f"文件未匹配任何类别，复制到 Others: {file_path}")
                target_folder = os.path.join(TARGET_DIR, 'Others')
                os.makedirs(target_folder, exist_ok=True)
                target_path = os.path.join(target_folder, filename)
                target_path = self.get_unique_path(target_path)
                shutil.copy2(file_path, target_path)
                logging.info(f"复制: {filename} 到 Others/")
        except FileNotFoundError:
            logging.error(f"文件未找到: {file_path}")
        except Exception as e:
            logging.error(f"复制文件时出错 {file_path}: {e}")

    def get_unique_path(self, path):
        """如果目标路径存在，则在文件名后添加数字以避免冲突"""
        base, extension = os.path.splitext(path)
        counter = 1
        unique_path = path
        while os.path.exists(unique_path):
            unique_path = f"{base}({counter}){extension}"
            counter += 1
        return unique_path

def main():
    event_handler = DownloadEventHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOAD_DIR, recursive=False)
    observer.start()
    logging.info(f"开始监控 {DOWNLOAD_DIR} 目录中的新文件和移动事件...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("停止监控。")
    observer.join()

if __name__ == "__main__":
    main()
