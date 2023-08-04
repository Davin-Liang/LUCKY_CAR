#!/usr/bin/env python3

import os
import random
import time

import math
from math import sin, cos
from base_function import judge_array, quick_jugde, get_full_path, \
    determine_the_contents_of_all_lists, playsound_for_num, prevent_lose, update_teb_params, \
    prompt_comletion_time
from own_classes import ROS_Voice_Node, ROS_Nav_Node, ROS_Vision_Node
import rospy
from playsound import playsound

# ----------------------------Function Labels-------------------------------#
# 存储部分功能的开启标签
# --------------------------------------------------------------------------#
LaserScan_detect = False  # 是否启动 激光雷达探测障碍物方位 功能
voice = True
voice_broadcast = True# 是否开启语音播报
predict_results = True

# 在到达识别区前，是否到达某一点
Pose_dest = True
transition_point = False# A 区与 E 区之间的一点(返途)

identify_E =  True
identify_D =  True
identify_C =  True
identify_B =  True
identify_F =  True

# 接近各个房间时是否减速
# 路线：A -> E -> D -> C -> B -> E -> A -> F -> A
Slow_E = False
Slow_D = False
Slow_B = False
Slow_C = False
Slow_F = False
Slow = False

recognize_results = []
place_storing_result = []
labels = ["corn", "wheat", "cucumber", "rice"]

all_results_in_F = []
# 赋默认值，防止识别不出来
sort_for_max_num = "cucumber_fruit"
max_num = 3

def UCAR_main():
    # 创建节点
    rospy.init_node("main_node", anonymous=False)

    playsound(get_full_path("请启动"))
    time.sleep(0.15)
    
    if voice:
        # 启动语音节点
        Voice_Node = ROS_Voice_Node()
        # 等待语音节点成功启动
        time.sleep(1)

    # 启动视觉节点
    Vision_Node = ROS_Vision_Node()
    time.sleep(1)

    # 创建启动导航辅助节点
    Nav_Aid = ROS_Nav_Node()

    # 语音唤醒成功后直接解冻导航节点，小车开始移动
    rospy.loginfo("请喊“ 小V小V ”")
    while not Voice_Node.get_start:  # self.get_start 默认为 false
        time.sleep(0.01)
    rospy.loginfo("succeed move")

    T1 = time.time()  # 开始计时

    if LaserScan_detect:
        pass
    else:
        if identify_E:
            place_storing_result.append(Nav_Aid.finish_room_tasks(Vision_Node,
                                                          room="E",
                                                          point1="E1",
                                                          point2="E01",
                                                          point3="E02",
                                                          point4="E00",
                                                          point5="E000"))

        if identify_D:
            place_storing_result.append(Nav_Aid.finish_room_tasks(Vision_Node,
                                                          room="D",
                                                          point1="D001",
                                                          point2="D2",
                                                          point3="D01",
                                                          point4="D02",
                                                          point5="D00"))

        if identify_C:
            place_storing_result.append(Nav_Aid.finish_room_tasks(Vision_Node,
                                                          room="C",
                                                          point1="C03",
                                                          point2="C2",
                                                          point3="C02",
                                                          point4="C01",
                                                          point5="C00"))

        if identify_B:
            place_storing_result.append(Nav_Aid.finish_room_tasks(Vision_Node,
                                                          room="B",
                                                          point1="B03",
                                                          point2="B2",
                                                          point3="B02",
                                                          point4="B01",
                                                          point5="B00"))

        if predict_results:
            if "lose" in place_storing_result:
                result = prevent_lose(place_storing_result)
                for i in range(4):
                    place_storing_result[i] = result[i]        

        if transition_point: # 设置固定点,防止出现差错
            Nav_Aid.point_of_arrival("transition_point")      

        Nav_Aid.point_of_arrival("Fdoor1")

#----------------------------------------------------------------------------------------------------------------
#-------------------------------------------*****************----------------------------------------------
#-------------------------------------------*****************----------------------------------------------
#-------------------------------------------*****************----------------------------------------------
#----------------------------------------------------------------------------------------------------------------

        if identify_F:
            all_results_in_F = []
            result1 = [""]
            result2 = [""]
            result3 = [""]
            result4 = [""]
            result5 = [""]
            result51 = [""]
            result52 = [""]

            impossible_results = ["corn", "wheat", "cucumber", "rice"]

            print("")
            print("")
            print("")
#----------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------

            Nav_Aid.point_of_arrival("F2")
            rospy.loginfo("Now in F room!!!!!!")
            rospy.loginfo("SEONCD recognize.")
            Vision_Node.result_list = [""]
            time.sleep(0.5)
            result2 = Vision_Node.result_list
            Vision_Node.result_list = [""]
            
            if None not in result2:
                for i in range(len(result2)):
                    if result2[i] in impossible_results:
                        result2.remove(result2[i])
                rospy.loginfo("The result of this identification is : {}".format(result2))
                # time.sleep(1)
                if "" not in result2:
                    all_results_in_F.append(result2[:])

#----------------------------------------------------------------------------------------------------------
            print("")
            print("")
            print("")
