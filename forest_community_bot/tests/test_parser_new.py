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
            "name": "French - Standard",
            "text": "Il est temps de poser votre téléphone et de vous remettre au travail !\nEntrez mon code de salle : 5AA76VZSG pour planter un Cuckoo Clock de 180 minutes avec moi !\nVous pouvez également appuyer sur ce lien pour me rejoindre : https://forestapp.cc/join-room?token=5AA76VZSG",
            "expected_code": "5AA76VZSG",
            "expected_plant": "Cuckoo Clock",
            "expected_duration": 180
        },
        {
            "name": "Korean - Standard",
            "text": "휴대폰을 내려놓고 업무에 복귀할 시간입니다!\n나와 함께 180분 동안 Cuckoo Clock을(를) 심으려면 방 코드: 5AA76VZSG을(를) 입력하세요!\n이 링크를 눌러 가입할 수도 있습니다: https://forestapp.cc/join-room?token=5AA76VZSG",
            "expected_code": "5AA76VZSG",
            "expected_plant": "Cuckoo Clock",
            "expected_duration": 180
        }
    ]

    for case in test_cases:
        result = parser.parse_message(case["text"])
        print(f"Testing: {case['name']}")
        if result:
            print(f"  Parsed Code: {result['room_code']} (Match: {result['room_code'] == case['expected_code']})")
            print(f"  Parsed Plant: {result['plant_name']} (Match: {result['plant_name'] == case['expected_plant']})")
            print(f"  Parsed Duration: {result['duration']} (Match: {result['duration'] == case['expected_duration']})")
            print(f"  Language: {result['language']}")
        else:
            print("  Failed to parse!")
        print("-" * 20)

if __name__ == "__main__":
    test_parser()
