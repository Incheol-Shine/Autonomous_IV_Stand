#include <ros.h>
#include <std_msgs/Float32MultiArray.h>

#define MA_DIR1 34
#define MA_DIR2 35
#define MA_PWM 12   //left

#define MB_DIR1 37
#define MB_DIR2 36
#define MB_PWM 8    //right

#define MC_DIR1 43
#define MC_DIR2 42 
#define MC_PWM 9   //middle

#define MAX_VEL 255

ros::NodeHandle nh;
ros::Subscriber<std_msgs::Float32MultiArray> cmd_vel_sub("cmd_vel", Callba);

int a_vel = 0;
int b_vel = 0;
int c_vel = 0;

void Callba(const std_msgs::Float32MultiArray& cmd_vel_msg)
{
  a_vel = cmd_vel_msg.data[0];
  b_vel = cmd_vel_msg.data[1];
  c_vel = cmd_vel_msg.data[2];
}

void setup() {
  // Motor
  pinMode(MA_DIR1, OUTPUT);
  pinMode(MA_DIR2, OUTPUT);
  pinMode(MA_PWM, OUTPUT);
  pinMode(MB_DIR1, OUTPUT);
  pinMode(MB_DIR2, OUTPUT);
  pinMode(MB_PWM, OUTPUT);
  pinMode(MC_DIR1, OUTPUT);
  pinMode(MC_DIR2, OUTPUT);
  pinMode(MC_PWM, OUTPUT);

  // rosserial
  nh.initNode();
  nh.subscribe(cmd_vel_sub);
}

void loop() {
  go(a_vel, b_vel, c_vel);
  nh.spinOnce();
}

void go(int spdA, int spdB, int spdC){
  ControlSpeed(spdA, MA_DIR1, MA_DIR2, MA_PWM);
  ControlSpeed(spdB, MB_DIR1, MB_DIR2, MB_PWM);
  ControlSpeed(spdC, MC_DIR1, MC_DIR2, MC_PWM);
}

void ControlSpeed(int ref_speed, int direct_1, int direct_2, int pwm_pin_3){
  if(ref_speed < 0){
    ref_speed = -ref_speed ;
    if(ref_speed > MAX_VEL) ref_speed = MAX_VEL;
    digitalWrite(direct_1, HIGH);
    digitalWrite(direct_2, LOW);
    analogWrite(pwm_pin_3, ref_speed);
  }
  else{
    if(ref_speed > MAX_VEL) ref_speed = MAX_VEL;
    digitalWrite(direct_1, LOW);
    digitalWrite(direct_2, HIGH);
    analogWrite(pwm_pin_3, ref_speed);
  }
}
