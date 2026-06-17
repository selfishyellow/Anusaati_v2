import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.forest_parser import ForestParser

def test_parser():
    parser = ForestParser()
    
    text_en = "Time to put down your phone and get back to work!\nEnter my room code: 5AA76VZSG to plant a 180-minute Cuckoo Clock with me!\nYou can also tap on this link to join me: https://forestapp.cc/join-room?token=5AA76VZSG"
    text_zh = "放下手机，专注工作吧！\n输入我的房间代码：5AA76VZSG，跟我一起种下 120 分钟的 咕咕钟 吧！\n也可以点击此链接加入我：https://forestapp.cc/join-room?token=5AA76VZSG"

    print(f"Keywords in zh text: {[kw for kw in parser.parsers[1].invite_keywords if kw in text_zh]}")
    
    result = parser.parse_message(text_zh)
    print(f"Result: {result}")

if __name__ == "__main__":
    test_parser()
