# coding: utf-8

ans_10 = [[4, 3, 2, 1], [2, 1, 3, 4], [1, 2, 4, 3], [3, 4, 1, 2]]
ans_10_list = []
for i in range(len(ans_10)):
    for j in range(len(ans_10[0])):
        ans_10_list.append(ans_10[i][j])

def low_judge(ans_10_list):
    for i in range(0, 16, 4):
        if len(list(set(ans_10_list[i:i+4]))) < 4:
            return False
    return True

def line_judge(ans_10_list):
    for i in range(0,4):
        get_line = []
        for j in range(i,16,4):
            get_line.append(ans_10_list[j])
        if len(list(set(get_line))) < 4:
            return False
        else:
            pass
    return True

def box_judge(ans_10_list):
    split_ans = []
    for i in range(0, len(ans_10_list), 2):
        split_ans.append([ans_10_list[i], ans_10_list[i+1]])
    for i in range(0, 2):
        get_box = split_ans[i] + split_ans[i+2]
        if len(list(set(get_box))) < 4:
            return False
        else:
            pass
    for i in range(4, 6):
        get_box = split_ans[i] + split_ans[i+2]
        if len(list(set(get_box))) < 4:
            return False
        else:
            pass
    return True

judgeA = low_judge(ans_10_list)
judgeB = line_judge(ans_10_list)
judgeC = box_judge(ans_10_list)