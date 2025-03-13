from pm4py.objects.petri_net.obj import PetriNet

from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.discovery.ocel.ocdfg.variants import classic as ocdfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from enum import Enum
from collections import OrderedDict

from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from typing import Optional, Dict, Any
class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    DOUBLE_ARC_THRESHOLD = "double_arc_threshold"

#将csv转成json
# import pm4py
# ocel = pm4py.read_ocel("D:/OCEL/test_obj-centr-log_events.csv")
# from pm4py.objects.ocel.exporter.jsonocel import exporter
# target_path = "D:/OCEL/test_obj-centr-log_events_New.jsonocel"
# exporter.apply(ocel,target_path)
# import pm4py
# ocel = pm4py.read_ocel("D:/毕业论文/案例分析/日志/变体0-9子日志/PM4PY-隐私保护/sublog-递增变体/9660E_2415UO_12880Oevent_variant_[0].csv")
# from pm4py.objects.ocel.exporter.jsonocel import exporter
# target_path = "D:/毕业论文/案例分析/日志/变体0-9子日志/PM4PY-隐私保护/sublog-递增变体/9660E_2415UO_12880Oevent_variant_[0].jsonocel"
# exporter.apply(ocel,target_path)

#导入ocel日志，挖掘ocdfg
import pm4py
import pprint
import time
import os

# path = r"D:\Microsoft Edge-downloads\ocpa-main\sample_logs\csv\PE2-不合规\PE1-BPI2017-filtered-合规.jsonocel"
# path = "D:/OCEL/test_obj-centr-log_events.csv"
path = r"D:\OCEL\en_test_obj-centr-log_events.jsonocel"

ocel = pm4py.read_ocel(path)

start_time = time.time()

ocdfg = ocdfg_discovery.apply(ocel)
orign_ocpn = pm4py.discover_oc_petri_net(ocel)
pm4py.view_ocpn(orign_ocpn, format='svg')
#将每个类型的活动都以字典存储[{类型：活动}]，所有类型的字典都存在一个列表中

type_acts_dic_list = []
for ot in ocdfg["activities_ot"]["events"]:
    type_acts_result_dict = {}
    type_acts_result_dict = {ot: list(ocdfg["activities_ot"]["events"][ot].keys())} #用list()将字典视图改成后续方便处理的列表
    type_acts_dic_list.append(type_acts_result_dict)
    print(type_acts_result_dict) #打印每个字典
pprint.pprint(type_acts_dic_list) #打印列表

end_time = time.time()
execution_time_1 = end_time - start_time


#给定一个类型type_to_find，输出其与其他类型的交互活动，存储在字典shared_result_dict中
type_to_find = input("请输入选定的对象类型：")

start_time = time.time()

from collections import OrderedDict
shared_result_dict = OrderedDict()  # 嵌套字典用于存储结果
#找到指定类型的所有值并存储在字典中
for item in type_acts_dic_list:
    if type_to_find in item:
        values_to_find = set(item[type_to_find])
        break
else:
    values_to_find = set()  # 如果未找到匹配类型，则将其设置为空集合
if values_to_find:
    # 遍历列表中的其他字典，查找共享相同值的键
    for item in type_acts_dic_list:
        for key, values in item.items():
            if key != type_to_find:
                common_values = set(values).intersection(values_to_find)
                if common_values:
                    # 将共享的键值对添加到嵌套字典中
                    if type_to_find not in shared_result_dict:
                        shared_result_dict[type_to_find] = {}
                    if key not in shared_result_dict[type_to_find]:
                        shared_result_dict[type_to_find][key] = list(common_values)
                    else:
                        shared_result_dict[type_to_find][key].extend(common_values)
# 输出结果：
# {'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
#                     'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
# 输出结果
if shared_result_dict:
    pprint.pprint(shared_result_dict)
else:
    print(f"没有与 '{type_to_find}' 共享相同值的键。")

