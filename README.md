# CNS_Platform

# 1. 공유메모리 관리
## 1.1. TSMS 모듈에 변수 추가 및 연결 과정
    - db.py 파일에 변수 추가 ex. 'TSMS_Shut_BOL': {'V': 0, 'L': [], 'D': deque(maxlen=max_len_deque), 'type': 0},
    - CNS_UDP.py 파일에 updage_old_CNS_data(self) 함수에
      self.append_value_to_old_CNS_data(key='TSMS_Shut_BOL', value=self.TSMS_mem['Shut_BOL']) 추가
    - Main.py 에 def make_TSMS_mem(self) 함수에 'Shut_BOL': 0 를 추가함.