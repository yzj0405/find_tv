import concurrent.futures
import re
import threading
import time
from queue import Queue

import eventlet
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options

eventlet.monkey_patch()

# 页面接口列表
web_urls = [
    # Hebei (河北)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iSGViZWki&page=1&page_size=20",
    # Beijing (北京)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iYmVpamluZyI%3D&page=1&page_size=20",
    # Guangdong (广东)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iZ3Vhbmdkb25nIg%3D%3D&page=1&page_size=20",
    # Shanghai (上海)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbmdoYWki&page=1&page_size=20",
    # Tianjin (天津)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0idGlhbmppbiI%3D&page=1&page_size=20",
    # Chongqing (重庆)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iY2hvbmdxaW5nIg%3D%3D&page=1&page_size=20",
    # Shanxi (山西)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2hhbnhpIg%3D%3D&page=1&page_size=20",
    # Shaanxi (陕西)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iU2hhYW54aSI%3D&page=1&page_size=20",
    # Liaoning (辽宁)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ibGlhb25pbmci&page=1&page_size=20",
    # Jiangsu (江苏)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iamlhbmdzdSI%3D&page=1&page_size=20",
    # Zhejiang (浙江)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iemhlamlhbmci&page=1&page_size=20",
    # Anhui (安徽)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5a6J5b69Ig%3D%3D&page=1&page_size=20",
    # 福建
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iRnVqaWFuIg%3D%3D&page=1&page_size=20",
    # 江西
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rGf6KW%2FIg%3D%3D&page=1&page_size=20",
    # 山东
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5bGx5LicIg%3D%3D&page=1&page_size=20",
    # 河南
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5Y2XIg%3D%3D&page=1&page_size=20",
    # 湖北
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5YyXIg%3D%3D&page=1&page_size=20",
    # 湖南
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rmW5Y2XIg%3D%3D&page=1&page_size=20",
    # 河北
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hebei%22",
    # 北京
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22beijing%22",
    # 广东
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22guangdong%22",
    # 上海
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanghai%22",
    # 天津
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22tianjin%22",
    # 重庆
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22chongqing%22",
    # 山西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shanxi%22",
    # 陕西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shaanxi%22",
    # 辽宁
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22liaoning%22",
    # 江苏
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangsu%22",
    # 浙江
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22zhejiang%22",
    # 安徽
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22anhui%22",
    # 福建
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22fujian%22",
    # 江西
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22jiangxi%22",
    # 山东
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22shandong%22",
    # 河南
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22henan%22",
    # 湖北
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hubei%22",
    # 湖南
    "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hunan%22"
]

# 规则映射
rule = {
    "cctv": "CCTV",
    "中央": "CCTV",
    "央视": "CCTV",
    "高清": "",
    "超高": "",
    "HD": "",
    "标清": "",
    "频道": "",
    "-": "",
    " ": "",
    "PLUS": "+",
    "＋": "+",
    "(": "",
    ")": "",
    "CCTV1综合": "CCTV1",
    "CCTV2财经": "CCTV2",
    "CCTV3综艺": "CCTV3",
    "CCTV4国际": "CCTV4",
    "CCTV4中文国际": "CCTV4",
    "CCTV4欧洲": "CCTV4",
    "CCTV5体育": "CCTV5",
    "CCTV6电影": "CCTV6",
    "CCTV7军事": "CCTV7",
    "CCTV7军农": "CCTV7",
    "CCTV7农业": "CCTV7",
    "CCTV7国防军事": "CCTV7",
    "CCTV8电视剧": "CCTV8",
    "CCTV9记录": "CCTV9",
    "CCTV9纪录": "CCTV9",
    "CCTV10科教": "CCTV10",
    "CCTV11戏曲": "CCTV11",
    "CCTV12社会与法": "CCTV12",
    "CCTV13新闻": "CCTV13",
    "CCTV新闻": "CCTV13",
    "CCTV14少儿": "CCTV14",
    "CCTV15音乐": "CCTV15",
    "CCTV16奥林匹克": "CCTV16",
    "CCTV17农业农村": "CCTV17",
    "CCTV17农业": "CCTV17",
    "CCTV5+体育赛视": "CCTV5+",
    "CCTV5+体育赛事": "CCTV5+",
    "CCTV5+体育": "CCTV5+",
}

