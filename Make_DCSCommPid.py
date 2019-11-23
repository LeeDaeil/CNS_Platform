## DCSCommPid.ini 만드는 기능


# all para
# with open('./db.txt', 'r') as f:
#     nub_line = -1
#     while True:
#         temp_ = f.readline().split('\t')
#         if temp_[0] == '':
#             break
#         if nub_line != -1:  # 첫번째 헤더의 내용 제외하고 추가
#             with open('./DCSCommPid.ini', 'a') as f_pid:
#                 if nub_line == 0:
#                     f_pid.write('{}\t{}\t{}'.format(nub_line, temp_[0], temp_[1]))
#                 else:
#                     f_pid.write('\n{}\t{}\t{}'.format(nub_line, temp_[0], temp_[1]))
#         nub_line += 1

# 용역용
selected_para = []
with open('./용역para.txt', 'r') as f:
    while True:
        temp = f.readline().split('\n')[0]
        if temp == '':
            break
        selected_para.append(temp)
print(selected_para[0:4])
tot_para = {}
with open('./db.txt', 'r') as f:
    nub_line = -1
    while True:
        temp_ = f.readline().split('\t')
        if temp_[0] == '':
            break
        if nub_line != -1:  # 첫번째 헤더의 내용 제외하고 추가
            tot_para[temp_[0]] = temp_[1]
        nub_line += 1

with open('./DCSCommPid.ini', 'a') as f_pid:
    for line_nub in range(0, len(selected_para)):
        print(selected_para[0], tot_para[selected_para[0]])
        if line_nub == 0:
            f_pid.write('{}\t{}\t{}'.format(line_nub, selected_para[line_nub], tot_para[selected_para[line_nub]]))
        else:
            f_pid.write('\n{}\t{}\t{}'.format(line_nub, selected_para[line_nub], tot_para[selected_para[line_nub]]))