#!/usr/bin/env python3

import json
import random

import rospy
from std_msgs.msg import Bool, Empty
import actionlib
from darknet_ros_msgs.msg import BoundingBoxes
from nav_msgs.msg import Odometry
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from threading import Lock
import math
from math import sqrt, cos, sin

import time
import numpy as np
import tf2_ros
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PointStamped, Point
from tf2_geometry_msgs.tf2_geometry_msgs import do_transform_point
from sklearn.cluster import DBSCAN

import threading
import queue

from base_function import judge_array, determine_the_contents_of_all_lists

# class for voice
class ROS_Voice_Node(object):
    def __init__(self):
        self.get_start = False
        # topic name is  “ /start_lable ”
        self.start_lable_subscriber = rospy.Subscriber("/start_lable", Bool, self._get_start)

    def _get_start(self, voice_state):
        """唤醒成功"""
        self.get_start = voice_state

# class for vision
class ROS_Vision_Node(object):
    def __init__(self):
        # rospy.init_node("ros_nav_node", anonymous=False)
        self.recognize_results = ""
        self.result_list = []
        self.rate = rospy.Rate(10)
        self.darknet_subsciber = rospy.Subscriber("/darknet_ros/bounding_boxes", BoundingBoxes, self._get_info)

    def _get_info(self, msg):
        num = len(msg.bounding_boxes)
        self.result_list.clear()
        if num != 0:
            for i in range(num):
                if msg.bounding_boxes[i].Class is None:
                    self.result_list.append("")
                else:
                    self.result_list.append(msg.bounding_boxes[i].Class)
        else:
            return ""


