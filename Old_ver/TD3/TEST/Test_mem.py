import numpy as np


class ReplayBuffer:
    def __init__(self, max_size=1e6):
        self.storage = []       # 훈련 정보를 저장하는 리스트
        self.max_size = max_size    # 최대 메모리의 크기
        self.prt = 0        # ?

    def add(self, data):
        if len(self.storage) == self.max_size:      # 저장소가 최대 크기 보다 크면
            self.storage[int(self.prt)] = data      # 0번째 부터 다시 저장
            self.prt = (self.prt + 1) % self.max_size # 1씩 더하면서 최대치에 도달하면 다시 0으로 변환
        else:
            self.storage.append(data)

    def sample(self, batch_size):
        # 0부터 len(self.storage의 크기내에서 size 만큼 랜덤하게 값을 추출
        ind = np.random.randint(0, len(self.storage), size=batch_size)
        x, y, u, r, d = [], [], [], [], []

        for i in ind:
            X, Y, U, R, D = self.storage[i] # self.storage에 저장된 값들 중에서 랜덤으로 추출된 번호의 값을 가져옴
            x.append(np.array(X, copy=False))
            y.append(np.array(Y, copy=False))
            u.append(np.array(U, copy=False))
            r.append(np.array(R, copy=False))
            d.append(np.array(D, copy=False))
        return np.array(x), np.array(y), np.array(u), np.array(r).reshape(-1, 1), np.array(d).reshape(-1, 1)
        # reshape(-1, 1)을 통하여 얻는 것.
        # (3, ) 모양을 -> (3, 1)로 만들어줌.