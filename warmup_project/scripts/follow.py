#!/usr/bin/env python
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist,Vector3
from sensor_msgs.msg import LaserScan

import sys, select, termios, tty

mean_distance = (-1,-1)
fwd_dist = -1
back_dist = -1
 
def scan_recived(msg):
    # print len(msg.ranges)
    global mean_distance, fwd_dist, back_dist
    fwd_ranges = []
    back_ranges = []
    valid_ranges = []

    min_dist = 0.5
    min_angl = -1
    for a in range(len(msg.ranges)):
        d = msg.ranges[a]
        if d==0.0:
            d = 0.5
        if d<min_dist:
            min_dist = d
            min_angl = a
    mean_distance = (min_dist, min_angl)

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

def check_status(fwd,back,min_reading):
    min_dist, min_angl = min_reading
    # lost?         4
    # crooked(l)    3
    # crooked(r)    2
    # at end?       1
    # ready?        0

    if min_angl == -1:
        return 4

    if min_angl < 60 or min_angl > 270:
        return 3
    if min_angl > 110:
        return 2
    if fwd == -1:
        return 1
    return 0

def follow(fwd, back, min_reading):
    turn, move = 0.0,0.3
    min_dist, min_angl = min_reading
    # print fwd, back
    # print min_dist
    state = check_status(fwd,back, min_reading)
    if state == 4:
        move = 0.0
        turn = 0.0
        print "I'm lost"
        print min_reading
    elif state == 3:
        move = 0.0
        turn = -0.3
        print 'right'
    elif state == 2:
        print 'left'
        move = 0.0
        turn = 0.3
    elif state == 1:
        move = 0.0
        turn = 0.0
        print 'end of wall'
    else:
        if(abs(fwd-back) < 0.01):
            print 'perfect'
            turn = 0.0
        else:
            print 'adjusting'
            turn = fwd-back
    twist = Twist(linear=Vector3(x=move), angular=Vector3(z=turn))
    return twist

    

def base():
    rospy.init_node('follower', anonymous=True)

    r=rospy.Rate(10)
    while not rospy.is_shutdown():
        rospy.Subscriber("scan", LaserScan, scan_recived)
        pub = rospy.Publisher('cmd_vel', Twist)
        twist = follow(fwd_dist,back_dist, mean_distance)
        pub.publish(twist)
        r.sleep()

    


if __name__ == '__main__':
    try:
        base()
    except rospy.ROSInterruptException: pass