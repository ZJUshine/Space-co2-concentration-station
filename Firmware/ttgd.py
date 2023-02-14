# 树莓派GPS+CO2
#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time
import mh_z19
import csv
import RTrobot_FS3000
import sys

ser = serial.Serial('/dev/ttyUSB0',115200)
ser.flushInput()
tmf = RTrobot_FS3000.RTrobot_FS3000()

power_key = 6
rec_buff = ''

#############################################################
pin = 21 # 这里填写GPIO号（BCM引脚编号模式）    手动改变此行
#############################################################

GPIO.setmode(GPIO.BCM)  # 设置使用BCM引脚编号模式

def getdht11data(pin):
    GPIO.setup(pin,GPIO.OUT)  # 設置引腳輸出
    GPIO.output(pin,True)  # 高电平

    # 树莓派下拉19ms
    GPIO.output(pin,False)
    time.sleep(0.02)
    #GPIO.output(pin,True)

    GPIO.setup(pin,GPIO.IN)  # 设置引腳输入

    time_data_list = []  # 保存数据（高电平持续）时间的列表

    pan_duan = 1  #判断数据是否正确

    end_times = 0  # 数据是否接收完毕 决定是否结束大循环
    start_time = 0  # 防止start_time未定义
    end_time = 0  # 防止end_time未定义
    while 1:
        start_time_total = time.time()  # 记录每次运行循环开始时间

        if end_times == 1: # 数据接收完毕
            break

        while GPIO.input(pin) == 0:  # 等待电平不为低
            start_time = time.time()  # 得到高电平开始时间
            if (start_time - start_time_total) > 0.1 :  # 判断循环时间过长 电平已经不再变化
                end_times = 1
                break

        while GPIO.input(pin) == 1:  # 等待电平不为高
            end_time = time.time()  # 得到高电平结束时间
            if (end_time - start_time_total) > 0.1 :  # 判断循环时间过长 电平已经不再变化
                end_times = 1
                break

        time_data = end_time - start_time  # 计算出高电平持续时间

        time_data_list.append(time_data)  # 高电平持续时间数据写入列表
        # print(str(time_data)+',   ', end='')

    # print(time_data_list)
    # print(len(time_data_list))

    new_time_data_list = []  # 保存筛选过的时间

    for i in range(len(time_data_list)):
        if (time_data_list[i] > 1.9e-5 ) and (time_data_list[i] < 7.8e-5):
            new_time_data_list.append(time_data_list[i])

    #print(new_time_data_list)
    #print(len(new_time_data_list))

    if len(new_time_data_list) != 40:
        pan_duan = 0  #判断数据是否正确
        return 0, '接收到的数据位数不足，请重新尝试'


    if pan_duan == 1:  #判断数据是否正确
        Binary_list = []  # 保存二进制数据
        for i in new_time_data_list:
            if i > 5.0e-5 :
                Binary_list.append(1)
            elif i < 5.0e-5 :
                Binary_list.append(0)
        if len(Binary_list) != 40 :
            pan_duan = 0  #判断数据是否正确
            return 0, '数据位数不足，请重新尝试'

        #print(Binary_list)
        #print(len(Binary_list))


    if pan_duan == 1:  #判断数据是否正确
    # 转字符串格式
        str_Binary_list = []
        for i in Binary_list:
            str_Binary_list.append(str(i))


    if pan_duan == 1:  #判断数据是否正确

        # 分割数据 并合并成字符串
        # 共40位数据 0-8为湿度整数 9-16为湿度小数 17-24为温度整数 25-32为湿度小数 33-40为校验和（前四个数据直接相加）
        str_shidu_zhengshu = ''.join(str_Binary_list[0:8])
        str_shidu_xiaoshu = ''.join(str_Binary_list[8:16])
        str_wendu_zhengshu = ''.join(str_Binary_list[16:24])
        str_wendu_xiaoshu = ''.join(str_Binary_list[24:32])
        str_yanzheng = ''.join(str_Binary_list[32:40])

        # 转换为十进制
        int_shidu_zhengshu = int(str_shidu_zhengshu,2)
        int_shidu_xiaoshu = int(str_shidu_xiaoshu,2)
        int_wendu_zhengshu = int(str_wendu_zhengshu,2)
        int_wendu_xiaoshu = int(str_wendu_xiaoshu,2)
        int_yanzheng = int(str_yanzheng,2)

        if int_yanzheng != (int_shidu_zhengshu + int_shidu_xiaoshu + int_wendu_zhengshu + int_wendu_xiaoshu):
            pan_duan = 0  # 数据不正确
            return 0, '校验和不匹配，请重新尝试'

        if int_yanzheng == (int_shidu_zhengshu + int_shidu_xiaoshu + int_wendu_zhengshu + int_wendu_xiaoshu):
            pan_duan = 1  # 数据正确
            str_shidu = str(int_shidu_zhengshu) + '.' + str(int_shidu_xiaoshu)
            str_wendu = str(int_wendu_zhengshu) + '.' + str(int_wendu_xiaoshu)
            float_shidu = float(str_shidu)
            float_wendu = float(str_wendu)
            return 1, (float_shidu, float_wendu)  # 返回 湿度 温度

