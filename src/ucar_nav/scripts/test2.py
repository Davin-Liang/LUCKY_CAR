from own_classes import ROS_Vision_Node
import time
import rospy

test = ROS_Vision_Node()
while 1:
    print(test.result_list2)
    time.sleep(2)