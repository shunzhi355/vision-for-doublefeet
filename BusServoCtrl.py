
import time
from pyb import UART

# 初始化串口（全局初始化一次即可）
uart = UART(3, 9600)

def send_servo_commands(time_ms, angle):
    """
    发送舵机控制命令函数
    :param time_ms: 转动时间（毫秒）
    :param angle: 转动角度（0-1000）
    :param servo_id: 舵机ID（十进制，将直接作为数据帧中的字节）
    """
    # 将输入的十进制变量转换为十六进制（低八位在前，高八位在后）
    # 处理转动时间
    time_low = time_ms & 0xFF
    time_high = time_ms >> 8
    # 处理转动角度
    angle_low = angle & 0xFF
    angle_high = angle >> 8

    # 构造data1（使用外部传入的变量）
    data1 = bytearray([
        0x55, 0x55,       # 帧头
        0x11,             # 有效数据位起始标志
        0x03,             # 固定执行命令
        0x02,             # 固定值舵机数量
        time_low, time_high,  # 转动时间的十六进制（低八位在前）
        #servo_id,         # 舵机ID（直接使用传入的十进制值作为字节）
        0X01,
        angle_low, angle_high,  # 转动角度的十六进制（低八位在前）
        0X05,
        angle_low, angle_high
    ])

    # data2保持不变
    data2 = bytearray([0x55, 0x55, 0x11, 0x03, 0x02, time_low, time_high, 0x01, 0xF4, 0x01, 0x05, 0xF4, 0x01])

    # 发送data1两次，间隔1秒
    for _ in range(2):
        uart.write(data1)
        print(f"发送data1（时间：{time_ms}ms，角度：{angle}，舵机ID：01,05）:", 
              [hex(b) for b in data1])
        time.sleep(0.5)

    # # data1发送完成后，间隔time_ms秒再发送data2
    # print(f"等待{time_ms}秒后发送data2...")
    # time.sleep(time_ms)

    # 等待 (time_ms 毫秒 + 50 毫秒)，转换为秒后传入 sleep
    #wait_time = (time_ms + 50) / 1000.0  # 单位：秒
    print(f"等待1秒后发送data2...")
    time.sleep(0.2)

    # 发送data2两次，间隔1秒
    for _ in range(2):
        uart.write(data2)
        print("发送data2:", [hex(b) for b in data2])
        time.sleep(0.5)

    print("本轮发送完成")


# 示例调用：
# send_servo_commands(转动时间, 转动角度, 舵机ID)
# send_servo_commands(1000, 550, 0x01)  # 时间1000ms，角度550，舵机ID为0x01
# send_servo_commands(800, 300, 0x02)   # 时间800ms，角度300，舵机ID为0x02