def dht11():  # 循环五次
    for i in range(5):
        pan_duan_01, return_data = getdht11data(pin)
        if pan_duan_01 == 1:
            return return_data
        time.sleep(0.5)
    print('错误')
    return return_data, return_data

# 开启SIM7600X模块--设定启动时间20s
def power_on(power_key):
    print('SIM7600X is starting:')
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(power_key,GPIO.OUT)
    time.sleep(0.1)
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(2)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(2)
    ser.flushInput()
    print('SIM7600X is ready')
# 关闭SIM7600X模块--设定关闭时间21s
def power_down(power_key):
    print('SIM7600X is loging off:')
    GPIO.output(power_key,GPIO.HIGH)
    time.sleep(3)
    GPIO.output(power_key,GPIO.LOW)
    time.sleep(18)
    print('Good bye')

# command:AT+CGPSINFO | back:OK | timeout:1
def send_at(command,back,timeout):
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01 )
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
            print(command + ' ERROR')
            print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:
            str_gps=rec_buff.decode()
            # print(rec_buff.decode())
            # if len(str_gps)>50:
            #     print(float(str_gps[25:27])+float(str_gps[27:36])/60)
            #     print(float(str_gps[39:42])+float(str_gps[42:51])/60)
            return 1,rec_buff.decode()
    else:
        print('GPS is not ready')
        return 0

# 获取GPS位置信息
def get_gps_position():
    f = open('data.csv','a',encoding='utf-8')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["gpsinfo","co2","fengsu","wendu","shidu"])
    print('doing get_gps_postion')
    rec_null = True
    answer = 0
    print('Start GPS session...')
    rec_buff = ''
    send_at('AT+CGPS=1,1','OK',1)
    time.sleep(2)
    while rec_null:
        # co2 = mh_z19.read()
        # co2 = co2['co2']
        # print("CO2:",co2)
        speed = tmf.FS3000_ReadData()
        if speed != 0:
            print(str(speed)+" m/s")
        shidu, wendu = dht11()
        print('湿度为' + str(shidu) + '%')
        print('温度为' + str(wendu) + '度')
        answer,gpsdata = send_at('AT+CGPSINFO','+CGPSINFO: ',1)
        gpsdata = gpsdata.split(":")[-1].split()[0]
        print("gpsdata:",gpsdata)
        if 1 == answer:
            answer = 0
            if ',,,,,,' in rec_buff:
                print('GPS is not ready')
                rec_null = False
                time.sleep(1)
        else:
            print('error %d'%answer)
            rec_buff = ''
            send_at('AT+CGPS=0','OK',1)
            return False
        csv_writer.writerow([gpsdata,speed,speed,wendu,shidu])
        time.sleep(1.5)

# 执行程序
try:
    # 开启SIM7600X
    power_on(power_key)
    # 获取GPS位置数据
    get_gps_position()
    # 关闭SIM7600X
    power_down(power_key)
except:
    if ser != None:
        ser.close()
    power_down(power_key)
    GPIO.cleanup()
if ser != None:
        ser.close()
        GPIO.cleanup()