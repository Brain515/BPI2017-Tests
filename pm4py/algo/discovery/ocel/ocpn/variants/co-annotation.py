from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.discovery.ocel.ocdfg.variants import classic as ocdfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from typing import Optional, Dict, Any

class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    DOUBLE_ARC_THRESHOLD = "double_arc_threshold"


''' #测试OCEL日志的格式
# import pprint
# import pm4py
# path = "D:/OCEL/日志/test_obj-centr-log_events.csv"
# ocel = pm4py.read_ocel(path)
# pprint.pprint(ocel) #输出ocel
# """
# Object-Centric Event Log (number of events: 21, number of objects: 12, number of activities: 11, number of object types: 5, events-objects relationships: 40)
# Activities occurrences: {'Unpack': 5, 'Create Order': 2, 'Place SO': 2, 'Create Invoice': 2, 'Receive SO': 2, 'Pack Shipment': 2, 'Ship': 2, 'Update SO': 1, 'Update Invoice': 1, 'Receive Payment': 1, 'Clear Invoice': 1}
# Object types occurrences (number of objects): {'Item': 5, 'Supplier Order': 2, 'Invoice': 2, 'Order': 2, 'Payment': 1}
# """
# event_data = ocel.get_extended_table()
# print(event_data) #输出ocel的csv表格
'''


#******
    #测试1：ocel存储格式转换成OCdfg字典后的具体内容
# import pm4py
# import pprint
# # path = "D:\OCEL\日志\obj-centr-log.jsonocel"
# path = "D:/OCEL/日志/test_obj-centr-log_events.csv"
# ocel = pm4py.read_ocel(path)
# ocdfg = ocdfg_discovery.apply(ocel)
# output_str = pprint.pformat(ocdfg)
# ocpn = pm4py.discover_oc_petri_net(ocel)
# pm4py.view_ocpn(ocpn, format='svg') #可视化输出
# with open(r'C:\Users\lenovo\Desktop\output.txt', 'w') as file:
#     file.write(output_str)
# with open(r'C:\Users\lenovo\Desktop\test_output.txt', 'w') as file:
#     file.write(output_str)
    #测试1结果：得到OCDFG嵌套字典的所有内容
#******


# 给定目标类型，输出该类型的petri网字典
# def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None, target_type: str = "") -> Dict[str, Any]:
#     if parameters is None:
#         parameters = {}
#         # 使用exec_utils模块中的get_param_value函数，从参数字典中获取Parameters.DOUBLE_ARC_THRESHOLD对应的值，如果不存在，默认为0.0
#         # 此阈值在后续的步骤中用于判断是否添加“双弧”
#     double_arc_threshold = exec_utils.get_param_value(Parameters.DOUBLE_ARC_THRESHOLD, parameters, 0.0)
#     ocdfg = ocdfg_discovery.apply(ocel, parameters=parameters)
#
#     petri_nets = {}
#     double_arcs_on_activity = {}
#
#     result = {}
#
#     #找到目标类型
#     for ot in ocdfg["object_types"]:
#         if ot == target_type:
#             activities_eo = ocdfg["activities_ot"]["total_objects"][ot]
#             activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][ot].items()}
#             start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][ot].items()}
#             end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][ot].items()}
#             dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][ot].items()}
#             is_activity_double = {}
#             for act in activities_eo:
#                 ev_obj_count = Counter()
#                 for evc in activities_eo[act]:
#                     ev_obj_count[evc[0]] += 1
#                 this_single_amount = len(list(x for x in ev_obj_count if ev_obj_count[x] == 1)) / len(ev_obj_count)
#                 if this_single_amount <= double_arc_threshold:
#                     is_activity_double[act] = True
#                 else:
#                     is_activity_double[act] = False
#             double_arcs_on_activity[ot] = is_activity_double
#             petri_nets[ot] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
#******

    #测试2:如何找到共享变迁？
    #思路：找到该类型的所有活动，遍历每个活动，判断该活动是否被其他类型使用，若使用则

# {ocdfg:{"activities_ot":{"events":{"ocel:type:Invoice":{"clear":{'e30'},'create':{'e18','e20'}},
#                            "ocel:type:Item":{"pick":{'e10'},"pack":{"e20"}}
#                            }
#                  }}}



