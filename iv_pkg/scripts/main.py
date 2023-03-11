#!/usr/bin/env python
import rospy
import cv2
from img_process import ImgProc
from control import Ctrl

rospy.init_node('camera')
cap = cv2.VideoCapture(0)
cap.set(3,160)	# 가로 픽셀 길이
cap.set(4,90)	# 세로 ''

cv2.namedWindow('img_color')							# 'img_color' 이름의 창 생성
cv2.setMouseCallback('img_color', ImgProc.mouse_callback)	#
rate = rospy.Rate(10)
movefc = Ctrl()

while True:
	ret, ImgProc.image_np = cap.read()
	ImgProc.image_process()
	ImgProc.emergence()
	movefc.find_min_sona()
	movefc.control(ImgProc.square, ImgProc.value, ImgProc.left_length, ImgProc.right_length, ImgProc.top_length)

	if cv2.waitKey(1) == 27:
		break  # esc to quit
cap.release()
cv2.destroyAllWindows()
