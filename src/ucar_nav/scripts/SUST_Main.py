#!/usr/bin/env python3

import os
import time

import math
from math import sin, cos
from base_function import judge_array, quick_jugde, get_full_path, \
    determine_the_contents_of_all_lists, playsound_for_num, prevent_lose, update_teb_params
from own_classes import ROS_Voice_Node, ROS_Nav_Node, ROS_Vision_Node
import rospy
from playsound import playsound

# ----------------------------Function Labels-------------------------------#
# 存储部分功能的开启标签
# --------------------------------------------------------------------------#
LaserScan_detect = False  # 是否启动 激光雷达探测障碍物方位 功能
voice = True
voice_broadcast = False # 是否开启语音播报
predict_results = False

# 在到达识别区前，是否到达某一点
Pose_dest = True
transition_point = False# A 区与 E 区之间的一点(返途)

identify_E =  False
identify_D =  False
identify_C =  False
identify_B = False
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

    if voice:
        # 启动语音节点
        Voice_Node = ROS_Voice_Node()
        # 等待语音节点成功启动
        time.sleep(1)

    # 启动视觉节点
    Vision_Node = ROS_Vision_Node()
    time.sleep(1)

    rospy.loginfo("请喊“ 小V小V ”")
    # 创建启动导航辅助节点
    Nav_Aid = ROS_Nav_Node()

    # 语音唤醒成功后直接解冻导航节点，小车开始移动
    # 喊 “小V小V" 进行启动
    while not Voice_Node.get_start:  # self.get_start 默认为 false
        time.sleep(0.01)
    print("1")


    # 开始导航任务
    # 记录出发区出发时间
    T1 = time.time()  # 开始计时

    if LaserScan_detect:
        pass
    else:
        if identify_E:
            # 一个点、一个方向
            Nav_Aid.send_goal_with_area_name("E1")
            Nav_Aid.wait_for_goal_reached()

            rospy.loginfo("first recognize in E")
            # Vision_Node.rate.sleep()
            time.sleep(0.5)
            recognize_results = Vision_Node.result_list
            print(Vision_Node.recognize_results)
            place_storing_result.append(judge_array(recognize_results))
            # place_storing_result.append(judge_array(recognize_results))
            # rospy.loginfo(judge_array(recognize_results))
            rospy.loginfo("The result of this identification is :")
            rospy.loginfo(judge_array(recognize_results))

            rospy.loginfo("recognize finished")

        if identify_D:
            # 一个点, 两个方向
            Nav_Aid.send_goal_with_area_name("D1")
            Nav_Aid.wait_for_goal_reached()

            rospy.loginfo("first recognize in D")
            time.sleep(0.5)
            recognize_results = Vision_Node.result_list
            if judge_array(recognize_results) != "lose":
                place_storing_result.append(judge_array(recognize_results))

                rospy.loginfo("The result of this identification is :")
                rospy.loginfo(judge_array(recognize_results))
                rospy.loginfo("recognize finished")
            else: # 如果第一个方位未识别出
                Nav_Aid.send_goal_with_area_name("D2")
                Nav_Aid.wait_for_goal_reached()

                rospy.loginfo("Second recognize in D")
                time.sleep(0.5)
                recognize_results = Vision_Node.result_list
                place_storing_result.append(judge_array(recognize_results))

                rospy.loginfo("The result of this identification is :")
                rospy.loginfo(judge_array(recognize_results))

            rospy.loginfo("recognize finished") # 成功与否,都播报 "采集结束"

        if identify_C:
            Nav_Aid.send_goal_with_area_name("C1")
            Nav_Aid.wait_for_goal_reached()

            rospy.loginfo("first recognize in C")
            time.sleep(0.5)
            recognize_results = Vision_Node.result_list
            if judge_array(recognize_results) != "lose":
                place_storing_result.append(judge_array(recognize_results))

                rospy.loginfo("The result of this identification is :")
                rospy.loginfo(judge_array(recognize_results))
                rospy.loginfo("recognize finished")
            else:
                Nav_Aid.send_goal_with_area_name("C2")
                Nav_Aid.wait_for_goal_reached()

                rospy.loginfo("Second recognize in C")
                time.sleep(0.5)
                recognize_results = Vision_Node.result_list
                place_storing_result.append(judge_array(recognize_results))

                rospy.loginfo("The result of this identification is :")
                rospy.loginfo(judge_array(recognize_results))

            rospy.loginfo("recognize finished")

        if identify_B:
            # if False:
            if place_storing_result[0] != "lose" \
                    and place_storing_result[1] != "lose" \
                    and place_storing_result[2] != "lose":
                if place_storing_result[0] != place_storing_result[1] \
                    and place_storing_result[0] != place_storing_result[1] \
                    and place_storing_result[1] != place_storing_result[2]:
                    place_storing_result.append(quick_jugde(place_storing_result, labels))
                    Nav_Aid.send_goal_with_area_name("special_point")
                    Nav_Aid.wait_for_goal_reached()

                    rospy.loginfo("The result of this identification is :")
                    rospy.loginfo(place_storing_result[3])
                    rospy.loginfo("recognize finished")

            else: # 判断不出, 就走正常渠道
                Nav_Aid.send_goal_with_area_name("B1")
                Nav_Aid.wait_for_goal_reached()

                rospy.loginfo("first recognize in B")
                time.sleep(0.5)
                recognize_results = Vision_Node.result_list
                if judge_array(recognize_results) != "lose":
                    place_storing_result.append(judge_array(recognize_results))

                    rospy.loginfo("The result of this identification is :")
                    rospy.loginfo(judge_array(recognize_results))
                    rospy.loginfo("recognize finished")
                    time.sleep(1)
                else:
                    Nav_Aid.send_goal_with_area_name("B2")
                    Nav_Aid.wait_for_goal_reached()

                    rospy.loginfo("Second recognize in B")
                    time.sleep(0.5)
                    recognize_results = Vision_Node.result_list
                    place_storing_result.append(judge_array(recognize_results))

                    rospy.loginfo("The result of this identification is :")
                    rospy.loginfo(judge_array(recognize_results))
                rospy.loginfo("recognize finished")

        if predict_results:
            if "lose" in place_storing_result:
                result = prevent_lose(place_storing_result)
                for i in range(4):
                    place_storing_result[i] = result[i]        

        if transition_point: # 设置固定点,防止出现差错
            Nav_Aid.send_goal_with_area_name("transition_point")
            Nav_Aid.wait_for_goal_reached()

        if Slow:
            update_teb_params(1.5)       

        if identify_F:
            Nav_Aid.send_goal_with_area_name("Fdoor1")
            Nav_Aid.wait_for_goal_reached()

            print(rospy.get_param("/move_base/TebLocalPlannerROS/max_vel_x"))
            Nav_Aid.send_goal_with_area_name("F03")
            Nav_Aid.wait_for_goal_reached()
            rospy.loginfo("first recognize in F")
            time.sleep(1)
            recognize_results = Vision_Node.result_list
            rospy.loginfo(recognize_results)
            all_results_in_F.append(recognize_results)

            Nav_Aid.send_goal_with_area_name("F2")
            Nav_Aid.wait_for_goal_reached()
            rospy.loginfo("Second recognize in F")
            time.sleep(1)
            recognize_results = Vision_Node.result_list
            rospy.loginfo(recognize_results)
            all_results_in_F.append(recognize_results)

            Nav_Aid.send_goal_with_area_name("F1")
            Nav_Aid.wait_for_goal_reached()
            rospy.loginfo("Third recognize in F")
            time.sleep(1)
            recognize_results = Vision_Node.result_list
            rospy.loginfo(recognize_results)
            all_results_in_F.append(recognize_results)

            Nav_Aid.send_goal_with_area_name("F01")
            Nav_Aid.wait_for_goal_reached()
            rospy.loginfo("Fouth recognize in F")
            time.sleep(1)
            recognize_results = Vision_Node.result_list
            rospy.loginfo(recognize_results)
            all_results_in_F.append(recognize_results)

            Nav_Aid.send_goal_with_area_name("F02")
            Nav_Aid.wait_for_goal_reached()
            rospy.loginfo("Fifth recognize in F")
            time.sleep(1)
            recognize_results = Vision_Node.result_list
            rospy.loginfo(recognize_results)
            all_results_in_F.append(recognize_results)

            sort_for_max_num, max_num = determine_the_contents_of_all_lists(all_results_in_F)
            print(sort_for_max_num)
            print(max_num)

            # Nav_Aid.send_goal_with_area_name("Fdoor2")
            # Nav_Aid.wait_for_goal_reached()

        if Pose_dest:
            Nav_Aid.send_goal_with_area_name("dest")
            Nav_Aid.wait_for_goal_reached()

        print("results of identification is :")
        print(place_storing_result)

        if voice_broadcast: # 是否打开语音播报
            playsound(get_full_path('任务完成'))
            time.sleep(0.15)

            playsound(get_full_path('E区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[0]))
            time.sleep(0.15)

            playsound(get_full_path('D区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[1]))
            time.sleep(0.15)

            playsound(get_full_path('C区域种植的作物为'))
            time.sleep(0.15)
            playsound(get_full_path(place_storing_result[2]))
            time.sleep(0.15)

            playsound(get_full_path('B区域种植的作物为'))
            time.sleep(0.15)
            # playsound(get_full_path(place_storing_result[3]))

            # playsound(get_full_path(sort_for_max_num))
            # time.sleep(0.15)
            playsound_for_num(max_num)


        T2 = time.time()
        Dur_Total = "%.5f" % (T2 - T1)
        print("到达终点，任务完成，总共用时" + str(Dur_Total) + "秒")

if __name__ == "__main__":
    try:
        UCAR_main()
    except KeyboardInterrupt:
        exit(0)
