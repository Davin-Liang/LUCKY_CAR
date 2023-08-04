#!/usr/bin/env python3

import os
import time
from playsound import playsound
import random
import rospy
from dynamic_reconfigure.client import Client

def update_teb_params(new_max_vel_x):
    # 使用ROS参数服务器设置新的max_vel_x值
    rospy.set_param('/move_base/TebLocalPlannerROS/max_vel_x', new_max_vel_x)

    # 创建动态重配置的客户端，用于调用TEB导航器的reconfigure服务
    client = Client('/move_base/TebLocalPlannerROS', timeout=30)

    # 构建新的参数字典，用于更新TEB导航器的参数
    teb_params = {'max_vel_x': new_max_vel_x}

    # 调用reconfigure服务来更新TEB导航器的参数
    config = client.update_configuration(teb_params)

def get_full_path(path):
    """ 获取完整语音文件途径"""
    dir = "/home/ucar/ucar_ws/src/ucar_nav/scripts/voice/"
    AP = dir + path + ".wav"
    return AP

def judge_array(array):
    """ 判断返回的列表中的内容 """
    if "rice" in array:
        return "rice"
    if "cucumber" in array:
        return "cucumber"
    if "wheat" in array:
        return "wheat"
    if "corn" in array:
        return "corn"

    if any(element is None for element in array):
        return "lose"

    return "lose"

def quick_jugde(place, labels):
    """ 快速判断 """
    labels.remove(place[0])
    labels.remove(place[1])
    labels.remove(place[2])
    result = labels[0]
    return result

def determine_the_contents_of_all_lists(all_lists):
    all = []
    # 创建一个字典用于存储每种字符串的数量
    string_count = {}

    all = [item for sublist in all_lists for item in sublist]

    # for i in range(len(all_lists)):
    #     for j in range(len(all_lists[i])):
    #         all.append(all_lists[i][j])
    #         print(all)

    # 遍历列表中的每个字符串
    for item in all:
        # 如果字符串不在字典中，则将其添加，并将数量设置为1
        if item not in string_count:
            string_count[item] = 1
        else:
            # 如果字符串已经存在于字典中，则增加其数量
            string_count[item] += 1

    print(all)

    # 找出数量最多的字符串及其数量值
    most_frequent_string = max(string_count, key=string_count.get)
    most_frequent_count = string_count[most_frequent_string]

    return most_frequent_string, most_frequent_count

def playsound_for_num(num):
    if num == 1:
        playsound(get_full_path('数量为1个'))
    if num == 2:
        playsound(get_full_path('数量为2个'))
    if num == 3:
        playsound(get_full_path('数量为3个'))
    if num == 4:
        playsound(get_full_path('数量为4个'))
    if num == 5:
        playsound(get_full_path('数量为5个'))
    if num == 6:
        playsound(get_full_path('数量为6个'))
    if num == 7:
        playsound(get_full_path('数量为7个'))
    if num == 8:
        playsound(get_full_path('数量为8个'))
    if num == 9:
        playsound(get_full_path('数量为9个'))

def prevent_lose(array):
    not_identify = ["corn", "wheat", "cucumber", "rice"]
    for i in range(4):
        if "lose" == array[i]:
            array[i] = random.choice(not_identify)
    return array

def prompt_comletion_time(time1, time2):
    Dur_Total = "%.5f" % (time2 - time1)
    print("到达终点，任务完成，总共用时" + str(Dur_Total) + "秒")

def open_new_terminal(commands):
    """
    打开一个新的终端并执行命令；
    如果未作参数检查，不要试图在传入的命令字符串中添加多余的引号，可能会引发错误；
    “ ; exec bash ” 这个参数加上保证终端执行完指令后不会自动退出
    """
    cmd_list = []
    for cmd in commands:
        # eg：gnome-terminal --tab -e "bash -c 'roscore; exec bash' " >/dev/null  2>&1
        cmd_list.append(""" gnome-terminal --tab -e "bash -c '%s; exec bash' " >/dev/null  2>&1 """ % cmd)
    os.system(";".join(cmd_list))


def snapshot_and_check(room, camera_socket):
    """
    检查是否完成识别，如果识别完成，就返回 true；如果识别失败，就返回 False。
    room 为所处房间
    eg. room = b"A"，表示现在所处的房间为 A 房间
    """
    # 发送识别指令
    camera_socket.send(b"recog")

    camera_socket.send(room)
    # camera_socket.recv(1024)

    # 等待识别完成
    return camera_socket.recv(1024) == b"finish"  # 如果识别完成，就返回 true
