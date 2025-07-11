import numpy as np

# 1. 물리 엔진 관련 클래스
class Carrier:
    def __init__(self, mass, diameter, initial_position, initial_velocity):
        self.mass = mass  # kg
        self.diameter = diameter # m
        self.carrier_area = np.pi * (self.diameter / 2)**2 # m^2
        self.position = np.array(initial_position, dtype=float)  # m
        self.velocity = np.array(initial_velocity, dtype=float)  # m/s
        self.acceleration = np.array([0.0, 0.0, 0.0], dtype=float) # m/s^2

    def calculate_forces(self, pressure_difference, air_density, tube_friction_coeff, air_drag_coefficient, brake_force_coeff):
        # 추진력 (그림 6: 송풍기가 불어넣는 상황)
        F_propulsion = pressure_difference * self.carrier_area

        # 공기 저항 (속도 제곱에 비례)
        F_air_drag = 0.5 * air_density * np.linalg.norm(self.velocity)**2 * air_drag_coefficient * self.carrier_area

        # 튜브 벽 마찰 (단순화를 위해 속도에 비례)
        F_tube_friction = tube_friction_coeff * np.linalg.norm(self.velocity)

        # 에어 브레이크 힘 (그림 6: 목적지 근처에서 작동)
        F_brake = 0.0
        # 특정 위치에 도달하면 에어 브레이크 작동 (이 로직은 시뮬레이션 메인 루프에서 처리하는 것이 더 적절)
        # 여기서는 단순히 brake_force_coeff가 0이 아니면 적용
        if brake_force_coeff > 0 and np.linalg.norm(self.velocity) > 0.01: # 속도가 0에 가까우면 브레이크 적용 안함
            F_brake = brake_force_coeff * np.linalg.norm(self.velocity) # 속도에 비례하는 감속력

        # 모든 힘의 합력 (단순화를 위해 1D 운동으로 가정)
        F_net = F_propulsion - F_air_drag - F_tube_friction - F_brake
        return F_net

    def update_state(self, dt, F_net):
        self.acceleration[0] = F_net / self.mass
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

class Blower:
    def __init__(self, pressure_output_blow, pressure_output_suck):
        self.pressure_blow = pressure_output_blow # Pa
        self.pressure_suck = pressure_output_suck # Pa
        self.is_blowing = False
        self.is_sucking = False

    def set_mode(self, mode):
        if mode == 'blow':
            self.is_blowing = True
            self.is_sucking = False
            return self.pressure_blow
        elif mode == 'suck':
            self.is_blowing = False
            self.is_sucking = True
            return self.pressure_suck
        else:
            self.is_blowing = False
            self.is_sucking = False
            return 0.0

class AirBrake:
    def __init__(self, brake_start_position, brake_force_coefficient):
        self.brake_start_position = brake_start_position # m
        self.brake_force_coefficient = brake_force_coefficient
        self.is_active = False

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

class TubeSwitch:
    def __init__(self, detection_position):
        self.detection_position = detection_position # m
        self.carrier_detected = False

    def detect_carrier(self, carrier_position):
        if carrier_position[0] >= self.detection_position and not self.carrier_detected:
            self.carrier_detected = True
            return True
        elif carrier_position[0] < self.detection_position and self.carrier_detected: # 캐리어가 지나가면 리셋
            self.carrier_detected = False
            return False
        return False

# 3. 시뮬레이션 메인 루프 (VisPy 없는 버전)
class PneumaticTubeSimulationHeadless:
    def __init__(self, dt=0.01, tube_length=1.0, air_density=1.225, tube_friction_coeff=0.1,
                 air_drag_coefficient=0.5, brake_force_coeff=0.5, blower_pressure_blow=1000,
                 blower_pressure_suck=-500, brake_start_position=0.8, switch_detection_position=0.8,
                 carrier_mass=0.1, carrier_diameter=0.113):

        # 물리 상수 및 초기 조건
        self.dt = dt  # 시간 단계 (s)
        self.tube_length = tube_length # 튜브 길이 (m)
        self.air_density = air_density # 공기 밀도 (kg/m^3)
        self.tube_friction_coeff = tube_friction_coeff # 튜브 마찰 계수
        self.air_drag_coefficient = air_drag_coefficient # 공기 저항 계수
        self.brake_force_coeff = brake_force_coeff # 에어 브레이크 힘 계수
        self.blower_pressure_blow = blower_pressure_blow # 송풍기 과압 (Pa)
        self.blower_pressure_suck = blower_pressure_suck # 송풍기 진공압 (Pa)
        self.brake_start_position = brake_start_position # 에어 브레이크 시작 위치 (m)
        self.switch_detection_position = switch_detection_position # 튜브 스위치 감지 위치 (m)

        # 객체 초기화
        self.carrier = Carrier(mass=carrier_mass, diameter=carrier_diameter, initial_position=[0.0, 0.0, 0.0], initial_velocity=[0.0, 0.0, 0.0])
        self.blower = Blower(self.blower_pressure_blow, self.blower_pressure_suck)
        self.air_brake = AirBrake(self.brake_start_position, self.brake_force_coeff)
        self.tube_switch = TubeSwitch(self.switch_detection_position)

        # 초기 송풍기 모드 설정 (그림 6: 불어넣기)
        self.current_pressure_difference = self.blower.set_mode('blow')

    def update(self):
        # 튜브 스위치 감지 및 제어 로직
        if self.tube_switch.detect_carrier(self.carrier.position):
            print(f"Carrier detected at {self.carrier.position[0]:.2f}m. Activating air brake.")
            self.air_brake.activate()

        # 캐리어에 작용하는 순 힘 계산
        F_net = self.carrier.calculate_forces(
            self.current_pressure_difference,
            self.air_density,
            self.tube_friction_coeff,
            self.air_drag_coefficient,
            self.air_brake.brake_force_coefficient if self.air_brake.is_active else 0.0
        )

        # 캐리어 상태 업데이트
        self.carrier.update_state(self.dt, F_net)

        # 시뮬레이션 종료 조건 확인
        if self.carrier.position[0] > self.tube_length + 0.05 or self.carrier.position[0] < -0.05:
            print("Simulation ended: Carrier out of bounds.")
            return False
        elif np.linalg.norm(self.carrier.velocity) < 0.01 and self.carrier.position[0] > self.brake_start_position:
            print("Simulation ended: Carrier stopped at destination.")
            return False
        
        return True

    def run_simulation(self, max_steps=10000):
        """시뮬레이션을 실행하고 결과를 반환"""
        step = 0
        positions = []
        velocities = []
        times = []
        
        while step < max_steps:
            positions.append(self.carrier.position[0])
            velocities.append(np.linalg.norm(self.carrier.velocity))
            times.append(step * self.dt)
            
            if not self.update():
                break
                
            step += 1
            
            # 진행 상황 출력 (100 스텝마다)
            if step % 100 == 0:
                print(f"Step {step}: Position = {self.carrier.position[0]:.3f}m, Velocity = {np.linalg.norm(self.carrier.velocity):.3f}m/s")
        
        return {
            'times': times,
            'positions': positions,
            'velocities': velocities,
            'final_position': self.carrier.position[0],
            'final_velocity': np.linalg.norm(self.carrier.velocity),
            'total_steps': step
        }

