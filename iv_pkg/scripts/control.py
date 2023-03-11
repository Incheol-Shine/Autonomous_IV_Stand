import rospy
import math
from img_process import ImgProc
from std_msgs.msg import Float32MultiArray

class Ctrl:

	def __init__(self) -> None:
		self.sona = [55,55,55,55,55]
		self.min_sona = [0, 55]
		self.pub = rospy.Publisher('cmd_vel', Float32MultiArray, queue_size = 4)
		self.count = 1
		self.start = 0
		self.last_vels = [0, 0, 0]
		self.linear_x = 0
		self.linear_y = 0
		self.linear_z = 0

	def sonarCB(self, sonar_val):
		for i in range(5):
			self.sona[i] = sonar_val.data[i]

	def find_min_sona(self):
		rospy.Subscriber('sonar', Float32MultiArray, self.sonarCB)
		temp = min(self.sona)
		self.min_sona = [self.sona.index(temp), temp]
		# rospy.loginfo(self.min_sona)

	def move(self, move_mode):
		msg = Float32MultiArray()
		msg.data = [0, 0, 0]
		if (move_mode == 0):
			msg.data[0] = -self.linear_x * 0.866 - self.linear_y * 0.5 - self.angular_z * 0.2
			msg.data[1] = +self.linear_x * 0.866 - self.linear_y * 0.5 - self.angular_z * 0.2
			msg.data[2] = +self.linear_y - self.angular_z*0.2
		else:
			msg.data[0] = self.linear_x * math.cos(2.61799 - self.linear_y) - self.angular_z * 0.2
			msg.data[1] = self.linear_x * math.cos(0.523599 - self.linear_y) - self.angular_z * 0.2
			msg.data[2] = self.linear_x * math.cos(4.71239 - self.linear_y) - self.angular_z * 0.2
		print(f"x:{self.linear_x}, y:{self.linear_y}, z:{self.angular_z}")
		self.pub.publish(msg)

	def get_angle(self, left_length, right_length, top_length):
		angle = 0
		side_length = 0.5*(left_length + right_length)
		if(side_length != 0):
			aspect_ratio = top_length * 1.03 / side_length
			if(aspect_ratio < 1):
				angle = math.acos(aspect_ratio)
		if(left_length!=0):
			if(left_length <= right_length):
				angle = -angle
		return angle

	def get_angular_z(self, angle):
		threshold = 200
		self.angular_z = int(70 * (angle))
		if (self.angular_z > threshold):
			self.angular_z = threshold
		elif (self.angular_z < -threshold):
			self.angular_z = -threshold			###### angle_z_vel (angle) 값을 보정하는 부분. 역시 함수화 하는게 좋을 듯

	def get_x_y_z(self, square, value, angle, min_vel, max_vel):
		self.linear_x = int((0.8 * (100 - square)))
		if (self.linear_x < 0):
			self.linear_x *= 0.5

		self.linear_y = value
		if (-min_vel < self.linear_y <= min_vel):
			self.linear_y = 0
		elif (min_vel < self.linear_y <= max_vel):
			self.linear_y -= min_vel
		elif (-max_vel < self.linear_y <= -min_vel):
			self.linear_y += min_vel
		elif (max_vel < self.linear_y):
			self.linear_y = max_vel - min_vel
		elif (self.linear_y <= -max_vel):
			self.linear_y = -max_vel + min_vel	###### self.linear_y = value 의 값을 보정하는 부분.
		self.get_angular_z(angle)
	
	def get_x_y_z_obstacle(self, value, angle, square):
		if(self.min_sona[0] == 4):
			if(value < 0):
				self.linear_x -= angle
				self.linear_y = 0		# 0 deg

		elif(self.min_sona[0] == 3):
			if(value < 0):
				self.linear_x -= angle
				self.linear_y = 0.5236	# 30 deg
			
		elif(self.min_sona[0] == 2):
			if(value < 0):
				self.linear_x -= angle
				self.linear_y = 1.0472	# 60 deg

		elif(self.min_sona[0] == 1):
			if(square > 100):
				self.linear_x -= angle
				self.linear_y = 1.4708	# 84 deg

		elif(self.min_sona[0] == 0):
			if(square > 100):
				self.linear_x -= angle
				self.linear_y = 1.5708	# 90 deg
										###### 초음파 센서가 감지 된 경우의 x_vel, y_vel 값 설정.
		self.get_angular_z(angle)

	def serial(self, square, value, left_length, right_length, top_length):
		min_vel = 2
		max_vel = 42
		angle = 0
		
		self.angular_z = 0
		move_mode = 0

		angle = self.get_angle(left_length, right_length, top_length)
		
		if(self.min_sona[1] < 35):
			angle -= 0.05 * value
			move_mode = 1
			self.get_x_y_z_obstacle(value, angle, square)
		else:
			self.get_x_y_z(square, value, angle, min_vel, max_vel)

		if (ImgProc.emergence_flag == 3):
			self.move(move_mode)
			self.count = 1
			self.last_vels = [self.linear_x, self.linear_y, self.angular_z]
		else:
			if(self.count <= 100):
				print(self.count)
				self.linear_x = self.last_vels[0] / self.count
				self.linear_y = self.last_vels[1] / self.count
				self.angular_z = self.last_vels[2] / self.count
				self.move(move_mode)
				self.count += 0.5
			else:
				self.linear_x, self.linear_y, self.linear_z = 0, 0, 0
				self.move(move_mode)