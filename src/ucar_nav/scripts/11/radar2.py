#!/usr/bin/env python3

import time
import numpy as np
import rospy
import sys
# sys.path.append("/home/ucar/ucar_ws/src/geometry2/tf2_ros/")
# from src import tf2_ros
# sys.path.append("/home/ucar/ucar_ws/src/geometry2/tf2_geometry_msgs/")
# from geometry2 import tf2_ros, tf2_geometry_msgs
# from src import tf2_geometry_msgs
# import numpy.testing.nosetester
import tf2_ros
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PointStamped, Point
from tf2_geometry_msgs.tf2_geometry_msgs import do_transform_point
from math import cos, sin
from sklearn.cluster import DBSCAN

class LaserToGlobalConverter:
    def __init__(self, # 类所需要的属性都有初始值
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

    def laser_callback(self, laser_scan_msg):
        try:
            self.global_points.clear()
            global a
            # 获取最新的激光雷达坐标系到全局坐标系的变换
            transform = self.tf_buffer.lookup_transform('map', laser_scan_msg.header.frame_id,
                                                        rospy.Time(0), rospy.Duration(1.0))

            # ranges = laser_scan_msg.ranges
            # filtered_ranges = []
            # for i in range(len(ranges)):
            #     if ranges[i] > 1.5:
            #         filtered_ranges.append(range[i])

            for i, range_val in enumerate(laser_scan_msg.ranges):
                # 构造一个Point消息，表示激光雷达扫描的一个点
                laser_point = Point()
                laser_point.x = range_val * cos(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)
                laser_point.y = range_val * sin(laser_scan_msg.angle_min + i * laser_scan_msg.angle_increment)

                # 将激光雷达扫描的点从激光雷达坐标系转换到全局坐标系
                global_point_stamped = PointStamped()
                global_point_stamped.header = laser_scan_msg.header
                global_point_stamped.point = laser_point
                global_point = do_transform_point(global_point_stamped, transform)

                # 将每个激光点的投影坐标加入到列表中
                self.global_points.append([global_point.point.x, global_point.point.y])
            # print(self.global_points)
            print(a)
            a += 1

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
            # self.rate.sleep()
            rospy.logwarn('Error while transforming laser scan: {}'.format(e))

    def find_points_in_roi(self, roi):
        lists = []
        global a
        for i in range(30):
            lists.append(self._find_points_in_roi(roi))
            print(a)
        self.global_points.clear()
        # print(lists)
        
        count_of_ones = lists.count(1)
        if count_of_ones > 15:
            return True
        else:
            return False
        
    def _find_points_in_roi(self, roi):
        if len(self.global_points) == 0:
            print(len(self.global_points))
            return
        self.global_points = [sublist for sublist in self.global_points if len(sublist) == 2]
        roi_np = np.array(roi)
        roi_min_x, roi_min_y = np.min(roi_np[:, 0]), np.min(roi_np[:, 1])
        roi_max_x, roi_max_y = np.max(roi_np[:, 0]), np.max(roi_np[:, 1])

        # 将self.global_points转换为numpy数组
        global_points_np = np.array(self.global_points)
        global_points_np[np.isnan(global_points_np)] = 0
        # self.global_points.clear()
        # 获取ROI内的点云数据
        roi_indices = np.where(
            (global_points_np[:, 0] >= roi_min_x) & (global_points_np[:, 0] <= roi_max_x) &
            (global_points_np[:, 1] >= roi_min_y) & (global_points_np[:, 1] <= roi_max_y)
        )[0]
        # print(roi_indices)
        roi_cloud = global_points_np[roi_indices]
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
        if roi_cloud.shape[0] >= 5:
            return 1
        else:
            return 0    
   
    # def find_center_in_clusters(self, roi):
    #     roi_np = np.array(roi)
    #     roi_min_x, roi_min_y = np.min(roi_np[:, 0]), np.min(roi_np[:, 1])
    #     roi_max_x, roi_max_y = np.max(roi_np[:, 0]), np.max(roi_np[:, 1])

    #     # 将self.global_points转换为numpy数组
    #     global_points_np = np.array(self.global_points)
    #     # self.global_points.clear()
    #     # 获取ROI内的点云数据
    #     roi_indices = np.where(
    #         (global_points_np[:, 0] >= roi_min_x) & (global_points_np[:, 0] <= roi_max_x) &
    #         (global_points_np[:, 1] >= roi_min_y) & (global_points_np[:, 1] <= roi_max_y)
    #     )[0]
    #     # print(roi_indices)
    #     roi_cloud = global_points_np[roi_indices]
    #     print(roi_cloud)
    #     dbscan = DBSCAN(eps=self.cluster_dist_threshold, min_samples=self.cluster_min_samples)
    #     clusters = dbscan.fit_predict(roi_cloud)

    #     projections = []
    #     # 查找聚类中心点
    #     for cluster in set(clusters):
    #         if cluster != -1:  # 非噪声点
    #             cluster_points = roi_cloud[clusters == cluster]
    #             cluster_center = np.mean(cluster_points, axis=0)
    #             projections.append(cluster_center)

    #     return projections


if __name__ == '__main__':
    try:
        a = 0
        converter = LaserToGlobalConverter(
            target_frame="map",
            scan_topic="/scan",
            edge_dist_threshold=0.07,
            cluster_dist_threshold=0.20,
            cluster_min_samples=8)
        time.sleep(1)
        roi = [[1.8, -0.1], [1.8, 0.1], [1.4, -0.1], [1.4, 0.1]]
        roi1 = [[0.2, -0.3], [0.2, 0.05], [1.8, -0.3], [1.8, 0.05]]
        roi2 = [[-0.2, 0.1], [0.2, 0.1], [0.2, 1.1], [-0.2, 1.1]]
        
        # print(converter.global_points)
        # if converter.find_points_in_roi(roi):
            # print("have")
        # else:
            # print("no have")
        # print(converter.find_center_in_clusters(roi))

        # time.sleep(3)

        while 1:
            lists = []
            for i in range(30):
                lists.append(converter._find_points_in_roi(roi1))
                print(a)
                converter.global_points.clear()
                converter.rate.sleep()
                
            print(lists)
        
            count_of_ones = lists.count(1)
            if count_of_ones > 15:
                result = True
            else:
                result = False
            # result = converter._find_points_in_roi(roi1)
            if result:
                print("have")
              # print(array)
            else:
                print("no have")

            time.sleep(1)


        rospy.spin()

    except rospy.ROSInterruptException:
        pass
