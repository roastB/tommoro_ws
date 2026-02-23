# conveyor.py
import serial
import serial.tools.list_ports
import time

# 🧩 [주석] 실제 하드웨어 제어 로직이 들어가는 클래스입니다.
# 🧩 기존에 사용하시던 conveyor.py 파일이 있다면 그 내용을 그대로 사용하세요.

class ConveyorController:
    def __init__(self, port_config={'a': None}):
        """
        초기화 함수
        port_config: {'a': 'COM3'} 등의 포트 설정 딕셔너리
        """
        self.conveyor = {}
        self.port_config = port_config
        self._connect()

    def _connect(self):
        """
        [내부 함수] 시리얼 포트 연결 로직
        (기존 코드의 연결 로직을 이곳에 구현)
        """
        # 🧩 예시: 포트가 None이면 오토 디텍팅하거나 설정된 포트로 연결
        # 실제 구현에서는 serial.Serial 객체를 self.conveyor에 할당해야 합니다.
        
        # [MOCK] 테스트를 위한 더미 객체 (실제 하드웨어 연결 시 삭제/수정 필요)
        for key, port in self.port_config.items():
            # 실제로는 serial.Serial(...) 연결
            self.conveyor[key] = MockSerialDevice(port or "AUTO_DETECTED_PORT")

    def command(self, belt_id, direction=None, speed=None):
        """
        컨베이어 동작 명령 함수
        """
        if belt_id not in self.conveyor:
            print(f"Error: {belt_id} not found.")
            return

        # 🧩 [구현 필요] 실제 하드웨어로 바이트(byte) 명령어를 전송하는 로직
        # 예: self.conveyor[belt_id].write(b'...')
        
        cmd_str = f"Belt: {belt_id}"
        if direction:
            cmd_str += f", Dir: {direction}"
        if speed:
            cmd_str += f", Speed: {speed}"
        
        # 디버깅용 출력
        # print(f"[Hardware Command] {cmd_str}")

# 🧩 [MOCK] 대시보드 에러 방지용 더미 클래스 (실제 파일에선 필요 없음)
class MockSerialDevice:
    def __init__(self, port_name):
        self.ser = type('', (), {})() # empty object
        self.ser.port = port_name
    
    def write(self, data):
        pass