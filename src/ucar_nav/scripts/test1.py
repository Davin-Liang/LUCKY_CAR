#!/usr/bin/env python3

# test whether car can arrive place.

import time
from own_classes import ROS_Nav_Node, ROS_Voice_Node
from laser_geometry import LaserProjection
import rospy
# from tf2_geometry_msgs.tf2_geometry_msgs import do_transform_point
# from tf2_ros import do_transform_cloud
Pose_1 = True
rospy.init_node("main_node", anonymous=False)
# 创建启动导航辅助节点
print("1")
Nav_Aid = ROS_Nav_Node()
yuyinNode = ROS_Voice_Node()

while 1:
    print(Nav_Aid.odom_pose_x)
    time.sleep(2)
# while not yuyinNode.get_start:
#     time.sleep(0.01)
# print("1")
# if Pose_1:
#     Nav_Aid.get_pose("B1")
#     Nav_Aid.send_goal()

#     # 等待任务完成
#     # while not Nav_Aid.get_state():
#         # time.sleep(0.1)
#     Nav_Aid.wait_for_goal_reached()

