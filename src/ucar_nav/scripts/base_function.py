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
    """ Get full voice file path """
    dir = "/home/ucar/ucar_ws/src/ucar_nav/scripts/voice/"
    AP = dir + path + ".wav"
    return AP

def judge_array(array):
    """ judge the contents in returned list """
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
    """ quick judge """
    labels.remove(place[0])
    labels.remove(place[1])
    labels.remove(place[2])
    result = labels[0]
    return result

def determine_the_contents_of_all_lists(all_lists):
    all = []
    string_count = {}
    all = [item for sublist in all_lists for item in sublist]

    for item in all:
        if item not in string_count:
            string_count[item] = 1
        else:
            string_count[item] += 1
    print(all)

    most_frequent_string = max(string_count, key=string_count.get)
    most_frequent_count = string_count[most_frequent_string]

    return most_frequent_string, most_frequent_count

def playsound_for_num(num):
    """ play sound based on num """
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
    """ replace the existing lose string with vegatation """
    not_identify = ["corn", "wheat", "cucumber", "rice"]
    for i in range(4):
        if "lose" == array[i]:
            array[i] = random.choice(not_identify)
    return array

def prompt_comletion_time(time1, time2):
    Dur_Total = "%.5f" % (time2 - time1)
    print("到达终点，任务完成，总共用时" + str(Dur_Total) + "秒")
