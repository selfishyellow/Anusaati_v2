import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.forest_parser import ForestParser

def test_parser():
    parser = ForestParser()
    
    test_cases = [
        {
            "name": "English - Standard",
            "text": "Time to put down your phone and get back to work!\nEnter my room code: 5AA76VZSG to plant a 180-minute Cuckoo Clock with me!\nYou can also tap on this link to join me: https://forestapp.cc/join-room?token=5AA76VZSG",
            "expected_code": "5AA76VZSG",
            "expected_plant": "Cuckoo Clock",
            "expected_duration": 180
        },
        {
            "name": "Chinese - Standard",
            "text": "放下手机，专注工作吧！\n输入我的房间代码：5AA76VZSG，跟我一起种下 120 分钟的 咕咕钟 吧！\n也可以点击此链接加入我：https://forestapp.cc/join-room?token=5AA76VZSG",
            "expected_code": "5AA76VZSG",
            "expected_plant": "咕咕钟",
            "expected_duration": 120
        }
    ]

    for case in test_cases:
        result = parser.parse_message(case["text"])
        print(f"Testing: {case['name']}")
        if result:
            print(f"  Parsed Code: {result['room_code']} (Match: {result['room_code'] == case['expected_code']})")
            print(f"  Parsed Plant: {result['plant_name']} (Match: {result['plant_name'] == case['expected_plant']})")
            print(f"  Parsed Duration: {result['duration']} (Match: {result['duration'] == case['expected_duration']})")
        else:
            print("  Failed to parse!")
        print("-" * 20)

if __name__ == "__main__":
    test_parser()
