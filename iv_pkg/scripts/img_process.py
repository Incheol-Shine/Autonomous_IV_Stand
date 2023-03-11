#!/usr/bin/env python
import cv2
import numpy as np

class ImgProc:
	lower_blue1 = 0
	upper_blue1 = 0
	lower_blue2 = 0
	upper_blue2 = 0
	lower_blue3 = 0
	upper_blue3 = 0
	image_np = [[[0,0,0]]]
	emergence_flag = 0
	square = 0
	check_data = 999
	emergence_filter = [0, 0, 0]
	left_length = 0
	right_length = 0
	top_length = 0
	value = 0
	min_square_area = 320

	def __init__(self) -> None:
		pass
    
	def mouse_callback(event, x, y, flags, param):
		if event == cv2.EVENT_LBUTTONDOWN:
			print(ImgProc.image_np[y, x])
			color = ImgProc.image_np[y, x]

			one_pixel = np.uint8([[color]])
			hsv = cv2.cvtColor(one_pixel, cv2.COLOR_BGR2HSV)
			hsv = hsv[0][0]

			if hsv[0] < 5:
				print("case1")
				ImgProc.lower_blue1 = np.array([hsv[0]-5+180, 40, 80])
				ImgProc.upper_blue1 = np.array([180, 255, 255])
				ImgProc.lower_blue2 = np.array([0, 40, 80])
				ImgProc.upper_blue2 = np.array([hsv[0], 255, 255])
				ImgProc.lower_blue3 = np.array([hsv[0], 40, 80])
				ImgProc.upper_blue3 = np.array([hsv[0]+5, 255, 255])

			elif hsv[0] > 175:
				print("case2")
				ImgProc.lower_blue1 = np.array([hsv[0], 40, 80])
				ImgProc.upper_blue1 = np.array([180, 255, 255])
				ImgProc.lower_blue2 = np.array([0, 40, 80])
				ImgProc.upper_blue2 = np.array([hsv[0]+5-180, 255, 255])
				ImgProc.lower_blue3 = np.array([hsv[0]-5, 40, 80])
				ImgProc.upper_blue3 = np.array([hsv[0], 255, 255])
			else:
				print("case3")
				ImgProc.lower_blue1 = np.array([hsv[0], 40, 80])
				ImgProc.upper_blue1 = np.array([hsv[0]+5, 255, 255])
				ImgProc.lower_blue2 = np.array([hsv[0]-5, 40, 80])
				ImgProc.upper_blue2 = np.array([hsv[0], 255, 255])
				ImgProc.lower_blue3 = np.array([hsv[0]-5, 40, 80])
				ImgProc.upper_blue3 = np.array([hsv[0], 255, 255])

			print(hsv[0])
			print("@1", ImgProc.lower_blue1, "~", ImgProc.upper_blue1)
			print("@2", ImgProc.lower_blue2, "~", ImgProc.upper_blue2)
			print("@3", ImgProc.lower_blue3, "~", ImgProc.upper_blue3)

	def find_num(data):
		ch = 0
		num_list = ([[55,[1,1,0,
					    0,1,1,
					    0,0,0]],
					[66,[0,1,0,
					    1,0,0,
					    0,1,0]]])
		mat_data = []
		mat_data_reverse = []
		number = 0
		for i in range(9):
			mat_data.append(data[i])
			mat_data_reverse.append(data[8-i])
		for i in range(len(num_list)):
			if mat_data == num_list[i][1]:
				number = int(num_list[i][0])
				ch = 1
				continue
			elif mat_data_reverse == num_list[i][1]:
				number = int(num_list[i][0])
				ch = 1
				continue
		if ch !=  1:
			number = 50
		return number

	def image_to_vector(image):
		image_raw = image
		color_data = 0
		range_data = []
		for j in range(3):
			for i in range(3):
				img = image_raw[0+(20*j):20+(20*j),0+(20*i):20+(20*i)]
				for y in range(0, 20):
					for x in range(0, 20):
						color_data = color_data + int(img[y, x])
				color_data = color_data//400
				if color_data < 180:
					range_data.append(1)
				else:
					range_data.append(0)
		number = int(ImgProc.find_num(range_data))
		return number

	def order_points(pts):
		rect = np.zeros((4, 2), dtype = "float32")
		s = pts.sum(axis=1)
		rect[0] = pts[np.argmin(s)]
		rect[2] = pts[np.argmax(s)]
		diff = np.diff(pts, axis=1)
		rect[1] = pts[np.argmin(diff)]
		rect[3] = pts[np.argmax(diff)]
		return rect

	def four_point_transform(image, pts):
		maxWidth = 120
		maxHeight = 120
		rect = ImgProc.order_points(pts)
		dst = np.array([
			[0, 0],
			[maxWidth, 0],
			[maxWidth, maxHeight],
			[0, maxHeight]], dtype="float32")
		M = cv2.getPerspectiveTransform(rect, dst)
		warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
		return warped

	def resize_and_threshold_warped(image):
		warped_new_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(warped_new_gray, (5, 5), 0)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blur)
		threshold = (min_val + max_val) // 2
		_, warped_processed = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		return warped_processed

	def emergence():
		ImgProc.emergence_filter.pop(2)
		ImgProc.emergence_filter.insert(0, ImgProc.square)
		if (ImgProc.emergence_filter[0] == ImgProc.emergence_filter[2] == ImgProc.emergence_filter[1]):
			ImgProc.emergence_flag = 1 ##stop
		elif(ImgProc.check_data != 55):
			ImgProc.emergence_flag = 2
		else:
			ImgProc.emergence_flag = 3
		# print(f"something : {ImgProc.something}")

	def image_process():
		# hsv
		img_hsv = cv2.cvtColor(ImgProc.image_np, cv2.COLOR_BGR2HSV)
		img_mask1 = cv2.inRange(img_hsv, ImgProc.lower_blue1, ImgProc.upper_blue1)
		img_mask2 = cv2.inRange(img_hsv, ImgProc.lower_blue2, ImgProc.upper_blue2)
		img_mask3 = cv2.inRange(img_hsv, ImgProc.lower_blue3, ImgProc.upper_blue3)
		img_mask = img_mask1 | img_mask2 | img_mask3
		img_result = cv2.bitwise_and(ImgProc.image_np, ImgProc.image_np, mask=img_mask)
		cv2.imshow('img_color', ImgProc.image_np)
		gray = cv2.cvtColor(img_result, cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (3, 3), 0)

		contours, hierarchy = cv2.findContours(blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		for cnt in contours:
			approx = cv2.approxPolyDP(cnt, 0.1 * cv2.arcLength(cnt, True), True)
			if len(approx):
				area = cv2.contourArea(approx)
				if area > ImgProc.min_square_area:
					ImgProc.square = (cv2.arcLength(cnt, True))
					try:
						rect = ImgProc.order_points(approx.reshape(4, 2))
					except ValueError:
						continue
					(tl, tr, br, bl) = rect

					img = cv2.drawContours(ImgProc.image_np, [approx], 0, (0, 0, 255), 2)
					ImgProc.left_length = (bl[1] - tl[1])
					ImgProc.right_length = (br[1] - tr[1])
					ImgProc.top_length = (tr[0] - tl[0])
					mid_line = (((tr[0]+br[0])/2 - (tl[0]+bl[0])/2) / 2)
					fin_mid = (tl[0] + mid_line)
					ImgProc.value = fin_mid - 80

					cv2.imshow("image", img)

					warped = ImgProc.four_point_transform(ImgProc.image_np, approx.reshape(4, 2))
					warped_eq = ImgProc.resize_and_threshold_warped(warped)
					cut = warped_eq[10:110,10:110] #up, left, down, right
					dst = cv2.resize(cut, (60, 60), interpolation=cv2.INTER_AREA)
					
					ImgProc.check_data = ImgProc.image_to_vector(dst)
