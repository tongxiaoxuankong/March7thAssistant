from managers.screen_manager import screen
from managers.config_manager import config
from managers.logger_manager import logger
from managers.automation_manager import auto
from managers.translate_manager import _
from tasks.base.base import Base
from tasks.base.pythonchecker import PythonChecker
from tasks.base.runsubprocess import RunSubprocess
import zipfile
import requests
import shutil
import os


class Universe:
    @staticmethod
    def start(get_reward=False):
        logger.hr(_("准备模拟宇宙"), 2)

        if PythonChecker.run(config.python_path):
            python_path = os.path.abspath(config.python_path)

            if not os.path.exists(config.universe_path):
                logger.error(_("模拟宇宙路径不存在: {path}").format(path=config.universe_path))
                if not Universe.update():
                    Base.send_notification_with_screenshot(_("⚠️模拟宇宙未完成⚠️"))
                    return False

            screen.change_to('universe_main')
            screen.change_to('main')

            logger.info(_("开始安装依赖"))
            if RunSubprocess.run(f"cd {config.universe_path} && {python_path}\\Scripts\\pip.exe install -i {config.pip_mirror} -r requirements.txt --no-warn-script-location", 3600):
                logger.info(_("开始校准"))
                if RunSubprocess.run(f"cd {config.universe_path} && {python_path}\\python.exe align_angle.py", 60):
                    logger.info(_("开始模拟宇宙"))
                    if RunSubprocess.run(f"cd {config.universe_path} && {python_path}\\python.exe states.py" + (" --bonus=1" if config.universe_bonus_enable else ""), config.universe_timeout * 3600):
                        config.save_timestamp("universe_timestamp")
                        if get_reward:
                            Universe.get_reward()
                        else:
                            Base.send_notification_with_screenshot(_("🎉模拟宇宙已完成🎉"))
                        return
                    else:
                        logger.info(_("模拟宇宙失败"))
                else:
                    logger.info(_("校准失败"))
            else:
                logger.info(_("依赖安装失败"))
        Base.send_notification_with_screenshot(_("⚠️模拟宇宙未完成⚠️"))

    @staticmethod
    def get_reward():
        logger.info(_("开始领取奖励"))
        screen.change_to('universe_main')
        if auto.click_element("./assets/images/universe/universe_reward.png", "image", 0.9):
            if auto.click_element("./assets/images/universe/one_key_receive.png", "image", 0.9, max_retries=10):
                if auto.find_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10):
                    Base.send_notification_with_screenshot(_("🎉模拟宇宙奖励已领取🎉"))
                    auto.click_element("./assets/images/base/click_close.png", "image", 0.9, max_retries=10)

    @staticmethod
    def update():
        url = f"{config.github_mirror}https://github.com/CHNZYX/Auto_Simulated_Universe/archive/main.zip"
        destination = '.\\3rdparty\\Auto_Simulated_Universe.zip'
        extracted_folder_path = '.\\3rdparty'

        logger.info(_("开始下载：{url}").format(url=url))
        response = requests.get(url)
        if response.status_code == 200:
            with open(destination, 'wb') as file:
                file.write(response.content)
                logger.info(_("下载完成：{destination}").format(destination=destination))
        else:
            logger.error(_("下载失败：{code}").format(code=response.status_code))
            return False

        with zipfile.ZipFile(destination, 'r') as zip_ref:
            zip_ref.extractall(extracted_folder_path)
        logger.info(_("解压完成：{path}").format(path=extracted_folder_path))

        folder = '.\\3rdparty\\Auto_Simulated_Universe-main'
        Universe.copy_and_replace_folder_contents(config.universe_path, folder)
        logger.info(_("更新完成：{path}").format(path=config.universe_path))

        os.remove(destination)
        shutil.rmtree(folder)
        logger.info(_("清理完成：{path}").format(path=destination))

    @staticmethod
    def copy_and_replace_folder_contents(folder_a, folder_b):
        # 复制文件夹B中的所有文件到文件夹A，直接覆盖同名文件
        for item in os.listdir(folder_b):
            source = os.path.join(folder_b, item)
            destination = os.path.join(folder_a, item)

            # 如果文件夹A中已经存在同名文件，就删除它
            if os.path.exists(destination):
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)

            # 复制文件或文件夹，直接覆盖同名文件
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
