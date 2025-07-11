# PyQt를 통한 VisPy 공압 튜브 시뮬레이션 환경 변수 설정

이 문서는 PyQt를 사용하여 VisPy 기반의 공압 튜브 시뮬레이션의 다양한 환경 변수를 제어하는 GUI(Graphical User Interface) 설계에 대해 설명합니다. 시뮬레이션의 과학적 분석을 용이하게 하기 위해 주요 물리적 매개변수들을 사용자가 직접 조절할 수 있도록 구현하는 것을 목표로 합니다.

## 1. 수정 가능한 시뮬레이션 매개변수 식별

이전 `test6_fixed.py` 코드에서 사용자가 조절할 수 있는 주요 시뮬레이션 매개변수들은 다음과 같습니다. 이 매개변수들은 시뮬레이션의 물리적 거동에 직접적인 영향을 미치므로, GUI를 통해 쉽게 접근하고 변경할 수 있도록 해야 합니다.

| 매개변수명           | 설명                                      | 단위    | 기본값 (예시) | 조절 범위 (예시) |
| :----------------- | :---------------------------------------- | :------ | :------------ | :--------------- |
| `carrier_mass`     | 캐리어의 질량                             | kg      | 0.1           | 0.01 ~ 1.0       |
| `carrier_diameter` | 캐리어의 직경 (단면적 계산에 사용)        | m       | 0.113         | 0.05 ~ 0.2       |
| `tube_length`      | 공압 튜브의 전체 길이                     | m       | 1.0           | 0.5 ~ 5.0        |
| `air_density`      | 공기의 밀도                               | kg/m³   | 1.225         | 0.5 ~ 2.0        |
| `tube_friction_coeff` | 튜브 벽과의 마찰 계수                     | 무차원  | 0.1           | 0.01 ~ 0.5       |
| `air_drag_coefficient` | 공기 저항 계수 (항력 계수, Cd)            | 무차원  | 0.5           | 0.1 ~ 1.0        |
| `brake_force_coeff` | 에어 브레이크의 감속력 계수               | 무차원  | 0.5           | 0.1 ~ 2.0        |
| `blower_pressure_blow` | 송풍기가 불어넣을 때의 과압               | Pa      | 1000          | 100 ~ 5000       |
| `blower_pressure_suck` | 송풍기가 흡입할 때의 진공압 (절대값)      | Pa      | 500           | 100 ~ 2000       |
| `brake_start_position` | 에어 브레이크가 작동하기 시작하는 튜브 내 위치 | m       | 0.8           | 0.5 ~ `tube_length` |
| `switch_detection_position` | 튜브 스위치가 캐리어를 감지하는 위치      | m       | 0.8           | 0.1 ~ `tube_length` |

**참고:** `carrier_area`는 `carrier_diameter`로부터 계산될 수 있습니다 ($A = \pi r^2 = \pi (d/2)^2$). `Carrier` 클래스 내부에서 이 계산이 이루어지도록 수정해야 합니다.

## 2. PyQt GUI 구조 설계

PyQt GUI는 사용자가 위에서 식별된 매개변수들을 쉽게 입력하고, 시뮬레이션을 시작/정지하며, 시뮬레이션 결과를 실시간으로 확인할 수 있도록 설계되어야 합니다. 다음은 제안하는 GUI의 주요 구성 요소입니다.

### 2.1. 메인 윈도우 (MainWindow)

*   **레이아웃:** 수직 레이아웃(QVBoxLayout)을 사용하여 상단에는 매개변수 설정 영역, 하단에는 VisPy 시뮬레이션 캔버스 영역을 배치합니다.
*   **시작/정지 버튼:** 시뮬레이션의 시작과 정지를 제어하는 버튼을 포함합니다.

### 2.2. 매개변수 설정 영역 (Parameter Settings Area)

이 영역은 사용자가 각 매개변수의 값을 입력하거나 조절할 수 있는 위젯들로 구성됩니다. `QFormLayout`을 사용하여 레이블과 입력 필드를 깔끔하게 정렬할 수 있습니다.

*   **입력 위젯:**
    *   **`QLineEdit` (텍스트 입력 필드):** 캐리어 질량, 튜브 길이, 공기 밀도, 압력 값 등 정확한 숫자 입력을 위해 사용합니다. 입력 값의 유효성 검사(숫자만 허용, 범위 제한 등)가 필요합니다.
    *   **`QSlider` (슬라이더):** 마찰 계수, 브레이크 힘 계수 등 연속적인 값 조절이 필요한 매개변수에 사용합니다. 슬라이더 옆에 현재 값을 표시하는 `QLabel`을 함께 배치하여 사용자가 값을 직관적으로 확인할 수 있도록 합니다.
*   **그룹화:** 관련 매개변수들을 `QGroupBox`로 묶어 GUI의 가독성을 높입니다 (예: `캐리어 설정`, `튜브 설정`, `송풍기 설정`, `제어 시스템 설정`).

