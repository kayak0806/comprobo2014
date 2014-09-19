#!/usr/bin/env python
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist,Vector3
from sensor_msgs.msg import LaserScan

import sys, select, termios, tty

mean_distance = -1
fwd_dist = -1
back_dist = -1
 
def scan_recived(msg):
    # print len(msg.ranges)
    global mean_distance, fwd_dist, back_dist
    fwd_ranges = []
    back_ranges = []
    valid_ranges = []

    for i in range(5):
        i += 43 # five degrees centered on 45
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            fwd_ranges.append(msg.ranges[i])
    for i in range(5):
        i += 133 # five degrees centered on 135
        if msg.ranges[i] > 0 and msg.ranges[i] < 8:
            back_ranges.append(msg.ranges[i])

    if len(fwd_ranges) > 0:
        fwd_dist = sum(fwd_ranges)/float(len(fwd_ranges))
    if len(back_ranges) > 0:
        back_dist = sum(back_ranges)/float(len(back_ranges))

def follow(fwd, back):
    if (abs(fwd-back) < 0.3):
        twist = Twist(linear=Vector3(x=0.2),angular=Vector3(z=0.0))
    elif(fwd>back):
        twist = Twist(linear=Vector3(x=0.0),angular=Vector3(z=0.5))
    else:
        twist = Twist(linear=Vector3(x=0.0),angular=Vector3(z=-0.5))

    return twist

    

def base():
    rospy.init_node('follower', anonymous=True)

    r=rospy.Rate(10)
    while not rospy.is_shutdown():
        rospy.Subscriber("scan", LaserScan, scan_recived)
        pub = rospy.Publisher('cmd_vel', Twist)

        
        print fwd_dist-back_dist,fwd_dist,back_dist
        twist = follow(fwd_dist,back_dist)
        pub.publish(twist)
        r.sleep()

    


if __name__ == '__main__':
    try:
        base()
    except rospy.ROSInterruptException: pass