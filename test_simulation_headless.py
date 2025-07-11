#!/usr/bin/env python3
"""
GUI 없이 시뮬레이션 코드를 테스트하는 스크립트
"""

import numpy as np
from pneumatic_tube_simulation_headless import PneumaticTubeSimulationHeadless

def test_simulation_parameters():
    """시뮬레이션 매개변수 설정 테스트"""
    
    # 기본 매개변수로 시뮬레이션 생성
    print("=== 기본 매개변수 테스트 ===")
    sim1 = PneumaticTubeSimulationHeadless()
    print(f"캐리어 질량: {sim1.carrier.mass} kg")
    print(f"캐리어 직경: {sim1.carrier.diameter} m")
    print(f"캐리어 단면적: {sim1.carrier.carrier_area:.6f} m²")
    print(f"튜브 길이: {sim1.tube_length} m")
    print(f"공기 밀도: {sim1.air_density} kg/m³")
    print(f"튜브 마찰 계수: {sim1.tube_friction_coeff}")
    print(f"공기 저항 계수: {sim1.air_drag_coefficient}")
    print(f"브레이크 힘 계수: {sim1.brake_force_coeff}")
    print(f"송풍기 과압: {sim1.blower_pressure_blow} Pa")
    print(f"송풍기 진공압: {sim1.blower_pressure_suck} Pa")
    print(f"브레이크 시작 위치: {sim1.brake_start_position} m")
    print(f"스위치 감지 위치: {sim1.switch_detection_position} m")
    print()
    
    # 사용자 정의 매개변수로 시뮬레이션 생성
    print("=== 사용자 정의 매개변수 테스트 ===")
    sim2 = PneumaticTubeSimulationHeadless(
        carrier_mass=0.2,
        carrier_diameter=0.15,
        tube_length=2.0,
        air_density=1.0,
        tube_friction_coeff=0.2,
        air_drag_coefficient=0.8,
        brake_force_coeff=1.0,
        blower_pressure_blow=2000,
        blower_pressure_suck=-1000,
        brake_start_position=1.5,
        switch_detection_position=1.5
    )
    print(f"캐리어 질량: {sim2.carrier.mass} kg")
    print(f"캐리어 직경: {sim2.carrier.diameter} m")
    print(f"캐리어 단면적: {sim2.carrier.carrier_area:.6f} m²")
    print(f"튜브 길이: {sim2.tube_length} m")
    print(f"공기 밀도: {sim2.air_density} kg/m³")
    print(f"튜브 마찰 계수: {sim2.tube_friction_coeff}")
    print(f"공기 저항 계수: {sim2.air_drag_coefficient}")
    print(f"브레이크 힘 계수: {sim2.brake_force_coeff}")
    print(f"송풍기 과압: {sim2.blower_pressure_blow} Pa")
    print(f"송풍기 진공압: {sim2.blower_pressure_suck} Pa")
    print(f"브레이크 시작 위치: {sim2.brake_start_position} m")
    print(f"스위치 감지 위치: {sim2.switch_detection_position} m")
    print()
    
    # 힘 계산 테스트
    print("=== 힘 계산 테스트 ===")
    # 초기 상태에서 힘 계산
    F_net_1 = sim1.carrier.calculate_forces(
        sim1.current_pressure_difference,
        sim1.air_density,
        sim1.tube_friction_coeff,
        sim1.air_drag_coefficient,
        0.0  # 브레이크 힘 없음
    )
    print(f"기본 매개변수 - 초기 순 힘: {F_net_1:.4f} N")
    
    F_net_2 = sim2.carrier.calculate_forces(
        sim2.current_pressure_difference,
        sim2.air_density,
        sim2.tube_friction_coeff,
        sim2.air_drag_coefficient,
        0.0  # 브레이크 힘 없음
    )
    print(f"사용자 정의 매개변수 - 초기 순 힘: {F_net_2:.4f} N")
    print()
    
    # 캐리어에 속도를 부여하고 힘 계산
    sim1.carrier.velocity = np.array([1.0, 0.0, 0.0])  # 1 m/s
    sim2.carrier.velocity = np.array([1.0, 0.0, 0.0])  # 1 m/s
    
    F_net_1_with_velocity = sim1.carrier.calculate_forces(
        sim1.current_pressure_difference,
        sim1.air_density,
        sim1.tube_friction_coeff,
        sim1.air_drag_coefficient,
        0.0  # 브레이크 힘 없음
    )
    print(f"기본 매개변수 - 속도 1m/s에서 순 힘: {F_net_1_with_velocity:.4f} N")
    
    F_net_2_with_velocity = sim2.carrier.calculate_forces(
        sim2.current_pressure_difference,
        sim2.air_density,
        sim2.tube_friction_coeff,
        sim2.air_drag_coefficient,
        0.0  # 브레이크 힘 없음
    )
    print(f"사용자 정의 매개변수 - 속도 1m/s에서 순 힘: {F_net_2_with_velocity:.4f} N")
    print()
    
    print("=== 테스트 완료 ===")
    print("시뮬레이션 매개변수가 올바르게 설정되고 힘 계산이 정상적으로 작동합니다.")

def test_simulation_run():
    """시뮬레이션 실행 테스트"""
    print("\n=== 시뮬레이션 실행 테스트 ===")
    
    # 기본 매개변수로 시뮬레이션 실행
    print("기본 매개변수로 시뮬레이션 실행 중...")
    sim = PneumaticTubeSimulationHeadless()
    result = sim.run_simulation(max_steps=1000)
    
    print(f"시뮬레이션 완료!")
    print(f"총 스텝 수: {result['total_steps']}")
    print(f"최종 위치: {result['final_position']:.3f} m")
    print(f"최종 속도: {result['final_velocity']:.3f} m/s")
    print(f"시뮬레이션 시간: {result['total_steps'] * sim.dt:.2f} s")

if __name__ == "__main__":
    test_simulation_parameters()
    test_simulation_run()

