import time
import threading
import win32pipe, win32file


class ConnectNamedPipe:
    def __init__(self):
        self.pipe_name =  r'\\.\pipe\ColorDetectionPipe'

    def create_pipe(self):
        pipe = win32pipe.CreateNamedPipe(
            self.pipe_name,
            win32pipe.PIPE_ACCESS_OUTBOUND,  # โหมดเขียน
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536, 0, None
        )
        return pipe

    def connect_named_pipe(self, pipe):
        print(f"Pipe ถูกสร้างแล้ว รอการเชื่อมต่อ...")
        win32pipe.ConnectNamedPipe(pipe, None)  # รอให้ AutoIt เชื่อมต่อ
        print("Client เชื่อมต่อสำเร็จ!")

    def send_data(self, pipe, msg):
        data_bytes = msg.encode("utf-8") + b"\x00"  # Null Terminator
        win32file.WriteFile(pipe, data_bytes)
        win32file.FlushFileBuffers(pipe)  # บังคับให้ส่งข้อมูลออกไปทันที