### 2.3. VisPy 시뮬레이션 캔버스 영역 (VisPy Simulation Canvas Area)

*   VisPy의 `SceneCanvas`를 PyQt 위젯으로 통합하여 시뮬레이션의 3D 시각화를 표시합니다. `SceneCanvas`는 `QWidget`의 서브클래스이므로 PyQt 레이아웃에 직접 추가할 수 있습니다.

### 2.4. 시뮬레이션 제어 버튼 (Simulation Control Buttons)

*   **`QPushButton`:** `시작 (Start)`, `정지 (Stop)`, `재설정 (Reset)` 등의 버튼을 포함하여 시뮬레이션의 흐름을 제어합니다.

### 2.5. 데이터 표시 영역 (Optional: Data Display Area)

*   시뮬레이션 중 캐리어의 현재 속도, 위치, 작용하는 힘 등을 실시간으로 표시하는 `QLabel` 또는 `QTextEdit` 위젯을 추가할 수 있습니다. 이는 과학적 분석에 유용합니다.

## 3. PyQt와 VisPy 연동 방안

PyQt GUI와 VisPy 시뮬레이션 간의 연동은 다음과 같은 방식으로 이루어집니다.

1.  **매개변수 전달:** PyQt GUI에서 입력된 매개변수 값들은 `PneumaticTubeSimulation` 클래스의 인스턴스를 생성하거나, 시뮬레이션이 시작되기 전에 해당 인스턴스의 속성을 업데이트하는 데 사용됩니다.
2.  **시뮬레이션 제어:** PyQt 버튼의 `clicked` 시그널을 `PneumaticTubeSimulation` 클래스의 시작/정지/재설정 메서드에 연결합니다.
3.  **VisPy 캔버스 통합:** `PneumaticTubeVisualizer`의 `SceneCanvas`를 PyQt 메인 윈도우의 레이아웃에 추가합니다. VisPy의 애니메이션 루프는 PyQt의 이벤트 루프와 독립적으로 실행될 수 있지만, PyQt의 `QTimer`를 사용하여 VisPy의 `update` 함수를 주기적으로 호출하는 방식으로 통합할 수도 있습니다.

### 3.1. 코드 구조 예시 (Conceptual)