#----------------------------------------------------------------------------------------------------------

            # if "" in recognize_results:
            Nav_Aid.point_of_arrival("F01")
            rospy.loginfo("THIRD recognize.")
            Vision_Node.result_list = [""]
            time.sleep(0.5)
            # recognize_results.clear()
            result3 = Vision_Node.result_list
            Vision_Node.result_list = [""]

            if None not in result3:
                for i in range(len(result3)):
                    if result3[i] in impossible_results:
                        result3.remove(result3[i])
                rospy.loginfo("The result of this identification is : {}".format(result3))
                if "" not in result3:
                    all_results_in_F.append(result3[:])
            # print(all_results_in_F)

#----------------------------------------------------------------------------------------------------------
            print("")
            print("")
            print("")
#----------------------------------------------------------------------------------------------------------

            Nav_Aid.point_of_arrival("F02")
            rospy.loginfo("FOURTH recognize.")
            Vision_Node.result_list = [""]
            time.sleep(0.5)
            result4 = Vision_Node.result_list
            Vision_Node.result_list = [""]

            if None not in result4:
                for i in range(len(result4)):
                    if result4[i] in impossible_results:
                        result4.remove(result4[i])
                rospy.loginfo("The result of this identification is : {}".format(result4))
                if "" not in result4:
                    all_results_in_F.append(result4[:])
                # print(all_results_in_F)

#----------------------------------------------------------------------------------------------------------
                    print("")
                    print("")
                    print("")
#----------------------------------------------------------------------------------------------------------

            Nav_Aid.point_of_arrival("F03")
            rospy.loginfo("FIFTH recognize.")
            Vision_Node.result_list = [""]
            time.sleep(1.0)
            result5 = Vision_Node.result_list
            Vision_Node.result_list = [""]

            if None not in result5:
                for i in range(len(result5)):
                    if result5[i] in impossible_results:
                        result5.remove(result5[i])
                rospy.loginfo("The result of this identification is : {}".format(result5))
                if "" not in result5:
                    all_results_in_F.append(result5[:])
                else:

#----------------------------------------------------------------------------------------------------------
                    print("")
                    print("")
                    print("")
#----------------------------------------------------------------------------------------------------------

                    Nav_Aid.point_of_arrival("F031")
                    rospy.loginfo("Special recognize.")
                    Vision_Node.result_list = [""]
                    time.sleep(0.5)
                    result51 = Vision_Node.result_list
                    Vision_Node.result_list = [""]

                    if None not in result51:
                        for i in range(len(result51)):
                            if result51[i] in impossible_results:
                                result51.remove(result51[i])
                        rospy.loginfo("The result of this identification is : {}".format(result51))
                        if "" not in result51:
                            all_results_in_F.append(result51[:])

#----------------------------------------------------------------------------------------------------------
                    print("")
                    print("")
                    print("")
#----------------------------------------------------------------------------------------------------------

                    Nav_Aid.point_of_arrival("F032")
                    rospy.loginfo("Special recognize.")
                    Vision_Node.result_list = [""]
                    time.sleep(0.5)
                    result52 = Vision_Node.result_list
                    Vision_Node.result_list = [""]

                    if None not in result52:
                        for i in range(len(result52)):
                            if result52[i] in impossible_results:
                                result52.remove(result52[i])
                        rospy.loginfo("The result of this identification is : {}".format(result52))
                        if "" not in result52:
                            all_results_in_F.append(result52[:])

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------

            print(all_results_in_F)

            # print(all_results_in_F)
            if [""] in all_results_in_F:
                not_identify = ["corn_fruit", "watermelon", "cucumber_fruit"]
                sort_for_max_num = random.choice(not_identify)
                max_num = random.choice([3, 4, 5, 6, 7, 8])
            else:
                sort_for_max_num, max_num = determine_the_contents_of_all_lists(all_results_in_F)

            print("The sort that have max number is {}.".format(sort_for_max_num))
            print("The max number is {}.".format(max_num))
        # Nav_Aid.point_of_arrival("Fdoor_out")
        # Nav_Aid.point_of_arrival("V2")
        if Pose_dest:
            Nav_Aid.send_goal_with_area_name("dest")
            Nav_Aid.wait_for_goal_reached()

        print("results of identification is :")
        print(place_storing_result)

        if voice_broadcast: # 是否打开语音播报
            playsound(get_full_path('任务完成'))
            time.sleep(0.15)

            playsound(get_full_path('B区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[3]))
            time.sleep(0.15)

            playsound(get_full_path('C区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[2]))
            time.sleep(0.15)

            playsound(get_full_path('D区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[1]))
            time.sleep(0.15)

            playsound(get_full_path('E区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[0]))
            time.sleep(0.15)

            

            playsound(get_full_path("F区域存放的果实为"))
            time.sleep(0.15)
            playsound(get_full_path(sort_for_max_num))
            time.sleep(0.15)
            playsound_for_num(max_num)


        T2 = time.time()
        prompt_comletion_time(time1=T1, time2=T2)

if __name__ == "__main__":
    try:
        UCAR_main()
    except KeyboardInterrupt:
        exit(0)
