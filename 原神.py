import requests
from bs4 import BeautifulSoup
import pyautogui
import cv2
import numpy as np
import time
import logging

# 定义全局的日志配置
logging.basicConfig(level=logging.INFO, filename='error.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

def search_game_guide(game_name):
    """
    使用网络搜索游戏攻略并获取其页面内容
    :param game_name: 游戏名称
    :return: 攻略链接
    """
    search_url = f"https://www.google.com/search?q={game_name}+攻略"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)  # 设置超时时间为 10 秒
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)

            # 简单查找第一个有效链接
            for link in links:
                if 'http' in link['href']:
                    logging.info(f"找到攻略链接: {link['href']}")
                    return link['href']
        else:
            logging.error("攻略查找失败，状态码: %s", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        logging.error("搜索攻略时发生错误: %s", e)
        return None

def extract_guide_content(guide_url):
    """
    提取攻略页面的主要内容
    :param guide_url: 攻略链接
    :return: 攻略内容文本
    """
    try:
        response = requests.get(guide_url, timeout=10)  # 设置超时时间为 10 秒
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 假设攻略内容在 <p> 标签中，实际情况需要根据具体攻略页面结构调整
            paragraphs = soup.find_all('p')
            guide_content = "\n".join([p.get_text() for p in paragraphs])

            return guide_content
        else:
            logging.error("无法访问攻略页面，状态码: %s", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        logging.error("获取攻略内容时发生错误: %s", e)
        return None

def execute_guide_actions(guide_content):
    """
    基于攻略内容执行操作
    :param guide_content: 攻略文本内容
    """
    # 简单示例：假设攻略中提到的“点击开始游戏”需要执行相应的点击操作
    if "点击开始游戏" in guide_content:
        logging.info("检测到‘开始游戏’操作，正在执行...")
        click_image('start_game_button.png')  # 假设已准备好模板图像
    else:
        logging.warning("未识别到有效操作指令。")

def click_image(image_path, threshold=0.8):
    """
    找到图像后点击该图像位置
    :param image_path: 要查找并点击的图像路径
    :param threshold: 模板匹配的相似度阈值
    """
    pos = find_image_on_screen(image_path, threshold)
    if pos:
        max_loc, w, h = pos
        center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2
        pyautogui.moveTo(center_x, center_y)
        pyautogui.click()
        logging.info(f"点击位置: ({center_x}, {center_y})")
    else:
        logging.warning("未找到目标图像。")

def find_image_on_screen(image_path, threshold=0.8):
    """
    在屏幕上查找目标图像，返回位置坐标
    :param image_path: 模板图像的路径
    :param threshold: 模板匹配的相似度阈值
    :return: 返回找到的图像位置（左上角坐标和宽高）
    """
    try:
        screen = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            return max_loc, template.shape[1], template.shape[0]  # 返回位置和模板的宽高
        else:
            return None
    except cv2.error as e:
        logging.error("图像处理时发生错误: %s", e)
        return None

def main():
    # 示例：从用户输入游戏名称
    game_name = input("请输入游戏名称：")

    # 步骤 1: 查找游戏攻略
    game_guide_url = search_game_guide(game_name)

    # 步骤 2: 解析攻略内容
    if game_guide_url:
        guide_content = extract_guide_content(game_guide_url)
        if guide_content:
            logging.info(f"攻略内容:\n{guide_content}")

            # 步骤 3: 基于攻略内容执行操作
            execute_guide_actions(guide_content)
        else:
            logging.error("未能获取攻略内容。")
    else:
        logging.error("未找到攻略链接。")

if __name__ == "__main__":
    main()
