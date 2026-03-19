import time  
import Robot

robot = Robot.RPC('192.168.58.2')
error,version = robot.GetSDKVersion()
for i in range(6):
    robot.StartJOG(0, i + 1, 0, 20.0, 20.0, 30.0)
    time.sleep(1)
    robot.ImmStopJOG()
    time.sleep(1)
robot.CloseRPC()