# 修正：确保 Create offer 作为起始活动
for outer_key, inner_dict in shared_result_dict.items():
    petri_nets = {}
    for inner_key, activities_list in inner_dict.items():
        # 获取参与协作类型的所有活动
        inner_activities = ocdfg["activities_ot"]["events"][inner_key]
        # 获取正确的 start 和 end 活动
        inner_start = ocdfg["start_activities"]["events"].get(inner_key, {})
        inner_end = ocdfg["end_activities"]["events"].get(inner_key, {})

        # 构造活动字典
        activities = {x: len(y) for x, y in inner_activities.items()}
        start_activities = {x: len(y) for x, y in inner_start.items()}
        end_activities = {x: len(y) for x, y in inner_end.items()}

        # 构造真实的 DFG
        dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"].get(inner_key, {}).items()}

        # 确保 Create offer 作为起始活动
        if "Create offer" in activities:
            if "Create offer" not in start_activities:
                start_activities["Create offer"] = 1  # 假设 Create offer 是起始活动
            if "Create offer" in dfg:
                # 确保 Create offer 的后续活动正确连接
                dfg = {k: v for k, v in dfg.items() if k[0] == "Create offer" or k[1] == "Create offer"}

        # 应用 Inductive Miner 挖掘 Petri 网
        petri_net = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
        petri_nets[inner_key] = petri_net
    petri_result_dict = petri_nets

