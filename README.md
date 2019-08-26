# CNS_Platform

# 1. 공유메모리 관리
## 1.1. TSMS 모듈에 변수 추가 및 연결 과정
    - db.py 파일에 변수 추가 ex. 'TSMS_Shut_BOL': {'V': 0, 'L': [], 'D': deque(maxlen=max_len_deque), 'type': 0},
    - CNS_UDP.py 파일에 updage_old_CNS_data(self) 함수에
      self.append_value_to_old_CNS_data(key='TSMS_Shut_BOL', value=self.TSMS_mem['Shut_BOL']) 추가
    - Main.py 에 def make_TSMS_mem(self) 함수에 'Shut_BOL': 0 를 추가함.
# 2. Interface 관리
## 2.1. Interface  수정 방법
    - 1) interface 폴더에서 terminal을 실행한다.
    - 2) pyuic5 -o gui_study_9.py study_9.ui 을 입력한다. 그리고 study_9.py의 마지막 라인에서 import를 주석으로
         처리한다.
    - 3) pyrcc5 -o Study_9_re_2.py Study_9_re.qrc 를 입력한다.
    - 4) 인터페이스(즉, study_9.py를 불러오는 곳)에서 from Interface.resource import Study_9_re_rc를 가져온다.
# 3. 검증 시 동작 과정
    - 1) 2% -> 100% 출력 증가 수행
    - 2) 100% 출력에 도달하면 정상 운전으로 전환 (제어봉 Auto)
    - 2) 100% 에서 비정상 상태 발생 및 진단.s
