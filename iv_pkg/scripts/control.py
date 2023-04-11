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

	''' 5개의 초음파센서로부터 받은 센서값 self.sona에 저장 '''
	def sonarCB(self, sonar_val):
		for i in range(5):
			self.sona[i] = sonar_val.data[i]

	''' 가장 거리가 짧은 초음파센서(index)를 min_sona[0]에, 센서값을 min_sona[1]에 저장 '''
	def find_min_sona(self):
		rospy.Subscriber('sonar', Float32MultiArray, self.sonarCB)
		temp = min(self.sona)
		self.min_sona = [self.sona.index(temp), temp]

	''' 모터 속도를 구한 뒤 토픽으로 보내는 코드 '''
	def move(self, move_mode):
		motor = Float32MultiArray()
		motor.data = [0, 0, 0]
		if (move_mode == 0):
			motor.data[0] = -self.linear_x * 0.866 - self.linear_y * 0.5 - self.angular_z * 0.2
			motor.data[1] = +self.linear_x * 0.866 - self.linear_y * 0.5 - self.angular_z * 0.2
			motor.data[2] = +self.linear_y - self.angular_z * 0.2
		else:
			motor.data[0] = self.linear_x * math.cos(2.61799 - self.linear_y) - self.angular_z * 0.2
			motor.data[1] = self.linear_x * math.cos(0.523599 - self.linear_y) - self.angular_z * 0.2
			motor.data[2] = self.linear_x * math.cos(4.71239 - self.linear_y) - self.angular_z * 0.2
		self.pub.publish(motor)

	''' angle 은 마크의 왼쪽, 오른쪽 길이의 평균값과 위쪽 길이의 비율을 구한 뒤 삼각비로 구한다 '''
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

	''' z 각속도를 구하는 코드 '''
	def get_angular_z(self, angle):
		threshold = 200
		self.angular_z = int(70 * (angle))
		if (self.angular_z > threshold):
			self.angular_z = threshold
		elif (self.angular_z < -threshold):
			self.angular_z = -threshold

	''' 장애물이 없을 때 x, y 속도, z 각속도를 구하는 코드'''
	def get_x_y_z(self, square, value, angle, min_vel, max_vel):
		''' x 속도는 square(사각형 둘레) 에 비례함 '''
		self.linear_x = int((0.8 * (100 - square)))
		if (self.linear_x < 0):
			self.linear_x *= 0.5
		
		''' y 속도는 value(화면 중심과 마크 사이의 거리)에 비례함 '''
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
			self.linear_y = -max_vel + min_vel
		''' z 각속도는 angle 에 비례하며, 일정 범위를 넘지 않음 '''
		self.get_angular_z(angle)
	
	''' 장애물이 있을 때 x, y 속도, z 각속도를 구하는 코드'''
	def get_x_y_z_obstacle(self, value, square):
		self.linear_x = int((0.8 * (100 - square)))
		self.angular_z = -value
		if(self.min_sona[0] == 4):
			self.linear_y = 0		# 0 deg

		elif(self.min_sona[0] == 3):
			self.linear_y = 0.5236	# 30 deg
			
		elif(self.min_sona[0] == 2):
			self.linear_y = 1.0472	# 60 deg

		elif(self.min_sona[0] == 1):
			self.linear_y = 1.4708	# 84 deg

		elif(self.min_sona[0] == 0):
			self.linear_y = 1.5708	# 90 deg


	def control(self, square, value, left_length, right_length, top_length):
		min_vel = 2
		max_vel = 42

		self.angular_z = 0
		move_mode = 0
		angle = self.get_angle(left_length, right_length, top_length)
		
		''' 장애물이 감지된 경우, 움직임 모드를 1로 바꿈 '''
		if(self.min_sona[1] < 35):
			angle -= 0.05 * value
			move_mode = 1
			self.get_x_y_z_obstacle(value, square)
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