# 外层(主类型Item)生成Petri网的字典,存储在petri_result_dict
# modified_result_dict = {}
petri_nets = {}
for outer_key in shared_result_dict:
    activities_eo = ocdfg["activities_ot"]["total_objects"][outer_key]
    activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][outer_key].items()}
    start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][outer_key].items()}
    end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][outer_key].items()}
    dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][outer_key].items()}
    petri_nets[outer_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
print("修改后的外层字典")
pprint.pprint(petri_nets)
petri_result_dict = petri_nets
print("修改后的")
pprint.pprint(petri_result_dict)


#内层生成Petri网的字典，存储在petri_result_dict
#ocdfg的协作类型的活动只包括共享变迁
for outer_key, inner_dict in shared_result_dict.items():
    for inner_key, inner_values in inner_dict.items():
        if inner_key in ocdfg['activities_ot']['events']:
            ocdfg['activities_ot']['events'][inner_key] = {
                value: ocdfg['activities_ot']['events'][inner_key][value]
                for value in inner_values
            }
#ocdfg的协作类型的开始和结束活动
# 源代码备份 ocdfg的开始和结束活动
# for outer_key, inner_dict in shared_result_dict.items():
#     for inner_key, activities_list in inner_dict.items():
#         if inner_key in ocdfg['start_activities']['events']:
#             # 检查活动个数
#             num_activities = len(activities_list)
#             if num_activities == 1:
#                 # 修改字典1中start_activities和end_activities的对应子键和子键值
#                 activity = activities_list[0]
#                 ocdfg['start_activities']['events'][inner_key] = {"VirtualStart": {'1'}}
#                 ocdfg['end_activities']['events'][inner_key] = {"VirtualEnd": {'1'}}
#             elif num_activities > 1:
#                 # 修改字典1中start_activities和end_activities的对应子键和子键值
#                 first_activity = activities_list[0]
#                 last_activity = activities_list[-1]
#                 ocdfg['start_activities']['events'][inner_key] = {first_activity: {'1'}}
#                 ocdfg['end_activities']['events'][inner_key] = {last_activity: {'1'}}
# # 输出修改后的字典1
# # pprint.pprint(ocdfg)

#修改：只包括一个活动，则该活动为ocdfg的开始和结束活动
for outer_key, inner_dict in shared_result_dict.items():
    for inner_key, activities_list in inner_dict.items():
        if inner_key in ocdfg['start_activities']['events']:
            # 检查活动个数
            num_activities = len(activities_list)
            if num_activities == 1:
                # 修改字典1中start_activities和end_activities的对应子键和子键值
                activity = activities_list[0]
                ocdfg['start_activities']['events'][inner_key] = {activity: {'1'}}
                ocdfg['end_activities']['events'][inner_key] = {activity: {'1'}}
            elif num_activities > 1:
                # 修改字典1中start_activities和end_activities的对应子键和子键值
                first_activity = activities_list[0]
                last_activity = activities_list[-1]
                ocdfg['start_activities']['events'][inner_key] = {first_activity: {'1'}}
                ocdfg['end_activities']['events'][inner_key] = {last_activity: {'1'}}
print("只包括一个活动的dfg")
pprint.pprint(ocdfg)

"""#源代码备份，最终的petri网
for outer_key, inner_dict in shared_result_dict.items():
    modified_result_dict = {}
    for inner_key,activities_list in inner_dict.items():
        activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][inner_key].items()}
        print(inner_key+"的activities为：")
        pprint.pprint(activities)
        start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][inner_key].items()}
        end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][inner_key].items()}
        print(inner_key + "的start_activities为：")
        pprint.pprint(start_activities)
        print(inner_key + "的end_activities为：")
        pprint.pprint(end_activities)
        activity_pairs = {}
        # activity_pairs = OrderedDict()
        if len(activities_list) == 1:
            # 如果活动列表只包含一个活动，添加虚拟开始和虚拟结束节点
            st_activities = "VirtualStart"
            en_activities = "VirtualEnd"
            activities["VirtualStart"] = 1
            activities["VirtualEnd"] = 1
            activity_pairs[(st_activities, activities_list[0])] = 1
            activity_pairs[(activities_list[0], en_activities)] = 1
        elif len(activities_list) > 1:
            for i in range(len(activities_list) - 1):
                st_activities = activities_list[i]
                en_activities = activities_list[i + 1]
                activity_pair = (st_activities, en_activities)
                if activity_pair in activity_pairs:
                    activity_pairs[activity_pair] += 1
                else:
                    activity_pairs[activity_pair] = 1
        print(inner_key + "的dfg结果为：")
        dfg = {x: 1 for x, y in activity_pairs.items()}  # 将频次设置为1
        # pprint.pprint(dfg)
        print(inner_key + "的Petri网结果为：")
        petri_nets[inner_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
    petri_result_dict = petri_nets
print("最终的Petri网结果为：")

# pprint.pprint(petri_result_dict)
# pm4py.view_ocpn(petri_result_dict, format='svg')
"""
#修改：只有一个活动时，设置事件对为空即可
for outer_key, inner_dict in shared_result_dict.items():
    modified_result_dict = {}
    for inner_key,activities_list in inner_dict.items():
        activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][inner_key].items()}
        print(inner_key+"的activities为：")
        pprint.pprint(activities)
        start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][inner_key].items()}
        end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][inner_key].items()}
        print(inner_key + "的start_activities为：")
        pprint.pprint(start_activities)
        print(inner_key + "的end_activities为：")
        pprint.pprint(end_activities)
        activity_pairs = {}
        # activity_pairs = OrderedDict()
        if len(activities_list) == 1:
            # 如果活动列表只包含一个活动，设置活动对为空
            activity_pairs={}
        else:
            for i in range(len(activities_list) - 1):
                st_activities = activities_list[i]
                en_activities = activities_list[i + 1]
                activity_pair = (st_activities, en_activities)
                if activity_pair in activity_pairs:
                    activity_pairs[activity_pair] += 1
                else:
                    activity_pairs[activity_pair] = 1
        # print(inner_key + "的dfg结果为：")
        dfg = {x: 1 for x, y in activity_pairs.items()}  # 将频次设置为1
        # pprint.pprint(dfg)
        # print(inner_key + "的Petri网结果为：")
        petri_nets[inner_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
    petri_result_dict = petri_nets
# print("最终的Petri网结果为：")
# pprint.pprint(petri_result_dict)
# pm4py.view_ocpn(petri_result_dict, format='svg')
"""



"""#源代码：完整的ocpn及可视化
# #创建一个ocpn字典
# ocpn = {}
# #外层+内层活动：
# activities = set()
# for outkey, inner_dict in shared_result_dict.items():
#     activities = {x for x in ocdfg["activities_ot"]["events"][outer_key].keys()}
#     for inner_key,activity_list in inner_dict.items():
#         activities.update({x for x in ocdfg["activities_ot"]["events"][inner_key].keys()})
#         if len(activity_list) == 1:
#             activities.add("VirtualStart")
#             activities.add("VirtualEnd")
# ocpn["activities"] = activities
# # pprint.pprint(ocpn)
# #活动类型：
# ocpn["activities_ot"] = ocdfg["activities_ot"]
# # pprint.pprint(ocpn)
# #双边活动：
# ocpn["double_arcs_on_activity"] = {}  # 创建 double_arcs_on_activity 子字典
# for outer_key, inner_dict in shared_result_dict.items():
#     # 复制 orign_ocpn 中的值到 ocpn
#     if outer_key in orign_ocpn.get("double_arcs_on_activity", {}):
#         ocpn["double_arcs_on_activity"][outer_key] = orign_ocpn["double_arcs_on_activity"][outer_key]
#     else:
#         ocpn["double_arcs_on_activity"][outer_key] = {}
#
#     for inner_key, activity_list in inner_dict.items():
#         ocpn["double_arcs_on_activity"][inner_key] = {}
#         for activity in activity_list:
#             if inner_key in orign_ocpn.get("double_arcs_on_activity", {}) and activity in orign_ocpn["double_arcs_on_activity"][inner_key]:
#                 # 如果 inner_key 和 activity 存在于 orign_ocpn 中，则将其值复制到 ocpn
#                 ocpn["double_arcs_on_activity"][inner_key][activity] = orign_ocpn["double_arcs_on_activity"][inner_key][activity]
#             else:
#                 # 否则，可以设置默认值或者执行其他逻辑
#                 ocpn["double_arcs_on_activity"][inner_key][activity] = "default_value"
# # pprint.pprint(ocpn)
# #边：
# ocpn["edges"] = {"event_couples":{}}
# for outer_key, inner_dict in shared_result_dict.items():
#     if outer_key in orign_ocpn["edges"].get("event_couples", {}):
#         ocpn["edges"]["event_couples"][outer_key] = orign_ocpn["edges"]["event_couples"][outer_key]
#     else:
#         ocpn["edges"]["event_couples"][outer_key] = {}
#     for inner_key, activity_list in inner_dict.items():
#         if inner_key in orign_ocpn["edges"].get("event_couples", {}).get(outer_key, {}):
#             ocpn["edges"]["event_couples"][outer_key] = orign_ocpn["edges"]["event_couples"][outer_key]
#         else:
#             activity_pairs = {}
#             if len(activity_list) == 1:
#                 # 如果活动列表只包含一个活动，添加虚拟开始和虚拟结束节点
#                 st_activities = "VirtualStart"
#                 en_activities = "VirtualEnd"
#                 activity_pairs[(st_activities, activity_list[0])] = 1
#                 activity_pairs[(activity_list[0], en_activities)] = 1
#             elif len(activity_list) > 1:
#                 for i in range(len(activity_list) - 1):
#                     st_activities = activity_list[i]
#                     en_activities = activity_list[i + 1]
#                     activity_pair = (st_activities, en_activities)
#                     if activity_pair in activity_pairs:
#                         activity_pairs[activity_pair] += 1
#                     else:
#                         activity_pairs[activity_pair] = 1
#             ocpn["edges"]["event_couples"][inner_key] = activity_pairs
# # pprint.pprint(ocpn)
# #结束活动：
# ocpn["end_activities"] = {}
# ocpn["end_activities"]["events"] = {}
# for outer_key,inner_dict in shared_result_dict.items():
#     if outer_key in orign_ocpn["end_activities"].get("events", {}) :
#         ocpn["end_activities"]["events"][outer_key] = orign_ocpn["end_activities"]["events"][outer_key]
#     else:
#         ocpn["end_activities"]["events"][outer_key] = {}
#     for inner_key,activity_list in inner_dict.items():
#         ocpn["end_activities"]["events"][inner_key] = {}
#         if len(activities_list) == 1:
#             en_activities = "VirtualEnd"
#             ocpn["end_activities"]["events"][inner_key] = {en_activities:1}
#         elif len(activities_list) > 1:
#             print("Debug: activities_list for", inner_key, "is", activities_list)
#             ocpn["end_activities"]["events"][inner_key] = {x: 1 for x in ocdfg["end_activities"]["events"][inner_key].keys()}
# # pprint.pprint(ocpn)
#
# #开始活动：
# ocpn["start_activities"] = {}
# ocpn["start_activities"]["events"] = {}
# for outer_key,inner_dict in shared_result_dict.items():
#     if outer_key in orign_ocpn["start_activities"].get("events", {}) :
#         ocpn["start_activities"]["events"][outer_key] = orign_ocpn["start_activities"]["events"][outer_key]
#     else:
#         ocpn["start_activities"]["events"][outer_key] = {}
#     for inner_key,activity_list in inner_dict.items():
#         ocpn["start_activities"]["events"][inner_key] = {}
#         if len(activities_list) == 1:
#             sn_activities = "VirtualStart"
#             ocpn["start_activities"]["events"][inner_key] = {sn_activities:1}
#         elif len(activities_list) > 1:
#             ocpn["start_activities"]["events"][inner_key] = {x: 1 for x in ocdfg["start_activities"]["events"][inner_key].keys()}
# # pprint.pprint(ocpn)
#
# #对象类型：
# oc_type = set()
# for outer_key, inner_dict in shared_result_dict.items():
#     oc_type.add(outer_key)
#     for inner_key in inner_dict:
#         oc_type.add(inner_key)
# print(oc_type)
# ocpn["object_types"] = set()
# ocpn["object_types"] = oc_type
# #Petri网
# ocpn["petri_nets"] = petri_result_dict
# pprint.pprint(ocpn)
# pm4py.view_ocpn(ocpn, format='svg')
#
#
# #其他内容都没变，最后把wo删掉，把稍后替换改成wo就行！！！
# # pm4py.view_ocpn




#修改：只有一个活动时，指向自己
#创建一个ocpn字典
ocpn = {}
#外层+内层活动：
activities = set()
for outkey, inner_dict in shared_result_dict.items():
    activities = {x for x in ocdfg["activities_ot"]["events"][outer_key].keys()}
    for inner_key,activity_list in inner_dict.items():
        activities.update({x for x in ocdfg["activities_ot"]["events"][inner_key].keys()})
ocpn["activities"] = activities
# pprint.pprint(ocpn)
#活动类型：
ocpn["activities_ot"] = ocdfg["activities_ot"]
# pprint.pprint(ocpn)
#双边活动：
ocpn["double_arcs_on_activity"] = {}  # 创建 double_arcs_on_activity 子字典
for outer_key, inner_dict in shared_result_dict.items():
    # 复制 orign_ocpn 中的值到 ocpn
    if outer_key in orign_ocpn.get("double_arcs_on_activity", {}):
        ocpn["double_arcs_on_activity"][outer_key] = orign_ocpn["double_arcs_on_activity"][outer_key]
    else:
        ocpn["double_arcs_on_activity"][outer_key] = {}

    for inner_key, activity_list in inner_dict.items():
        ocpn["double_arcs_on_activity"][inner_key] = {}
        for activity in activity_list:
            if inner_key in orign_ocpn.get("double_arcs_on_activity", {}) and activity in orign_ocpn["double_arcs_on_activity"][inner_key]:
                # 如果 inner_key 和 activity 存在于 orign_ocpn 中，则将其值复制到 ocpn
                ocpn["double_arcs_on_activity"][inner_key][activity] = orign_ocpn["double_arcs_on_activity"][inner_key][activity]
            else:
                # 否则，可以设置默认值或者执行其他逻辑
                ocpn["double_arcs_on_activity"][inner_key][activity] = "default_value"
# pprint.pprint(ocpn)
#边：
ocpn["edges"] = {"event_couples":{}}
for outer_key, inner_dict in shared_result_dict.items():
    if outer_key in orign_ocpn["edges"].get("event_couples", {}):
        ocpn["edges"]["event_couples"][outer_key] = orign_ocpn["edges"]["event_couples"][outer_key]
    else:
        ocpn["edges"]["event_couples"][outer_key] = {}
    for inner_key, activity_list in inner_dict.items():
        if inner_key in orign_ocpn["edges"].get("event_couples", {}).get(outer_key, {}):
            ocpn["edges"]["event_couples"][outer_key] = orign_ocpn["edges"]["event_couples"][outer_key]
        else:
            activity_pairs = {}
            if len(activity_list) == 1:
                # 如果活动列表只包含一个活动，添加虚拟开始和虚拟结束节点
                activity_pairs = {}
            elif len(activity_list) > 1:
                for i in range(len(activity_list) - 1):
                    st_activities = activity_list[i]
                    en_activities = activity_list[i + 1]
                    activity_pair = (st_activities, en_activities)
                    if activity_pair in activity_pairs:
                        activity_pairs[activity_pair] += 1
                    else:
                        activity_pairs[activity_pair] = 1
            ocpn["edges"]["event_couples"][inner_key] = activity_pairs
# pprint.pprint(ocpn)
#结束活动：
ocpn["end_activities"] = {}
ocpn["end_activities"]["events"] = {}
for outer_key,inner_dict in shared_result_dict.items():
    if outer_key in orign_ocpn["end_activities"].get("events", {}) :
        ocpn["end_activities"]["events"][outer_key] = orign_ocpn["end_activities"]["events"][outer_key]
    else:
        ocpn["end_activities"]["events"][outer_key] = {}
    for inner_key,activity_list in inner_dict.items():
        ocpn["end_activities"]["events"][inner_key] = {}
        if len(activities_list) == 1:
            ocpn["end_activities"]["events"][inner_key] = ocdfg["end_activities"]["events"][inner_key]
        elif len(activities_list) > 1:
            print("Debug: activities_list for", inner_key, "is", activities_list)
            ocpn["end_activities"]["events"][inner_key] = {x: 1 for x in ocdfg["end_activities"]["events"][inner_key].keys()}
# pprint.pprint(ocpn)

#开始活动：
ocpn["start_activities"] = {}
ocpn["start_activities"]["events"] = {}
for outer_key,inner_dict in shared_result_dict.items():
    if outer_key in orign_ocpn["start_activities"].get("events", {}) :
        ocpn["start_activities"]["events"][outer_key] = orign_ocpn["start_activities"]["events"][outer_key]
    else:
        ocpn["start_activities"]["events"][outer_key] = {}
    for inner_key,activity_list in inner_dict.items():
        ocpn["start_activities"]["events"][inner_key] = {}
        if len(activities_list) == 1:
            ocpn["start_activities"]["events"][inner_key] = ocdfg["start_activities"]["events"][inner_key]
        elif len(activities_list) > 1:
            ocpn["start_activities"]["events"][inner_key] = {x: 1 for x in ocdfg["start_activities"]["events"][inner_key].keys()}
# pprint.pprint(ocpn)

#对象类型：
oc_type = set()
for outer_key, inner_dict in shared_result_dict.items():
    oc_type.add(outer_key)
    for inner_key in inner_dict:
        oc_type.add(inner_key)
print(oc_type)
ocpn["object_types"] = set()
ocpn["object_types"] = oc_type
#Petri网
ocpn["petri_nets"] = petri_result_dict
pprint.pprint(ocpn)
pm4py.view_ocpn(ocpn, format='svg')

end_time = time.time()
execution_time_2 = end_time - start_time
execution_time = execution_time_1 + execution_time_2
print(execution_time)
#找到只有一个活动的对象类型
#修改其Petri网字典
#针对库所：删掉除sink和source外的所有库所