```python
# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QGroupBox, QSlider
from PyQt5.QtCore import Qt

from vispy.app import use_app
use_app("pyqt5") # VisPy가 PyQt5 백엔드를 사용하도록 설정

from test6_fixed import PneumaticTubeSimulation, PneumaticTubeVisualizer # 기존 시뮬레이션 코드 임포트

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("공압 튜브 시뮬레이션 제어")
        self.setGeometry(100, 100, 1200, 800)

        self.simulation = None # 시뮬레이션 인스턴스

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 1. 매개변수 설정 영역
        param_group_box = QGroupBox("시뮬레이션 매개변수")
        param_layout = QFormLayout()

        self.carrier_mass_input = QLineEdit("0.1")
        param_layout.addRow("캐리어 질량 (kg):", self.carrier_mass_input)

        self.carrier_diameter_input = QLineEdit("0.113")
        param_layout.addRow("캐리어 직경 (m):", self.carrier_diameter_input)

        self.tube_length_input = QLineEdit("1.0")
        param_layout.addRow("튜브 길이 (m):", self.tube_length_input)

        self.air_density_input = QLineEdit("1.225")
        param_layout.addRow("공기 밀도 (kg/m³):", self.air_density_input)

        self.tube_friction_slider = QSlider(Qt.Horizontal)
        self.tube_friction_slider.setRange(1, 50) # 0.01 ~ 0.5
        self.tube_friction_slider.setValue(10) # 0.1
        self.tube_friction_label = QLabel("0.1")
        self.tube_friction_slider.valueChanged.connect(lambda val: self.tube_friction_label.setText(str(val/100.0)))
        h_layout_friction = QHBoxLayout()
        h_layout_friction.addWidget(self.tube_friction_slider)
        h_layout_friction.addWidget(self.tube_friction_label)
        param_layout.addRow("튜브 마찰 계수:", h_layout_friction)

        # ... 다른 매개변수들도 유사하게 추가 ...

        param_group_box.setLayout(param_layout)
        main_layout.addWidget(param_group_box)

        # 2. 시뮬레이션 제어 버튼
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("시작")
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button = QPushButton("정지")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.reset_button = QPushButton("재설정")
        self.reset_button.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.reset_button)
        main_layout.addLayout(control_layout)

        # 3. VisPy 시뮬레이션 캔버스 영역
        # VisPy 캔버스는 시뮬레이션 인스턴스가 생성될 때 함께 생성되므로, 여기에 직접 추가하지 않음
        # 시뮬레이션 시작 시 기존 캔버스를 제거하고 새 캔버스를 추가하는 방식 고려
        self.vispy_canvas_container = QWidget()
        self.vispy_canvas_layout = QVBoxLayout()
        self.vispy_canvas_container.setLayout(self.vispy_canvas_layout)
        main_layout.addWidget(self.vispy_canvas_container, 1) # 확장 가능하도록 설정

        self.setLayout(main_layout)

    def start_simulation(self):
        if self.simulation:
            self.simulation.timer.stop()
            # 기존 캔버스 제거 (VisPy 캔버스가 PyQt 위젯으로 통합될 경우)
            if self.simulation.visualizer.canvas.parent() == self.vispy_canvas_container:
                self.vispy_canvas_layout.removeWidget(self.simulation.visualizer.canvas)
                self.simulation.visualizer.canvas.close()

        # GUI에서 매개변수 값 읽기
        carrier_mass = float(self.carrier_mass_input.text())
        carrier_diameter = float(self.carrier_diameter_input.text())
        tube_length = float(self.tube_length_input.text())
        air_density = float(self.air_density_input.text())
        tube_friction_coeff = self.tube_friction_slider.value() / 100.0
        # ... 다른 매개변수들도 읽기 ...

        # PneumaticTubeSimulation 클래스에 매개변수 전달 방식 수정 필요
        # 현재 PneumaticTubeSimulation은 __init__에서 모든 상수를 정의하고 있음
        # 이를 외부에서 주입받도록 수정해야 함
        # 예: self.simulation = PneumaticTubeSimulation(carrier_mass=carrier_mass, ...)

        # 임시로 직접 설정 (실제 구현 시 수정 필요)
        # test6_fixed.py의 PneumaticTubeSimulation.__init__을 수정하여 매개변수를 받도록 해야 함
        # 현재는 이 부분에서 오류가 발생할 수 있음
        self.simulation = PneumaticTubeSimulation()
        self.simulation.carrier.mass = carrier_mass
        self.simulation.tube_length = tube_length
        self.simulation.air_density = air_density
        self.simulation.tube_friction_coeff = tube_friction_coeff
        # ... 다른 매개변수들도 설정 ...

        # VisPy 캔버스를 PyQt 레이아웃에 추가
        self.vispy_canvas_layout.addWidget(self.simulation.visualizer.canvas)

        self.simulation.timer.start()
        print("시뮬레이션 시작")

    def stop_simulation(self):
        if self.simulation:
            self.simulation.timer.stop()
            print("시뮬레이션 정지")

    def reset_simulation(self):
        self.stop_simulation()
        # 매개변수 입력 필드를 초기값으로 되돌림
        self.carrier_mass_input.setText("0.1")
        self.carrier_diameter_input.setText("0.113")
        self.tube_length_input.setText("1.0")
        self.air_density_input.setText("1.225")
        self.tube_friction_slider.setValue(10)
        # ... 다른 매개변수들도 초기화 ...

        # 시뮬레이션 인스턴스 초기화 (필요시)
        if self.simulation:
            # 기존 캔버스 제거
            if self.simulation.visualizer.canvas.parent() == self.vispy_canvas_container:
                self.vispy_canvas_layout.removeWidget(self.simulation.visualizer.canvas)
                self.simulation.visualizer.canvas.close()
            self.simulation = None
        print("시뮬레이션 재설정")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
```

## 4. `test6_fixed.py` 코드 수정 필요 사항

위 PyQt GUI와 연동하기 위해서는 기존 `test6_fixed.py` 코드에 몇 가지 수정이 필요합니다.

1.  **`PneumaticTubeSimulation` 클래스 초기화 매개변수화:** 현재 `PneumaticTubeSimulation` 클래스의 `__init__` 메서드 내부에 모든 물리 상수가 하드코딩되어 있습니다. 이를 외부에서 매개변수로 받아 초기화할 수 있도록 수정해야 합니다. 이렇게 하면 PyQt GUI에서 입력받은 값을 시뮬레이션에 전달할 수 있습니다.
2.  **`Carrier` 클래스 `carrier_area` 계산:** `carrier_diameter`를 입력받아 `carrier_area`를 계산하도록 `Carrier` 클래스를 수정해야 합니다.
3.  **VisPy 캔버스 관리:** `PneumaticTubeVisualizer`의 `SceneCanvas`가 PyQt 애플리케이션 내에서 올바르게 생성되고 관리되도록 해야 합니다. `use_app("pyqt5")`를 호출하여 VisPy가 PyQt 이벤트 루프와 통합되도록 설정하는 것이 중요합니다.
4.  **시뮬레이션 재시작 로직:** 시뮬레이션을 재시작할 때 VisPy 캔버스가 올바르게 다시 그려지도록 기존 캔버스를 정리하고 새 캔버스를 추가하는 로직을 고려해야 합니다.

이 문서는 PyQt GUI를 통한 시뮬레이션 환경 변수 설정의 전반적인 구조와 필요한 코드 수정 사항을 제시합니다. 다음 단계에서는 이 설계에 따라 실제 코드를 구현하고 연동하는 작업을 진행할 수 있습니다.