# '''
import pm4py
import pprint
path = "D:\OCEL\日志\obj-centr-log.jsonocel"
ocel = pm4py.read_ocel(path)
ocdfg = ocdfg_discovery.apply(ocel)

#测试：找到该类型的所有活动
# result_set = set()
# target_ot = "ocel:type:Supplier Order"
# if target_ot in ocdfg["activities_ot"]["events"]:
#     result_set.update(ocdfg["activities_ot"]["events"][target_ot].keys())
# print(result_set)

#测试：将每个类型的活动都以字典存储{类型：活动}，并将所有类型的字典存在一个列表中
dic_list = []
for ot in ocdfg["activities_ot"]["events"]:
    result_dict = {}
    result_dict = {ot: list(ocdfg["activities_ot"]["events"][ot].keys())} #用list()将字典视图改成后续方便处理的列表
    dic_list.append(result_dict)
    print(result_dict) #打印每个字典
pprint.pprint(dic_list) #打印列表
print("******")


#实现给定一个对象类型，即可输出该类型与其他类型的交互活动
#判断给定类型与其他类型是否有交互活动，若有则给出活动名
#type_to_find = 'ocel:type:Item' #改成人机交互，要求输入type_to_find，自动输出结果
type_to_find = input("请输入选定的对象类型：")
from collections import OrderedDict
shared_result_dict = OrderedDict()  # 嵌套字典用于存储结果
#找到指定类型的所有值并存储在字典中
for item in dic_list:
    if type_to_find in item:
        values_to_find = set(item[type_to_find])
        break
else:
    values_to_find = set()  # 如果未找到匹配类型，则将其设置为空集合
if values_to_find:
    # 遍历列表中的其他字典，查找共享相同值的键
    for item in dic_list:
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
if shared_result_dict:
    pprint.pprint(shared_result_dict)
else:
    print(f"没有与 '{type_to_find}' 共享相同值的键。")
print("*******")



