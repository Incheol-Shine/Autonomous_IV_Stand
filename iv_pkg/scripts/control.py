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

	def sonarCB(self, sonar_val):
		for i in range(5):
			self.sona[i] = sonar_val.data[i]

	def find_min_sona(self):
		rospy.Subscriber('sonar', Float32MultiArray, self.sonarCB)
		temp = min(self.sona)
		self.min_sona = [self.sona.index(temp), temp]
		# rospy.loginfo(self.min_sona)

	def move(self, linear_x_vel, linear_y_vel, angular_z_vel, move_mode):
		msg = Float32MultiArray()
		msg.data = [0, 0, 0]
		if (move_mode == 0):
			msg.data[0] = -linear_x_vel * 0.866 - linear_y_vel * 0.5 - angular_z_vel * 0.2
			msg.data[1] = +linear_x_vel * 0.866 - linear_y_vel * 0.5 - angular_z_vel * 0.2
			msg.data[2] = +linear_y_vel - angular_z_vel*0.2
		else:
			msg.data[0] = linear_x_vel * math.cos(2.61799 - linear_y_vel) - angular_z_vel * 0.2
			msg.data[1] = linear_x_vel * math.cos(0.523599 - linear_y_vel) - angular_z_vel * 0.2
			msg.data[2] = linear_x_vel * math.cos(4.71239 - linear_y_vel) - angular_z_vel * 0.2
		print(f"x:{linear_x_vel}, y:{linear_y_vel}, z:{angular_z_vel}")
		self.pub.publish(msg)

	def serial(self, square, value, left_length, right_length, top_length):
		k=200
		min_vel = 2
		max_vel = 42
		angle = 0
		linear_y_vel = value
		angular_z_vel = 0
		move_mode = 0

		side_length = 0.5*(left_length + right_length)
		if(side_length != 0):
			aspect_ratio = top_length * 1.03 / side_length
			if(aspect_ratio >= 1):
				angle = 0
			else:
				angle = math.acos(aspect_ratio)
		if(left_length!=0):
			if(left_length <= right_length):
				angle = -angle
	
		if (-min_vel < linear_y_vel <= min_vel):
			linear_y_vel = 0
		elif (min_vel < linear_y_vel <= max_vel):
			linear_y_vel -= min_vel
		elif (-max_vel < linear_y_vel <= -min_vel):
			linear_y_vel += min_vel
		elif (max_vel < linear_y_vel):
			linear_y_vel = max_vel - min_vel
		elif (linear_y_vel <= -max_vel):
			linear_y_vel = -max_vel + min_vel	###### linear_y_vel = value 의 값을 보정하는 부분. 함수화 하는게 좋을 듯

		linear_x_vel = int((0.8 * (100 - square)))
		if (linear_x_vel < 0):
			linear_x_vel *= 0.5
		
		if(self.min_sona[1] < 35):
			angle -= 0.05 * value
			if(self.min_sona[0] == 4):
				if(value < 0):
					move_mode = 1
					linear_x_vel -= angle
					linear_y_vel = 0		# 0 deg

			elif(self.min_sona[0] == 3):
				if(value < 0):
					move_mode = 1
					linear_x_vel -= angle
					linear_y_vel = 0.5236	# 30 deg
				
			elif(self.min_sona[0] == 2):
				if(value < 0):
					move_mode = 1
					linear_x_vel -= angle
					linear_y_vel = 1.0472	# 60 deg

			elif(self.min_sona[0] == 1):
				if(square > 100):
					move_mode = 1
					linear_x_vel -= angle
					linear_y_vel = 1.4708	# 84 deg

			elif(self.min_sona[0] == 0):
				if(square > 100):
					move_mode = 1
					linear_x_vel -= angle
					linear_y_vel = 1.5708	# 90 deg
											###### 초음파 센서가 감지 된 경우의 x_vel, y_vel 값 설정. 더 좋은 구조가 가능하지 않을까?

		angular_z_vel = int(70 * (angle))
		if (angular_z_vel > k):
			angular_z_vel = k
		elif (angular_z_vel < -k):
			angular_z_vel = -k			###### angle_z_vel (angle) 값을 보정하는 부분. 역시 함수화 하는게 좋을 듯

		if (ImgProc.emergence_flag == 3):
			self.move(linear_x_vel, linear_y_vel, angular_z_vel, move_mode)
			self.count = 1
			self.last_vels = [linear_x_vel, linear_y_vel, angular_z_vel]
		else:
			if(self.count <= 100):
				print(self.count)
				linear_x_vel = self.last_vels[0] / self.count
				linear_y_vel = self.last_vels[1] / self.count
				angular_z_vel = self.last_vels[2] / self.count
				self.move(linear_x_vel, linear_y_vel, angular_z_vel, move_mode)
				self.count += 0.5
			else:
				self.move(0, 0, 0, move_mode)
				