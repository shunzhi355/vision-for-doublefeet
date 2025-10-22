import pyb, sensor, image, math, time
from pyb import UART
from image import SEARCH_EX, SEARCH_DS

from BusServoCtrl import send_servo_commands  # 从BusServoCtrl模块导入函数

# 定义ROI区域
roi1 = [
    (15,10, 10, 100),
    (45, 10, 10, 100),
    (75, 10, 10, 100),
    (105, 10, 10, 100),
    (130, 10, 10, 100),
]

# 初始化LED和传感器
led = pyb.LED(1)
led.on()

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # 灰度模式
sensor.set_framesize(sensor.QQVGA)     # 80x60分辨率
# sensor.set_vflip(True)               # 如需镜像/翻转可开启
# sensor.set_hmirror(True)
sensor.skip_frames(time=2000)          # 传感器预热
sensor.set_auto_whitebal(True)
sensor.set_auto_gain(False)

# 地面阈值（灰度模式，只检测亮度范围）
GROUND_THRESHOLD = (0, 30)

# 帧率计算变量
clock = time.clock()

# 防止重复发送的标志（可选，避免短时间内重复触发）
last_command_time = 0
COMMAND_INTERVAL = 2000  # 命令间隔（毫秒），避免频繁发送

while True:
    clock.tick()
    flag = [0, 0, 0, 0, 0]  # 5个ROI的检测结果（1表示检测到地面，0表示未检测到）
    img = sensor.snapshot().lens_corr(strength=1.7, zoom=1.0)
    
    # 检测各ROI区域
    for i in range(5):
        blobs = img.find_blobs([GROUND_THRESHOLD], roi=roi1[i])
        if blobs:  # 如果检测到符合阈值的区域
            flag[i] = 1
    
    # 打印当前检测结果
    current_flag = tuple(flag)
    print("检测结果:", current_flag)
    
    # 绘制ROI区域（红色矩形）
    for rec in roi1:
        img.draw_rectangle(rec, color=255)  # 灰度模式下255为白色
    
    # 显示帧率
    img.draw_string(
        img.width() - 40, 0,
        f"{clock.fps():.1f}",
        color=255,
        scale=1
    )
    
    # 判断偏航状态并发送舵机命令（加入时间间隔防止重复发送）
    current_time = time.ticks_ms()
    if current_time - last_command_time > COMMAND_INTERVAL:
        # 右偏模式：10000 或 11000
        if current_flag in [(1,0,0,0,0), (1,1,0,0,0),(1,1,1,0,0),(0,1,0,0,0)]:
            print("检测到右偏，发送右偏校正命令...")
            send_servo_commands(300, 450)  # 舵机ID=01，时间500ms，角度450
            last_command_time = current_time       # 更新最后发送时间
        
        # 左偏模式：00001 或 00011
        elif current_flag in [(0,0,0,0,1), (0,0,0,1,1),(0,0,1,1,1),(0,0,0,1,0)]:
            print("检测到左偏，发送左偏校正命令...")
            send_servo_commands(300, 540)  # 舵机ID=05，时间500ms，角度540
            last_command_time = current_time       # 更新最后发送时间