#!/usr/bin/env python
import rospy
import roslib

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

import sys, select, termios, tty

import follow, run

dist = -1
angl = -1
mean_distance = -1
fwd_dist = -1
back_dist = -1


def base():
    global dist, angl
    global mean_distance, fwd_dist, back_dist

    rospy.init_node('follower', anonymous=True)
    pub = rospy.Publisher('cmd_vel', Twist)
    r=rospy.Rate(10)
    while not rospy.is_shutdown():
        twist = Twist()
        ch = getch()
        if ch == '\x03':
            # stop
            twist = Twist()
            pub.publish(twist)
            break

        elif ch == 'f':
            # wall follow
            rospy.Subscriber("scan", LaserScan, follow.scan_recived)
            twist = follow.follow(fwd_dist,back_dist)
        elif ch == 'r':
            # run away
            rospy.Subscriber("scan", LaserScan, run.scan_recived)
            twist = run.run(dist,angl)
        pub.publish(twist)

def getch():
    """ Return the next character typed on the keyboard """
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


if __name__ == "__main__":
    try:
        base()
    except rospy.ROSInterruptException: pass