# 定义返回结果
results = []
# 错误的数据
error_channels = []


# 查找所有的tv列表
def find_all_tv_list(source_url=None):
    if source_url is None:
        source_url = web_urls

    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 创建驱动
    driver = webdriver.Chrome(options=chrome_options)
    # 设置超时时间为10秒
    driver.set_page_load_timeout(10)
    # 定义IP列表
    ip_port_set = set()
    # 设置匹配IP和端口号的正则
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    # 打开文件并读取内容
    with open('./data/test.html', 'r', encoding="utf-8") as file:
        file_content = file.read()
    # 通过webDriver查找所有的符合格式的网址
    for web_url in source_url:
        try:
            # 使用 get 方法加载网页，如果加载时间超过10秒则会抛出 TimeoutException 异常
            driver.get(web_url)
            # 获取网页内容
            time.sleep(10)
            page_content = driver.page_source
            # FIXME:测试本地数据,减少页面访问次数
            # page_content = file_content
            # 查找符合条件：IP:PORT的数据
            urls_all = re.findall(pattern, page_content)
            # 替换IP最后一位为1并去重
            ip_port_set = ip_port_set.union(set(replace_last_octet_with_list(urls_all)))
        except TimeoutException:
            print("页面加载超时，进行相应处理")
            continue
    # 关闭WebDriver
    driver.quit()
    # 多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for ip_port in ip_port_set:
            ip_port = ip_port.strip()
            modified_urls = modify_urls(ip_port)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))
    # 节目列表
    task_queue = Queue()
    # 遍历所有的原始数据
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            # 解析JSON文件，获取name和url字段
            for item in result["json_data"]['data']:
                if isinstance(item, dict):
                    name = item.get('name')
                    urlx = item.get('url')
                    if name and urlx:
                        # if 'http' in urlx or 'udp' in urlx or 'rtp' in urlx:
                        if urlx.startswith("http"):
                            urld = f"{urlx}"
                        else:
                            urld = result["ip"] + urlx
                        # 删除特定文字
                        for key, value in rule.items():
                            name = name.replace(key, value)
                        name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                        task_queue.put({"name": name, "url": urld})
    # 创建线程组，获取执行状态数据
    create_work_threads(task_queue)
    # 排序
    results.sort(key=lambda x: (x[0], -float(x[2].split()[0])))
    results.sort(key=lambda x: channel_key(x[0]))
    print(f"输出结果：{results}")
    # 保存到文件中
    save_tv_to_file()


