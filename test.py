import requests
import m3u8

def check_m3u8(url):
    # 发送请求获取M3U8内容
    r = requests.get(url)
    m3u8_content = r.text

    # 解析M3U8内容
    m3u8_obj = m3u8.loads(m3u8_content)

    # 判断是否可用
    if m3u8_obj.playlists:
        print("M3U8链接可用")

        # 获取视频码率等信息
        for playlist in m3u8_obj.playlists:
            resolution = playlist.stream_info.resolution
            bitrate = playlist.stream_info.bandwidth
            print(f"Resolution: {resolution}, Bitrate: {bitrate}")
    else:
        print("M3U8链接不可用")

# 测试链接
url = "http://123.163.114.5:85/tsfile/live/0001_1.m3u8"
check_m3u8(url)
