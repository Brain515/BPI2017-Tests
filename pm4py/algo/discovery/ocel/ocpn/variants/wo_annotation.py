'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
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


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net (without annotation) from the given object-centric event log,
    using the Inductive Miner as process discovery algorithm.

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY => the activity attribute to be used
        - Parameters.OBJECT_TYPE => the object type attribute to be used
        - Parameters.DOUBLE_ARC_THRESHOLD => the threshold for the attribution of the "double arc", as
        described in the paper.

    Returns
    -----------------
    ocpn
        Object-centric Petri net model, as a dictionary of properties.
    """
    if parameters is None:
        parameters = {}
    # 使用exec_utils模块中的get_param_value函数，从参数字典中获取Parameters.DOUBLE_ARC_THRESHOLD对应的值，如果不存在，默认为0.0
    # 此阈值在后续的步骤中用于判断是否添加“双弧”
    double_arc_threshold = exec_utils.get_param_value(Parameters.DOUBLE_ARC_THRESHOLD, parameters, 0.0)
    ocdfg = ocdfg_discovery.apply(ocel, parameters=parameters)

    petri_nets = {}
    double_arcs_on_activity = {}
    # 进入循环，遍历OCDFG的所有对象类型
    for ot in ocdfg["object_types"]:
        # 获取特定对象类型ot的所有活动事件
        # 对ocdfg字典进行第一个索引操作，从中获取键为activities_ot的值，此值为另一个嵌套的字典
        # 在activities_ot字典内部，继续进行索引，获取键为total_objects的值，此值可能是另一个嵌套的字典
        # 最后使用ot作为键来从上一步嵌套字典中提取一个特定的值
        activities_eo = ocdfg["activities_ot"]["total_objects"][ot]
        # 分别获取活动、开始活动、结束活动以及直接跟随关系的数量，都可从ocdfg字典中提取
        activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][ot].items()}
        start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][ot].items()}
        end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][ot].items()}
        dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][ot].items()}
        #一个活动是否多次出现
        is_activity_double = {}
        #在内部循环中，遍历每个活动act，计算该活动的事件对象数量，并根据双弧阈值判断是否为双弧活动
        for act in activities_eo:
            ev_obj_count = Counter()
            for evc in activities_eo[act]:
                ev_obj_count[evc[0]] += 1
            this_single_amount = len(list(x for x in ev_obj_count if ev_obj_count[x] == 1)) / len(ev_obj_count)
            if this_single_amount <= double_arc_threshold:
                is_activity_double[act] = True
            else:
                is_activity_double[act] = False

        double_arcs_on_activity[ot] = is_activity_double
        # 调用IM的apply_dfg方法，使用dfg\开始活动\结束活动和活动事件的数量来发现一个Petri网模型，结果将存储在petri_nets字典中
        petri_nets[ot] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)
    # 更新两个字典中的信息，将生成的Petri网和双弧活动信息存储在ocdfg字典中
    ocdfg["petri_nets"] = petri_nets
    ocdfg["double_arcs_on_activity"] = double_arcs_on_activity
    # 返回完整的ocdfg字典，其中包括OCPN和双弧信息和其他属性
    return ocdfg