def save_tv_to_file(result_counter=8):
    with open("./data/new_itvlist.txt", 'w', encoding='utf-8') as file:
        channel_counters = {}
        file.write('央视频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if 'CCTV' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        file.write('卫视频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if '卫视' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        file.write('其他频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"{channel_name},{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] = 1

    with open("./data/new_itvlist.m3u", 'w', encoding='utf-8') as file:
        channel_counters = {}
        file.write('#EXTM3U\n')
        for result in results:
            channel_name, channel_url, speed = result
            if 'CCTV' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                        file.write(f"{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        # file.write('卫视频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if '卫视' in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                        file.write(f"{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] = 1
        channel_counters = {}
        # file.write('其他频道,#genre#\n')
        for result in results:
            channel_name, channel_url, speed = result
            if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
                if channel_name in channel_counters:
                    if channel_counters[channel_name] >= result_counter:
                        continue
                    else:
                        file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                        file.write(f"{channel_url}\n")
                        channel_counters[channel_name] += 1
                else:
                    file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] = 1


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无


# 创建work线程
def create_work_threads(task_queue, num_threads=10):
    for _ in range(min(num_threads, task_queue.qsize())):
        t = threading.Thread(target=worker, args=(task_queue,), daemon=True)  # 将工作线程设置为守护线程
        t.start()
    # 等待所有任务完成
    task_queue.join()


# 定义工作线程函数
def worker(task_queue):
    while True:
        # 从队列中获取一个任务
        source_url = task_queue.get()
        process_channel(source_url["name"], source_url["url"])
        # 标记任务完成
        task_queue.task_done()


# 处理数据
def process_channel(channel_name, channel_url):
    try:
        # FIXME:采用m3u8的模式,目前只能确保数据有效,
        # m3u8_obj = m3u8.load(channel_url)
        # if m3u8_obj is not None:
        #     if m3u8_obj.keys[0] is None:
        #         result = channel_name, channel_url
        #         results.append(result)
        #     else:
        #         process_error_channel(channel_name, channel_url)

        response = requests.get(channel_url, timeout=2)
        if response.status_code == 200:
            process_valid_channel(channel_name, channel_url, response.text.strip().split('\n'))
        else:
            process_error_channel(channel_name, channel_url)
    except:
        process_error_channel(channel_name, channel_url)


def process_valid_channel(channel_name, channel_url, lines):
    # m3u8链接前缀
    channel_url_t = channel_url.rstrip(channel_url.split('/')[-1])
    # 获取m3u8文件下视频流后缀
    ts_lists = [line.split('/')[-1] for line in lines if line.startswith('#') == False]

    file_size = 0
    start_time = time.time()
    # 对获取的视频数据进行5秒钟限制
    with eventlet.Timeout(10, False):
        for i in range(len(ts_lists)):
            ts_url = channel_url_t + ts_lists[i]  # 拼接单个视频片段下载链接
            response = requests.get(ts_url, stream=True, timeout=1)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file_size += len(chunk)
            response.close()
    end_time = time.time()
    response_time = end_time - start_time
    normalized_speed = file_size / response_time / 1024 / 1024  # 将速率从B/s转换为MB/s
    if normalized_speed >= 0.5:
        result = channel_name, channel_url, f"{normalized_speed:.3f} MB/s"
        results.append(result)
        print_summary()
    else:
        error_channel = channel_name, channel_url
        error_channels.append(error_channel)
        print_summary()


# 错误数据
def process_error_channel(channel_name, channel_url):
    error_channel = (channel_name, channel_url)
    error_channels.append(error_channel)
    print_summary()


# 打印输出
def print_summary():
    print(f"可用频道：{len(results)} 个 , 不可用频道：{len(error_channels)} 个")


# URL合理性校验并获取返回值
def is_url_accessible(ip_port):
    try:
        url = ip_port + "/iptv/live/1000.json?key=txiptv"
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            json_data = response.json()
            return {"ip": ip_port, "url": url, "json_data": json_data}
    except requests.exceptions.RequestException:
        pass
    return None


# 批量替换IP地址的最后一段为1
def replace_last_octet_with_list(ip_addresses):
    return [re.sub(r'\d+\.\d+\.\d+\.\d+', lambda x: replace_last_octet_with_one(x.group()), ip) for ip
            in ip_addresses]


# 单个替换IP地址的最后一段为1
def replace_last_octet_with_one(ip_address, replacement=1):
    octets = ip_address.split('.')
    octets[-1] = str(replacement)
    return '.'.join(octets)


# 生成255个IP
def modify_urls(ip_address):
    return [re.sub(r'\d+\.\d+\.\d+\.\d+', lambda x: replace_last_octet_with_one(x.group(), i), ip_address) for
            i
            in
            range(1, 255)]


# 入口方法
if __name__ == "__main__":
    print(f"开始解析数据")
    # 解决跨域问题
    find_all_tv_list()
