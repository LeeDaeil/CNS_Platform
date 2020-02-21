import pandas as pd


# 전략 설정 기능 Case OPStrategy
Normal = 'Normal'
Abnormal = 'Abnormal'
Emergency = 'Emergency'

# 출력 증가 Case ST_OPStratey
PZR_OP = 'PZR_OP'
ST_OP = 'ST_OP'
Full_op = 'Full_OP'

# 제어 HIS
temp = pd.read_csv('CONT_HIS_DUMY.csv')
HIS_CONT = temp
#print(HIS_CONT[11])