# class for navigation
class ROS_Nav_Node(object):
    def __init__(self, dest_D="dest"):
        # rospy.init_node("ros_nav_node", anonymous=False)
        # MoveBaseAction from move_base_msgs.msg
        self.client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.odom_subsciber = rospy.Subscriber("/odom", Odometry, self._get_info)
        self.odom_pose_x = 0.0
        self.odom_pose_y = 0.0
        self._info_lock = Lock()

        # 一定要有这一行，读 actionlib 源码可以看到 client 和 server 会在建立连接时进行协商，然后丢掉第一个 goal
        # http://docs.ros.org/en/jade/api/actionlib/html/action__client_8py_source.html
        self.client.wait_for_server()
        self.pass_thres_radius = 0.05
        self.dest_D = dest_D

        # self.target_reached = False
        # self.timeout_duration = rospy.Duration(10)  # 设置10秒的超时时间
        # self.cancel_pub = rospy.Publisher('/cancel_navigation', Empty, queue_size=1)
        # self.timer = rospy.Timer(self.timeout_duration, self.timeout_callback)

    # def timeout_callback(self, event):
        # 定时器回调函数，在超时时被调用
        # if not self.target_reached:
            # rospy.logwarn("Target not reached within 10 seconds. Cancelling target.")
            # self.cancel_target()

    # def cancel_target(self):
        # 发布一个消息来取消目标点导航
        # cancel_msg = Empty()
        # self.cancel_pub.publish(cancel_msg)

    def _get_info(self, msg):
        """ process odometry message """
        self.odom_pose_x = msg.pose.pose.position.x
        self.odom_pose_y = msg.pose.pose.position.y

    def get_pose(self, id):
        """ read coordinate for goal point """
        with open("/home/ucar/ucar_ws/src/ucar_nav/scripts/pose/pose_{}.json".format(id), "r") as f:
            text = json.loads(f.read())
            # "position"
            self.pos_x = text["position"]["x"]
            self.pos_y = text["position"]["y"]
            self.pos_z = text["position"]["z"]
            # "orientation"
            self.ori_x = text["orientation"]["x"]
            self.ori_y = text["orientation"]["y"]
            self.ori_z = text["orientation"]["z"]
            self.ori_w = text["orientation"]["w"]

    def make_goal_pose(self):
        """ build goal """
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.pose.position.x = self.pos_x
        self.goal.target_pose.pose.position.y = self.pos_y
        self.goal.target_pose.pose.position.z = self.pos_z
        self.goal.target_pose.pose.orientation.x = self.ori_x
        self.goal.target_pose.pose.orientation.y = self.ori_y
        self.goal.target_pose.pose.orientation.z = self.ori_z
        self.goal.target_pose.pose.orientation.w = self.ori_w

    def send_goal(self):
        """ send goal """
        self.make_goal_pose()
        # 将目标对象通过 client 传入
        self.client.send_goal(self.goal)

    def get_state(self):
        """ 判断目标完成情况，若完成目标则返回 True """
        result = self.client.get_result()
        return result

    def send_goal_with_area_name(self, area_name):
        """ 结合读取和发送 """
        with open("/home/ucar/ucar_ws/src/ucar_nav/scripts/pose/pose_{}.json".format(area_name), "r") as f:
            text = json.loads(f.read())
            # "position"
            self.pos_x = text["position"]["x"]
            self.pos_y = text["position"]["y"]
            self.pos_z = text["position"]["z"]
            # "orientation"
            self.ori_x = text["orientation"]["x"]
            self.ori_y = text["orientation"]["y"]
            self.ori_z = text["orientation"]["z"]
            self.ori_w = text["orientation"]["w"]

        self.send_goal()

    def get_pose_xy(self):
        "获取并返回当前坐标 X，Y"
        return self.odom_pose_x, self.odom_pose_y

    def wait_for_goal_reached(self):
        """ 等待目标完成 """
        self.client.wait_for_result()

    def check_if_pose_near(self, target_point, threshold=0.8):
        """ 计算欧氏距离 """
        target_x = target_point[0]
        target_y = target_point[1]
        distance = sqrt((self.odom_pose_x - target_x) ** 2 + (self.odom_pose_y - target_y) ** 2)
        if distance < threshold:
            return True

    @staticmethod
    def _wrapAngle(angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def point_of_arrival(self, point):
        self.send_goal_with_area_name(point)
        self.wait_for_goal_reached()

    def finish_room_tasks(self, Vision_Node, room, point1, point2, point3, point4, point5):
        results1 = [""]
        results2 = [""]
        results3 = [""]
        results4 = [""]
        results5 = [""]
        
        print(Vision_Node.result_list)
        self.send_goal_with_area_name(point1)
        self.wait_for_goal_reached()

        rospy.loginfo("Now in {} room!".format(room))
        rospy.loginfo("first recognize :")
        Vision_Node.result_list = [""]
        time.sleep(0.5)
        # print(Vision_Node.result_list)
        results1 = Vision_Node.result_list
        Vision_Node.result_list = ['']
        if judge_array(results1)  is not None and judge_array(results1) != "lose":
            rospy.loginfo("The result of this identification is :")
            rospy.loginfo(judge_array(results1))
            rospy.loginfo("recognize finished")
            
            return judge_array(results1)
        else:
            rospy.loginfo("Failed to identify, proceed to next identification .")
            self.send_goal_with_area_name(point2)
            self.wait_for_goal_reached()

            rospy.loginfo("Second recognize :")
            Vision_Node.result_list = [""]
            time.sleep(0.5)
            results2 = Vision_Node.result_list
            Vision_Node.result_list = ['']
            if judge_array(results2) is not None and judge_array(results2) != "lose":
                rospy.loginfo("The result of this identification is :")
                rospy.loginfo(judge_array(results2))
                rospy.loginfo("recognize finished")
                return judge_array(results2)
            else:
                rospy.loginfo("Failed to identify, proceed to next identification .")
                self.send_goal_with_area_name(point3)
                self.wait_for_goal_reached()

                rospy.loginfo("Third recognize :")
                Vision_Node.result_list = [""]
                time.sleep(0.5)
                results3 = Vision_Node.result_list
                Vision_Node.result_list = ['']
                if judge_array(results3) is not None and judge_array(results3) != "lose":
                    rospy.loginfo("The result of this identification is :")
                    rospy.loginfo(judge_array(results3))
                    rospy.loginfo("recognize finished")
                    return judge_array(results3)
                else:
                    rospy.loginfo("Failed to identify, proceed to next identification .")
                    self.send_goal_with_area_name(point4)
                    self.wait_for_goal_reached()

                    rospy.loginfo("Fourth recognize :")
                    Vision_Node.result_list = [""]
                    time.sleep(0.5)
                    results4 = Vision_Node.result_list
                    Vision_Node.result_list = ['']
                    if judge_array(results4) is not None and judge_array(results4) != "lose":
                        rospy.loginfo("The result of this identification is :")
                        rospy.loginfo(judge_array(results4))
                        rospy.loginfo("recognize finished")
                        return judge_array(results4)
                    # else:

                    #     return "lose"
                        
                    else:
                        rospy.loginfo("Failed to identify, proceed to next identification .")
                        self.send_goal_with_area_name(point5)
                        self.wait_for_goal_reached()

                        rospy.loginfo("Fifth recognize :")
                        Vision_Node.result_list = [""]
                        time.sleep(0.5)
                        results5 = Vision_Node.result_list
                        Vision_Node.result_list = ['']
                        if  judge_array(results5) is not None and judge_array(results5) != "lose":
                            rospy.loginfo("The result of this identification is :")
                            rospy.loginfo(judge_array(results5))
                            rospy.loginfo("recognize finished")

                            return judge_array(results5)
                        else:
                            rospy.loginfo("The recognition failed.")
                            return "lose"

    def find_max_sort_in_FFFFF(self, Vision_Node, point1, point2, point3, point4, point5):
        all_results_in_F = []
        result1 = [""]
        result2 = [""]
        result3 = [""]
        result4 = [""]
        result5 = [""]
        impossible_results = ["corn", "wheat", "cucumber", "rice"]

        self.send_goal_with_area_name(point1)
        self.wait_for_goal_reached()
        rospy.loginfo("Now in F room!!!!!!")
        rospy.loginfo("First recognize.")
        Vision_Node.result_list = [""]
        time.sleep(0.5)
        result1 = Vision_Node.result_list
        Vision_Node.result_list = [""]
        
        if None not in result1:
            for i in range(len(result1)):
                if result1[i] in impossible_results:
                    result1.remove(result1[i])
            rospy.loginfo("The result of this identification is : {}".format(result1))
            # time.sleep(1)
            all_results_in_F.append(result1[:])
        # print(all_results_in_F)
        # time.sleep(1)

        self.point_of_arrival(point2)
        # self.send_goal_with_area_name(point2)
        # self.wait_for_goal_reached()
        # rospy.loginfo("Second recognize.")
        # time.sleep(0.5)
        # # recognize_results.clear()
        # Vision_Node.rate.sleep()
        # recognize_results = Vision_Node.result_list
        # for i in range(len(recognize_results)):
        #     if recognize_results[i] in impossible_results:
        #         recognize_results.remove(recognize_results[i])
        # rospy.loginfo("The result of this identification is : {}".format(recognize_results))
        # if "" not in recognize_results:
        #     all_results_in_F.append(recognize_results[:])
        # print(all_results_in_F)

        # if "" in recognize_results:
        self.send_goal_with_area_name(point3)
        self.wait_for_goal_reached()
        rospy.loginfo("Third recognize.")
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

        self.send_goal_with_area_name(point4)
        self.wait_for_goal_reached()
        rospy.loginfo("Fouth recognize.")
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

        self.send_goal_with_area_name(point5)
        self.wait_for_goal_reached()
        rospy.loginfo("Fifth recognize.")
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
        print(all_results_in_F)

        # print(all_results_in_F)
        if [""] in all_results_in_F:
            not_identify = ["corn_fruit", "watermelon", "cucumber_fruit"]
            sort_for_max_num = random.choice(not_identify)
            max_num = random.choice([3, 4, 5, 6,7 ,8])
            return sort_for_max_num, max_num
        sort_for_max_num, max_num = determine_the_contents_of_all_lists(all_results_in_F)
        return sort_for_max_num, max_num



# class for radar obstacle avoidance
class LaserToGlobalConverter(object):
    def __init__(self,
                 target_frame="map",
                 scan_topic="/scan",
                 edge_dist_threshold=0.08,
                 cluster_dist_threshold=0.2,
                 cluster_min_samples=10):
        # 初始化ROS节点
        rospy.init_node('laser_to_global_converter')
        self.target_frame = target_frame
        self.scan_topic = scan_topic
        self.edge_dist_threshold = edge_dist_threshold
        self.cluster_dist_threshold = cluster_dist_threshold
        self.cluster_min_samples = cluster_min_samples

        # 初始化tf2库的Buffer和Listener，用于坐标变换
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.rate = rospy.Rate(10)
        # 订阅激光雷达数据
        self.laser_sub = rospy.Subscriber('/scan', LaserScan, self.laser_callback)
        # 用于存储每个激光点在全局坐标系中的投影坐标的列表
        self.global_points = []

        self.process_thread = threading.Thread(target=self.process_data)
        self.process_thread.daemon = True  # 设置为守护线程，使得主程序退出时能够自动结束线程
        self.data_queue = queue.Queue()

    def laser_callback(self, laser_scan_msg):
        try:
            self.global_points.clear()  # 在每次读取雷达数据时，将原来的内容清空

            self.data_queue.put(laser_scan_msg)
            # global a
            # 获取最新的激光雷达坐标系到全局坐标系的变换
            # transform = self.tf_buffer.lookup_transform('map', laser_scan_msg.header.frame_id,
            #                                             rospy.Time(0), rospy.Duration(1.0))
            # # ranges = laser_scan_msg.ranges
            # # filtered_ranges = []
            # # for i in range(len(ranges)):
            # #     if ranges[i] > 1.5:
            # #         filtered_ranges.append(range[i])

            # for i, range_val in enumerate(laser_scan_msg.ranges):
            #     # 构造 Point 消息，表示激光雷达扫描的一个点
            #     laser_point = Point()
            #     laser_point.x = range_val * cos(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)
            #     laser_point.y = range_val * sin(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)

            #     # 将激光雷达扫描的点从激光雷达坐标系转换到全局坐标系
            #     global_point_stamped = PointStamped()
            #     global_point_stamped.header = laser_scan_msg.header
            #     global_point_stamped.point = laser_point
            #     # 将得到的雷达点云数据投影到 map 坐标系下
            #     global_point = do_transform_point(global_point_stamped, transform)

            #     # 将每个激光点的投影坐标加入到列表中
            #     self.global_points.append([global_point.point.x, global_point.point.y])
            # print(self.global_points)
            # print(a)
            # a += 1

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            # self.rate.sleep()
            rospy.logwarn('Error while transforming laser scan: {}'.format(e))

    def process_data(self):
        while not rospy.is_shutdown():
            if not self.data_queue.empty():
                laser_scan_msg = self.data_queue.get()
                transform = self.tf_buffer.lookup_transform('map', laser_scan_msg.header.frame_id,
                                                            rospy.Time(0), rospy.Duration(1.0))
                # ranges = laser_scan_msg.ranges
                # filtered_ranges = []
                # for i in range(len(ranges)):
                #     if ranges[i] > 1.5:
                #         filtered_ranges.append(range[i])

                for i, range_val in enumerate(laser_scan_msg.ranges):
                    # 构造 Point 消息，表示激光雷达扫描的一个点
                    laser_point = Point()
                    laser_point.x = range_val * cos(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)
                    laser_point.y = range_val * sin(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)

                    # 将激光雷达扫描的点从激光雷达坐标系转换到全局坐标系
                    global_point_stamped = PointStamped()
                    global_point_stamped.header = laser_scan_msg.header
                    global_point_stamped.point = laser_point
                    # 将得到的雷达点云数据投影到 map 坐标系下
                    global_point = do_transform_point(global_point_stamped, transform)

                    # 将每个激光点的投影坐标加入到列表中
                    self.global_points.append([global_point.point.x, global_point.point.y])

    def start_processing(self):
        # 启动数据处理线程
        self.process_thread.start()

    def find_points_in_roi(self, roi):
        """ 寻找可能在 roi 区域内的投影点 """
        # lists = []
        # # global a
        # for i in range(30):
        #     lists.append(self._find_points_in_roi(roi))
        #     # print(a)
        # self.global_points.clear()
        # # print(lists)
        #
        # count_of_ones = lists.count(1)
        # if count_of_ones > 15:
        #     return True
        # else:
        #     return False
        if len(self.global_points) == 0:  # 检查是否有雷达点云投影点，没有就直接返回
            print(len(self.global_points))
            return

        # 去除可能存在的一维列表，只要二维列表
        self.global_points = [sublist for sublist in self.global_points if len(sublist) == 2]

        roi_np = np.array(roi)
        roi_min_x, roi_min_y = np.min(roi_np[:, 0]), np.min(roi_np[:, 1])
        roi_max_x, roi_max_y = np.max(roi_np[:, 0]), np.max(roi_np[:, 1])

        # 将 self.global_points 转换为 numpy 数组
        global_points_np = np.array(self.global_points)
        global_points_np[np.isnan(global_points_np)] = 0  # 将可能存在的无效数据去除
        self.global_points.clear()

        # 获取 ROI 区域内的点云数据
        roi_indices = np.where(
            (global_points_np[:, 0] >= roi_min_x) & (global_points_np[:, 0] <= roi_max_x) &
            (global_points_np[:, 1] >= roi_min_y) & (global_points_np[:, 1] <= roi_max_y)
        )[0]  # 得到在区域内的投影点的索引
        # print(roi_indices)

        roi_cloud = global_points_np[roi_indices]  # 根据索引找投影点
        print(roi_cloud)

        # dbscan = DBSCAN(eps=self.cluster_dist_threshold, min_samples=self.cluster_min_samples)
        # clusters = dbscan.fit_predict(roi_cloud)

        # projections = []
        # # 查找聚类中心点
        # for cluster in set(clusters):
        #     if cluster != -1:  # 非噪声点
        #         cluster_points = roi_cloud[clusters == cluster]
        #         cluster_center = np.mean(cluster_points, axis=0)
        #         projections.append(cluster_center)

        # projections = [array.tolist() for array in projections]
        # if len(roi_cloud) >= 2:
        #     return True, projections
        # else:
        #     return False, projections
        # if len(roi_cloud) >= 2:
        if roi_cloud.shape[0] >= 5:  # 如果投影点数量大于 5 个，就判断在 roi 内有板子
            return 1
        else:
            return 0

    def _find_points_in_roi(self, roi):
        pass
        # if len(self.global_points) == 0:
        #     print(len(self.global_points))
        #     return
        # self.global_points = [sublist for sublist in self.global_points if len(sublist) == 2]
        # roi_np = np.array(roi)
        # roi_min_x, roi_min_y = np.min(roi_np[:, 0]), np.min(roi_np[:, 1])
        # roi_max_x, roi_max_y = np.max(roi_np[:, 0]), np.max(roi_np[:, 1])
        #
        # # 将self.global_points转换为numpy数组
        # global_points_np = np.array(self.global_points)
        # global_points_np[np.isnan(global_points_np)] = 0
        # # self.global_points.clear()
        # # 获取ROI内的点云数据
        # roi_indices = np.where(
        #     (global_points_np[:, 0] >= roi_min_x) & (global_points_np[:, 0] <= roi_max_x) &
        #     (global_points_np[:, 1] >= roi_min_y) & (global_points_np[:, 1] <= roi_max_y)
        # )[0]
        # # print(roi_indices)
        # roi_cloud = global_points_np[roi_indices]
        # print(roi_cloud)
        #
        #     # dbscan = DBSCAN(eps=self.cluster_dist_threshold, min_samples=self.cluster_min_samples)
        #     # clusters = dbscan.fit_predict(roi_cloud)
        #
        #     # projections = []
        #     # # 查找聚类中心点
        #     # for cluster in set(clusters):
        #     #     if cluster != -1:  # 非噪声点
        #     #         cluster_points = roi_cloud[clusters == cluster]
        #     #         cluster_center = np.mean(cluster_points, axis=0)
        #     #         projections.append(cluster_center)
        #
        #     # projections = [array.tolist() for array in projections]
        #     # if len(roi_cloud) >= 2:
        #     #     return True, projections
        #     # else:
        #     #     return False, projections
        #     # if len(roi_cloud) >= 2:
        # if roi_cloud.shape[0] >= 5:
        #     return 1
        # else:
        #     return 0

    def find_center_in_clusters(self, roi):
        # 确保有投影点，不然会报错
        if len(self.global_points) == 0:  # 检查是否有雷达点云投影点，没有就直接返回
            print(len(self.global_points))
            return

        # 去除可能存在的一维列表，只要二维列表
        self.global_points = [sublist for sublist in self.global_points if len(sublist) == 2]

        roi_np = np.array(roi)
        roi_min_x, roi_min_y = np.min(roi_np[:, 0]), np.min(roi_np[:, 1])
        roi_max_x, roi_max_y = np.max(roi_np[:, 0]), np.max(roi_np[:, 1])

        # 将self.global_points转换为numpy数组
        global_points_np = np.array(self.global_points)
        global_points_np[np.isnan(global_points_np)] = 0  # 将可能存在的无效数据去除
        self.global_points.clear()
        # self.global_points.clear()
        # 获取ROI内的点云数据
        roi_indices = np.where(
            (global_points_np[:, 0] >= roi_min_x) & (global_points_np[:, 0] <= roi_max_x) &
            (global_points_np[:, 1] >= roi_min_y) & (global_points_np[:, 1] <= roi_max_y)
        )[0]
        # print(roi_indices)
        roi_cloud = global_points_np[roi_indices]
        print(roi_cloud)

        dbscan = DBSCAN(eps=self.cluster_dist_threshold,
                        min_samples=self.cluster_min_samples)
        clusters = dbscan.fit_predict(roi_cloud)

        # 存放每一个 clusters 的中心点坐标
        projections = []

        # 查找聚类中心点
        for cluster in set(clusters):
            if cluster != -1:  # 非噪声点
                cluster_points = roi_cloud[clusters == cluster]
                cluster_center = np.mean(cluster_points, axis=0)
                projections.append(cluster_center)

        return projections  # 返回中心点列表
