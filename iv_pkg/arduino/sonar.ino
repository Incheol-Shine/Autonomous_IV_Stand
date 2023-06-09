#include <ros.h>
#include <std_msgs/Float32.h>
#include <geometry_msgs/Twist.h>
#include <std_msgs/Float32MultiArray.h>

ros::NodeHandle  nh;
std_msgs::Float32MultiArray sonar_val;
ros::Publisher sonar("sonar", &sonar_val);

int trig0 = 3;
int echo0 = 8;
int trig1 = 4;                                   
int echo1 = 9;
int trig2 = 5;
int echo2 = 10;
int trig3 = 6;
int echo3 = 11;
int trig4 = 7;
int echo4 = 12;
int trig_arr[5] = {trig0, trig1, trig2, trig3, trig4};
int echo_arr[5] = {echo0, echo1, echo2, echo3, echo4};
float sonar_arr[5] = {0, 0, 0, 0, 0};
unsigned long duration;
float distance;

void setup() {
  nh.initNode();
  nh.advertise(sonar);

  pinMode(echo0, INPUT);
  pinMode(trig0, OUTPUT);
  pinMode(echo1, INPUT);
  pinMode(trig1, OUTPUT);
  pinMode(echo2, INPUT);
  pinMode(trig2, OUTPUT);
  pinMode(echo3, INPUT);
  pinMode(trig3, OUTPUT);
  pinMode(echo4, INPUT);
  pinMode(trig4, OUTPUT);
}

void loop() {
  // 각 초음파센서로부터 distance 를 계산
  // 튀는값 (0.0) 을 필터링하려고 조건문 사용
  // 40 은 로봇의 최소 안전거리를 임의로 정함
  for (int i=0; i<5; i++){
	// Trigger로 10ms동안 신호 출력
    digitalWrite(trig_arr[i], HIGH);
    delay(10);
    digitalWrite(trig_arr[i], LOW);
	// Echo 신호 입력받음
    duration = pulseIn(echo_arr[i], HIGH, 3000);
	// 거리 계산
    distance = ((float)(17 * duration) / 1000 );
    if(distance == 0){
      sonar_arr[i] = 40;
    }
    else sonar_arr[i] = distance;
  }
  sonar_val.data_length = 5;
  sonar_val.data = sonar_arr;
  sonar.publish(&sonar_val);
  nh.spinOnce();
}
