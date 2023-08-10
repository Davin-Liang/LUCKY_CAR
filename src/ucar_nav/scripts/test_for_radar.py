import time
from own_classes import LaserToGlobalConverter
import rospy




if __name__ == '__main__':
    try:
        a = 0
        converter = LaserToGlobalConverter(
            target_frame="map",
            scan_topic="/scan",
            edge_dist_threshold=0.07,
            cluster_dist_threshold=0.20,
            cluster_min_samples=8)

        # time.sleep(1)
        roi = [[1.8, -0.1], [1.8, 0.1], [1.4, -0.1], [1.4, 0.1]]
        roi1 = [[0.2, -0.3], [0.2, 0.05], [1.8, -0.3], [1.8, 0.05]]
        roi2 = [[-0.2, 0.1], [0.2, 0.1], [0.2, 1.1], [-0.2, 1.1]]
        
        converter.start_processing()

        # print(converter.global_points)
        # if converter.find_points_in_roi(roi):
            # print("have")
        # else:
            # print("no have")
        # print(converter.find_center_in_clusters(roi))

        # time.sleep(3)

        while 1:
            # lists = []
            # for i in range(30):
            #     lists.append(converter.find_points_in_roi(roi1))
            #     # print(a)
            #     converter.global_points.clear()
            #     converter.rate.sleep()
            #
            # print(lists)
            #
            # count_of_ones = lists.count(1)
            # if count_of_ones > 15:
            #     result = True
            # else:
            #     result = False
            result = converter.find_points_in_roi(roi1)
            array = converter.find_center_in_clusters(roi1)
            if result:
                print("have board")
                print(array)
            else:
                print("no have board")

            time.sleep(1)


        rospy.spin()

    except rospy.ROSInterruptException:
        pass
