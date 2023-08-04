#! /usr/bin/env python3
import os
import cv2
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def publish_camera_data():
    # 初始化ROS节点
    rospy.init_node('camera_publisher', anonymous=True)

    # 创建ROS话题发布者
    image_pub = rospy.Publisher('/camera_topic', Image, queue_size=10)
    bridge = CvBridge()

    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 0表示默认摄像头设备编号

    # 循环读取并发布视频流
    while not rospy.is_shutdown():
        ret, frame = cap.read()

        if ret:
            # 将OpenCV图像转换为ROS图像消息
            img_msg = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            
            # 发布图像消息
            image_pub.publish(img_msg)
            
        else:
            rospy.logerr("无法读取摄像头")
            break

    # 释放资源
    cap.release()

if __name__ == '__main__':
    try:
        publish_camera_data()
    except rospy.ROSInterruptException:
        pass
