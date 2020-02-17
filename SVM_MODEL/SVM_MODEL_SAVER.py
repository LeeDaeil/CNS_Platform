import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn import svm


# 데이터 로드
data = pd.read_csv('SVM_PT_DATA.csv', header=None)

X = data.loc[:, 0:1].values
y = data[2].values

# 스케일러 로드
scaler = MinMaxScaler()
scaler.fit(X)
X = scaler.transform(X)

# SVM 훈련
svc = svm.SVC(kernel='rbf', gamma='auto', C=1000)
svc.fit(X, y)

# 훈련된 SVM 및 스케일러 저장.
with open('SVM_MODLE.bin', 'wb') as f:
    pickle.dump([svc, scaler], f)