#测试3，生成Petri网的字典，存储在字典petri_result_dict中
#先生成外层Petri网：输出结果如下
#{'ocel:type:Item': {'ocel:type:Item': (places: [ p_3, p_4, sink, source ]
# transitions: [ (1f49a271-9427-4b14-b8b3-0cb4d135e158, 'Unpack'), (b83fb725-47be-423b-bce0-3d78614a6848, 'Receive SO'), (c3850c6e-51f6-492a-9013-17a79a8ac399, 'Pack Shipment') ]
# arcs: [ (1f49a271-9427-4b14-b8b3-0cb4d135e158, 'Unpack')->p_4, (b83fb725-47be-423b-bce0-3d78614a6848, 'Receive SO')->p_3, (c3850c6e-51f6-492a-9013-17a79a8ac399, 'Pack Shipment')->sink, p_3->(1f49a271-9427-4b14-b8b3-0cb4d135e158, 'Unpack'), p_4->(c3850c6e-51f6-492a-9013-17a79a8ac399, 'Pack Shipment'), source->(b83fb725-47be-423b-bce0-3d78614a6848, 'Receive SO') ],
#                                        ['source:1'],
#                                        ['sink:1'])}}
modified_result_dict = {}
for outer_key in shared_result_dict:
    #outer_key要能挖掘出完整的dfg和Petri网：
    petri_nets = {}
    activities_eo = ocdfg["activities_ot"]["total_objects"][outer_key]
    activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][outer_key].items()}
    #print("activities为:")#{'Receive SO': 2, 'Unpack': 5, 'Pack Shipment': 2}
    start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][outer_key].items()}
    end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][outer_key].items()}
    dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][outer_key].items()}
    #print("测试此时dfg结果") #{('Receive SO', 'Unpack'): 5, ('Unpack', 'Pack Shipment'): 5}
    petri_nets[outer_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
    modified_result_dict[outer_key] = petri_nets
petri_result_dict = modified_result_dict
pprint.pprint(petri_result_dict)
#{'ocel:type:Item': {'ocel:type:Item': (places: [ p_3, p_4, sink, source ]
# transitions: [ (d2e5ae55-2435-4157-8398-94cb5d6a6464, 'Unpack'), (ef6a4151-1e59-40ff-8952-acf7a5994dd7, 'Pack Shipment'), (f87e0332-144b-438d-9170-42ded6601abc, 'Receive SO') ]
# arcs: [ (d2e5ae55-2435-4157-8398-94cb5d6a6464, 'Unpack')->p_4, (ef6a4151-1e59-40ff-8952-acf7a5994dd7, 'Pack Shipment')->sink, (f87e0332-144b-438d-9170-42ded6601abc, 'Receive SO')->p_3, p_3->(d2e5ae55-2435-4157-8398-94cb5d6a6464, 'Unpack'), p_4->(ef6a4151-1e59-40ff-8952-acf7a5994dd7, 'Pack Shipment'), source->(f87e0332-144b-438d-9170-42ded6601abc, 'Receive SO') ],
#                                        ['source:1'],
#                                        ['sink:1'])}}
print("******")




# 输出结果oce
# {'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
#                     'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
#内层测试：通过遍历，匹配dfg，然后过滤
# dict_A = {'outer_key_1': {'inner_key_1': 'value_1', 'inner_key_2': 'value_2'},
#           'outer_key_2': {'inner_key_3': 'value_3'}}
#
# dict_B = {'outer_key_1': {'inner_key_1': 'new_value', 'inner_key_2': 'value_4'},
#           'outer_key_2': {'inner_key_3': 'new_value'}}
#
# # 使用嵌套字典推导，将B中与A键相同的值修改为A键的值
# dict_B = {outer_key: {inner_key: dict_A[outer_key][inner_key] if outer_key in dict_A and inner_key in dict_A[outer_key] else value
#                      for inner_key, value in inner_dict.items()}
#           for outer_key, inner_dict in dict_B.items()}
#
# pprint.pprint(dict_B)
# activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][outer_key].items()}
# '''



#******测试3：根据协作类型的活动结果，修改ocdfg，并生成相应的Petri网结果。



#测试：给定两个字典，修改协作类型Order和Supplier Order的ocdfg字典中的活动，存储在dict1中
dict1 = {'activities_ot': {'events': {'ocel:type:Invoice': {'Clear Invoice': {'e30'},
                                                    'Create Invoice': {'e18',
                                                                       'e5'},
                                                    'Update Invoice': {'e9'}},
                              'ocel:type:Item': {'Pack Shipment': {'e27',
                                                                   'e33'},
                                                 'Receive SO': {'e6', 'e19'},
                                                 'Unpack': {'e10',
                                                            'e11',
                                                            'e20',
                                                            'e21',
                                                            'e8'}},
                              'ocel:type:Order': {'Create Invoice': {'e18',
                                                                     'e5'},
                                                  'Create Order': {'e2', 'e1'},
                                                  'Pack Shipment': {'e27',
                                                                    'e33'},
                                                  'Ship': {'e28', 'e34'},
                                                  'Update SO': {'e7'}},
                              'ocel:type:Payment': {'Clear Invoice': {'e30'},
                                                    'Receive Payment': {'e29'}},
                              'ocel:type:Supplier Order': {'Place SO': {'e3',
                                                                        'e4'},
                                                           'Receive SO': {'e19',
                                                                          'e6'},
                                                           'Unpack': {'e10',
                                                                      'e11',
                                                                      'e20',
                                                                      'e21',
                                                                      'e8'},
                                                           'Update SO': {'e7'}}}}}
dict2={'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
                    'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
#将ocdfg中，与Item类型协作的类型的活动进行修改，变成只包括共享变迁。
for outer_key, inner_dict in dict2.items():
    for inner_key, inner_values in inner_dict.items():
        if inner_key in dict1['activities_ot']['events']:
            dict1['activities_ot']['events'][inner_key] = {
                value: dict1['activities_ot']['events'][inner_key][value]
                for value in inner_values
            }
#打印修改后的第一个字典
pprint.pprint(dict1)



#测试：修改协作类型的开始和结束活动，并存在dict3中
dict3 = {'start_activities': {'events': {'ocel:type:Invoice': {'Create Invoice': {'e18',
                                                                          'e5'}},
                                 'ocel:type:Item': {'Receive SO': {'e19',
                                                                   'e6'}},
                                 'ocel:type:Order': {'Create Order': {'e1',
                                                                      'e2'}},
                                 'ocel:type:Payment': {'Receive Payment': {'e29'}},
                                 'ocel:type:Supplier Order': {'Place SO': {'e3',
                                                                           'e4'}}},
                      'total_objects': {'ocel:type:Invoice': {'Create Invoice': {('e18',
                                                                                  'I1'),
                                                                                 ('e5',
                                                                                  'I2')}},
                                        'ocel:type:Item': {'Receive SO': {('e19',
                                                                           'Y1'),
                                                                          ('e19',
                                                                           'Y2'),
                                                                          ('e6',
                                                                           'X1'),
                                                                          ('e6',
                                                                           'X2'),
                                                                          ('e6',
                                                                           'X3')}},
                                        'ocel:type:Order': {'Create Order': {('e1',
                                                                              'O1'),
                                                                             ('e2',
                                                                              'O2')}},
                                        'ocel:type:Payment': {'Receive Payment': {('e29',
                                                                                   'P1')}},
                                        'ocel:type:Supplier Order': {'Place SO': {('e3',
                                                                                   'A'),
                                                                                  ('e4',
                                                                                   'B')}}},
                      'unique_objects': {'ocel:type:Invoice': {'Create Invoice': {'I1',
                                                                                  'I2'}},
                                         'ocel:type:Item': {'Receive SO': {'X1',
                                                                           'X2',
                                                                           'X3',
                                                                           'Y1',
                                                                           'Y2'}},
                                         'ocel:type:Order': {'Create Order': {'O1',
                                                                              'O2'}},
                                         'ocel:type:Payment': {'Receive Payment': {'P1'}},
                                         'ocel:type:Supplier Order': {'Place SO': {'A',
                                                                                   'B'}}}},
         'end_activities': {'events': {'ocel:type:Invoice': {'Clear Invoice': {'e30'}},
                                       'ocel:type:Item': {'Pack Shipment': {'e27',
                                                                            'e33'}},
                                       'ocel:type:Order': {'Ship': {'e28', 'e34'}},
                                       'ocel:type:Payment': {'Clear Invoice': {'e30'}},
                                       'ocel:type:Supplier Order': {'Unpack': {'e11',
                                                                               'e21'}}},
                            'total_objects': {'ocel:type:Invoice': {'Clear Invoice': {('e30',
                                                                                       'I1'),
                                                                                      ('e30',
                                                                                       'I2')}},
                                              'ocel:type:Item': {'Pack Shipment': {('e27',
                                                                                    'X1'),
                                                                                   ('e27',
                                                                                    'X2'),
                                                                                   ('e27',
                                                                                    'Y1'),
                                                                                   ('e33',
                                                                                    'X3'),
                                                                                   ('e33',
                                                                                    'Y2')}},
                                              'ocel:type:Order': {'Ship': {('e28',
                                                                            'O1'),
                                                                           ('e34',
                                                                            'O2')}},
                                              'ocel:type:Payment': {'Clear Invoice': {('e30',
                                                                                       'P1')}},
                                              'ocel:type:Supplier Order': {'Unpack': {('e11',
                                                                                       'A'),
                                                                                      ('e21',
                                                                                       'B')}}},
                            'unique_objects': {'ocel:type:Invoice': {'Clear Invoice': {'I1',
                                                                                       'I2'}},
                                               'ocel:type:Item': {'Pack Shipment': {'X1',
                                                                                    'X2',
                                                                                    'X3',
                                                                                    'Y1',
                                                                                    'Y2'}},
                                               'ocel:type:Order': {'Ship': {'O1',
                                                                            'O2'}},
                                               'ocel:type:Payment': {'Clear Invoice': {'P1'}},
                                               'ocel:type:Supplier Order': {'Unpack': {'A',
                                                                                       'B'}}}}
         }
dict2={'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
                    'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
for outer_key, inner_dict in dict2.items():
    for inner_key, activities_list in inner_dict.items():
        if inner_key in dict3['start_activities']['events']:
            # 检查活动个数
            num_activities = len(activities_list)
            if num_activities == 1:
                # 修改字典1中start_activities和end_activities的对应子键和子键值
                activity = activities_list[0]
                dict3['start_activities']['events'][inner_key] = {"VirtualStart": {'1'}}
                dict3['end_activities']['events'][inner_key] = {"VirtualEnd": {'1'}}
            elif num_activities > 1:
                # 修改字典1中start_activities和end_activities的对应子键和子键值
                first_activity = activities_list[0]
                last_activity = activities_list[-1]
                dict3['start_activities']['events'][inner_key] = {first_activity: {'1'}}
                dict3['end_activities']['events'][inner_key] = {last_activity: {'1'}}
# 输出修改后的字典1
pprint.pprint(dict3)


#dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][outer_key].items()}
#测试：修改协作类型的ocdfg，并存储在dfg字典中oc
# dict2={'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
#                     'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
# 将每个协作类型的dfg修改正常，遍历每个协作类型的活动集，设置元组存储相邻元素，然后其次数设置为1。
# for outer_key, inner_dict in dict2.items():
#     for inner_key, activities_list in inner_dict.items():
#         activity_pairs = {}
#         # activity_pairs = OrderedDict()
#         if len(activities_list) == 1:
#             # 如果活动列表只包含一个活动，添加虚拟开始和虚拟结束节点
#             st_activities = "VirtualStart"
#             en_activities = "VirtualEnd"
#             activity_pairs[(st_activities, activities_list[0])] = 1
#             activity_pairs[(activities_list[0], en_activities)] = 1
#         elif len(activities_list) > 1:
#             for i in range(len(activities_list) - 1):
#                 st_activities = activities_list[i]
#                 en_activities = activities_list[i + 1]
#                 activity_pair = (st_activities, en_activities)
#                 if activity_pair in activity_pairs:
#                     activity_pairs[activity_pair] += 1
#                 else:
#                     activity_pairs[activity_pair] = 1
#         print(inner_key + "的dfg结果为：")
#         dfg = {x: 1 for x, y in activity_pairs.items()}  # 将频次设置为1
#         pprint.pprint(dfg)
#ocpn字典内容：
{"activities":{"CI"},
 "activities_indep":{"events":{"CI":{"e30"}},
                     "total_objects":{"CI":{("e30","I1")}},
                     "unique_objects":{"CI":{"P1","I1","I2"}},
                    },
 "activities_ot":{"events":{"ocel:type:Invoice":{"CI":{"e30"}}},
                  "total_objects":{},
                  "unique_objects":{}
                },
'double_arcs_on_activity':{"ocel:type:Invoice":{"CI":True},
                           "ocel:type:Item":{"PS":True}
                          },
'edges': {'event_couples': {
          'ocel:type:Invoice': {('Create Invoice', 'Clear Invoice'): {('e18','e30')}},
                           },
          'total_objects': {
          'ocel:type:Invoice': {('Create Invoice', 'Clear Invoice'): {('e18','e30','I1')}},
                           },
          'unique_objects': {
          'ocel:type:Invoice': {('Create Invoice', 'Clear Invoice'): {'I1'}},
                            }
         },
 "end_activities":{},
 "object_type":{},
 "petri_nets":{},
 "start_activities":{}
 }











#通用： 协作类型的活动\开始活动\结束活动修改正常
# for outer_key, inner_dict in dict2.items():
for outer_key, inner_dict in shared_result_dict.items():
    modified_result_dict = {}
    for inner_key,activities_list in inner_dict.items():
        activities = {x: len(y) for x, y in dict1["activities_ot"]["events"][inner_key].items()}
        print(inner_key+"的activities为：")
        pprint.pprint(activities)
        start_activities = {x: len(y) for x, y in dict3["start_activities"]["events"][inner_key].items()}
        end_activities = {x: len(y) for x, y in dict3["end_activities"]["events"][inner_key].items()}
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
        pprint.pprint(dfg)
        print(inner_key + "的Petri网结果为：")
        petri_nets[inner_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
        pprint.pprint(petri_nets[inner_key])
        modified_result_dict[outer_key] = petri_nets
    petri_result_dict = modified_result_dict
print("最终的Petri网结果为：")
pprint.pprint(petri_result_dict)
pm4py.view_ocpn(petri_result_dict, format='svg')

co_result_dict={}
co_result_dict["activities_ot"]=dict1["activities_ot"]
co_result_dict["activities"] = dict1[""]

        # petri_nets[inner_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
        # modified_result_dict[outer_key] = petri_nets
        # petri_result_dict = modified_result_dict
        # pprint.pprint(petri_result_dict)



# activities = {x: len(y) for x, y in dict1["activities_ot"]["events"][inner_key].items()}
# 协作类型的开始和结束活动修改正常
# start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][outer_key].items()}
# end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][outer_key].items()}
#dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][outer_key].items()}
#petri_nets[outer_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)



#内层字典a


#再构造内层Petri网
# activity_pairs = {}  # 用于存储活动对的字典
# for outer_key, inner_dict in shared_result_dict.items():
#     for inner_key, activities_list in inner_dict.items():
#         petri_nets = {}
#         # 初始化开始和结束活动
#         start_activities = end_activities = activities_list[0]
#         # 如果只有一个活动，start和end都设置为它
#         if len(activities_list) == 1:
#             start_activities = end_activities = activities_list[0]
#         # 如果有多个活动，设置start为第一个，end为最后一个，并构造活动对
#         elif len(activities_list) > 1:
#             start_activities = activities_list[0]
#             end_activities = activities_list[-1]
#             # 构造活动对
#             activity_pair = (start_activities, end_activities)
#             activity_pairs[activity_pair] = 1  # 设置活动对出现的次数
#         petri_nets[inner_key] = inductive_miner.apply_dfg(activity_pairs, start_activities, end_activities, activities)
#
# # 输出活动对字典
# print(activity_pairs)
# {'ocel:type:Item': {'ocel:type:Order': ['Pack Shipment'],
#                     'ocel:type:Supplier Order': ['Receive SO', 'Unpack']}}
# for outer_key, inner_dict in shared_result_dict.items():
#     for inner_key, activities_list in inner_dict.items():
#         if isinstance(activities_list, list):
#             # 如果只有一个活动
#             if len(activities_list) == 1:
#                 activity = activities_list[0]
#                 start_activities = end_activities = activity
#                 activity_pair = (start_activities, end_activities)
#                 print(inner_key)
#                 print({activity_pair: 1})
#             # 如果有多个活动
#             elif len(activities_list) > 1:
#                 activity_pairs = []
#                 for i in range(len(activities_list) - 1):
#                     start_activities = activities_list[i]
#                     end_activities = activities_list[i + 1]
#                     activity_pair = (start_activities, end_activities)
#                     activity_pairs.append(activity_pair)
#                 print(inner_key)
#                 for pair in activity_pairs:
#                     print({pair: 1})
#             print(inner_key)
#             print(activity_pairs)

#inner_activities:{'Receive SO': 2, 'Unpack': 5, 'Pack Shipment': 2}

#修改相应类型的活动为字典
# for outer_key, inner_dict in shared_result_dict.items():
#     for inner_key, activities_list in inner_dict.items():
#         activity_pairs = {}  # 创建一个新的 activity_pairs 字典
#         inner_activities = {}
#         for activity in activities_list:
#             activities_dict = {activity: 1 for activity in activities_list}
       # print(activities_dict)
       # {'Pack Shipment': 1}
       # {'Unpack': 1, 'Receive SO': 1}

        # if isinstance(activities_list, list):
        #     # 如果只有一个活动
        #     if len(activities_list) == 1:
        #         activity = activities_list[0]
        #         start_activities = end_activities = activity
        #         activity_pair = (start_activities, end_activities)
        #         activity_pairs[activity_pair] = 1
        #         print(inner_key)
        #         print(activity_pairs)
        #         petri_nets[inner_key] = inductive_miner.apply_dfg(activity_pairs, start_activities, end_activities, activities_dict)
        #         print("petri_nets如下：")
        #         print(petri_nets)
        #         break
        #     # 如果有多个活动
        #     elif len(activities_list) > 1:
        #         for i in range(len(activities_list) - 1):
        #             start_activities = activities_list[i]
        #             end_activities = activities_list[i + 1]
        #             activity_pair = (start_activities, end_activities)
        #             if activity_pair in activity_pairs:
        #                 activity_pairs[activity_pair] += 1
        #             else:
        #                 activity_pairs[activity_pair] = 1
        #         print(inner_key)
        #         print(activity_pairs)
        # if isinstance(activities_list, list):
        #     # 如果只有一个活动
        #     if len(activities_list) == 1:
        #         activity = activities_list[0]
        #         start_activities = {activity: 1}
        #         end_activities = {activity: 1}
        #         activity_pair = (start_activities, end_activities)
        #         activity_pairs[activity_pair] = 1
        #         print(inner_key)
        #         print(activity_pairs)
        #         petri_nets[inner_key] = inductive_miner.apply_dfg(activity_pairs, start_activities, end_activities,
        #                                                           activities_dict)
        #         print("petri_nets如下：")
        #         print(petri_nets)
        #         break
        #     # 如果有多个活动
        #     elif len(activities_list) > 1:
        #         activity_pairs = []
        #         for i in range(len(activities_list) - 1):
        #             start_activities = {activities_list[i]: 1}
        #             end_activities = {activities_list[i + 1]: 1}
        #             activity_pair = (start_activities, end_activities)
        #             if activity_pair in activity_pairs:
        #                 activity_pairs[activity_pair] += 1
        #             else:
        #                 activity_pairs[activity_pair] = 1
        #         print(inner_key)
        #         print(activity_pairs)

# 输出活动对及其频次
# for pair, count in activity_pairs.items():
#     print(pair, count)











        # petri_nets[inner_key] = inductive_miner.apply_dfg(activity_pairs, start_activities, end_activities, activities)




# dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][outer_key].items()}
        # petri_nets[outer_key] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
        # modified_result_dict[outer_key] = petri_nets




    #inter_key




#个例
# supplier_order_values = None
# for item in dic_list:
#     if 'ocel:type:Supplier Order' in item:
#         supplier_order_values = set(item['ocel:type:Supplier Order'])
#         break
# if supplier_order_values:
#     # 存储共享相同值的键
#     shared_keys = {}
#     # 遍历列表中的其他字典
#     for item in dic_list:
#         for key, values in item.items():
#             if key != 'ocel:type:Supplier Order':
#                 common_values = set(values).intersection(supplier_order_values)
#                 if common_values:
#                     shared_keys[key] = common_values
#     # 输出结果
#     if shared_keys:
#         print("与 'ocel:type:Supplier Order' 共享相同值的键：")
#         for key, values in shared_keys.items():
#             print(f"'{key}' 与 'ocel:type:Supplier Order' 具有共同值：{', '.join(values)}")
#     else:
#         print("没有与 'ocel:type:Supplier Order' 共享相同值的键。")
# else:
#     print("'ocel:type:Supplier Order' 不存在或没有相关的值。")

#新思路，直接修改日志，实现结果：给出指定对象类型和关联类型以及相应活动的字典(correspondence_dict)，随后进行事件过滤，最后利用过滤后的日志挖掘模型
#现在需要给出correspondence_dict字典


# def apply(ocel: OCEL, correspondence_dict: Dict[str, Collection[str]],
#           parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
#     if parameters is None:
#         parameters = {}
#
#     activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, ocel.event_activity)
#     object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
#     temp_column = exec_utils.get_param_value(Parameters.TEMP_COLUMN, parameters, "@@temp_column")
#     temp_separator = exec_utils.get_param_value(Parameters.TEMP_SEPARATOR, parameters, "@#@#")
#
#     ocel = copy(ocel)
#
#     # 构建一个集合，包含了要保留的对象类型以及它们相关的活动
#     selected_types_and_activities = set()
#     for ot in correspondence_dict:
#         selected_types_and_activities.add(ot)
#         selected_types_and_activities.update(correspondence_dict[ot])
#
#     # 使用筛选条件，只保留与选定对象类型和活动相关的关系
#     ocel.relations = ocel.relations[
#         (ocel.relations[object_type_column].isin(selected_types_and_activities)) &
#         (ocel.relations[activity_key].isin(selected_types_and_activities))
#     ]
#
#     return filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)
















