import traceback

import lux
import pandas as pd
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
import random
from itertools import combinations



# df.intent=['ACTMedian']
def get_all_rec(rec_dict):
    all_rec = []
    for each in rec_dict:
        all_rec += rec_dict[each]
    return all_rec




def already_exist(lst, item):
    for each in lst:
        if str(each) == str(item):
            return 1
    else:
        return 0


# topk1:unexplored_intents类
# topk2:基于用户选择的推荐
# new_problem:这两个里可能有大量相同的recommendation

def rec_next_step(df, unexplored_intents, explored_intents, current_choice, top_k1, top_k2):
    # recommend related to explored (E)
    all_recommendation_E = []
    all_recommendation_E_afterdelete = []
    if current_choice != 'NULL':
        df.intent = current_choice

        for each in df.recommendation:
            all_recommendation_E += df.recommendation[each]

    # unexplored推荐
    all_recommendation_U = []
    for each in unexplored_intents:
        if str(each) in explored_intents:

            pass


        else:
            all_recommendation_U.append(each)

    # 删除掉已经explore过的：

    for each in all_recommendation_E:
        if str(each) in explored_intents:

            pass

        else:
            all_recommendation_E_afterdelete.append(each)

    # 排序
    all_recommendation_E_afterdelete.sort(key=lambda x: x.score, reverse=True)
    all_recommendation_U.sort(key=lambda x: x.score, reverse=True)

    return all_recommendation_U[:min(top_k1, len(all_recommendation_U))], all_recommendation_E_afterdelete[:min(top_k2,len(all_recommendation_E_afterdelete))]


def multiDF_rec(df_list, unexplored_intents, explored_intents, current_choice, top_k1, top_k2):
    U = []
    E = []
    for i in range(len(df_list)):
        try:
            rec_list = rec_next_step(df_list[i], unexplored_intents[i], explored_intents[i], current_choice[i], top_k1, top_k2)[0]
            rec_dict = [{'vis_obj': x, 'df_index': i} for x in rec_list]
            U += rec_dict
            rec_list = rec_next_step(df_list[i], unexplored_intents[i], explored_intents[i], current_choice[i], top_k1, top_k2)[1]
            rec_dict = [{'vis_obj': x, 'df_index': i} for x in rec_list]
            E += rec_dict
        except:
            traceback.print_exc()






    U.sort(key=lambda x: x['vis_obj'].score, reverse=True)
    E.sort(key=lambda x: x['vis_obj'].score, reverse=True)
    return U[:min(top_k1, len(U))], E[:min(top_k2, len(E))]  # 前一个是基于unexplored的推荐，后一个是基于current_choice的推荐
def lux_rec_test():
    rec = multiDF_rec(df_list, unexplored_intents, explored_intents, current_choice, top_k1, top_k2)
    print(rec)
    return rec

if __name__ == "__main__":
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/college.csv")
    new_df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/countries.csv")
    df_list = [df, new_df]

    unexplored_intents = [0 for i in range(len(df_list))]
    explored_intents = [0 for i in range(len(df_list))]
    current_choice = [0 for i in range(len(df_list))]
    for i in range(len(df_list)):
        unexplored_intents[i] = get_all_rec(df_list[i].recommendation)
        explored_intents[i] = []

        current_choice[i] = "NULL"
    top_k1 = 5
    top_k2 = 5



    print('lux_test')
    print(lux_rec_test())
    print('end')
    for i in range(10):
        print("第", i + 1, "次推荐")
        # rec=rec_next_step(new_df,unexplored_intents,explored_intents,current_choice,top_k1,top_k2)
        rec = multiDF_rec(df_list, unexplored_intents, explored_intents, current_choice, top_k1, top_k2)
        print('rec[0]')
        for each in rec[0]:
            print(each)
        print('rec[1]')
        for each in rec[1]:
            print(each)
        C = random.choice(rec[0] + rec[1])
        index = C['df_index']
        C_vis_obj = C['vis_obj']
        explored_intents[index].append(str(C_vis_obj))
        print('choose', C_vis_obj)
        current_choice[index] = C_vis_obj
        # print('explored_intents',explored_intents[-1])
        # if C in rec:
        #   print('remove_c')
        # rec.remove(C)

        # 从unexplored intents里面去掉C
        unexplored_intents[index] = [x for x in unexplored_intents[index] if str(x) != str(C_vis_obj)]

        # if already_exist(unexplored_intents,C):
        #   print('remove')
        #   unexplored_intents.remove(C)

        # 将推荐中未被选中的元素加入unexplored_intents（出现了莫名其妙bug）
        for each in rec:
            if already_exist(unexplored_intents, each):
                pass
            else:
                pass
        # unexplored_intents.append(each)
