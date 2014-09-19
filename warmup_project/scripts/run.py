#!/usr/bin/env python
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist,Vector3
from sensor_msgs.msg import LaserScan

import sys, select, termios, tty

dist = -1
angl = -1
 
def scan_recived(msg):
    # print len(msg.ranges)
    global dist, angl
    min_dist = 0.5
    min_angl = -1
    for a in range(len(msg.ranges)):
        d = msg.ranges[a]
        if d==0.0:
            d = 0.5
        if d<min_dist:
            min_dist = d
            min_angl = a
    dist = min_dist
    angl = min_angl        

def run(dist,angl):
    top = 2.0
    turn = 0
    move = 0
    if angl == -1:
        move = 0.0
    else:
        turn = angl/180.0 -1
        if angl<270 and angl >90:
            move = -top*(dist-1)
    twist = Twist(linear = Vector3(x=move),angular=Vector3(z=turn))
    return twist


def base():
    rospy.init_node('follower', anonymous=True)

    r=rospy.Rate(10)
    while not rospy.is_shutdown():
        rospy.Subscriber("scan", LaserScan, scan_recived)
        pub = rospy.Publisher('cmd_vel', Twist)

        twist = run(dist,angl)
        pub.publish(twist)
        r.sleep()


    


if __name__ == '__main__':
    try:
        base()
    except rospy.ROSInterruptException: pass