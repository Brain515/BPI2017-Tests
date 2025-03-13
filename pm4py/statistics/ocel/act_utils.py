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
from typing import Optional, Dict, Any, Tuple, Set
from enum import Enum
from pm4py.util import exec_utils
#constants 中存储了所有用到的参数名，如PARAM_EVENT_ID = "param:event:id"
from pm4py.objects.ocel import constants as ocel_constants
import pandas as pd
from pm4py.objects.ocel.obj import OCEL
from copy import copy


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_ID = ocel_constants.PARAM_OBJECT_ID
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    PREFILTERING = "prefiltering"

#associations字典示例：
"""
associations = {
    "Activity1": {("EventA", "Object1"), ("EventB", "Object2")},
    "Activity2": {("EventC", "Object3"), ("EventD", "Object4")},
    "Activity3": {("EventA", "Object1"), ("EventE", "Object5")}
}
"""

#aggregate_events函数，目的是生成一个新字典[键为活动:{值为与活动关联的事件集合}]，结果示例：
"""
Activity: Activity1 - Associated Events: EventA, EventB
Activity: Activity2 - Associated Events: EventC, EventD
Activity: Activity3 - Associated Events: EventA, EventE
"""
def aggregate_events(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[str]]:
    """
    Utility method to calculate the "events" metric from the associations.
    """
    ret = {}
    for act in associations:
        ret[act] = set()
        for el in associations[act]:
            ret[act].add(el[0])
    return ret

#aggregate_unique_objects函数，目的是生成一个新字典{键为活动：{值为与活动关联的对象集合}}，结果示例：
"""
Activity: Activity1 - Unique Objects: Object1, Object2
Activity: Activity2 - Unique Objects: Object3, Object4
Activity: Activity3 - Unique Objects: Object1, Object5
"""
def aggregate_unique_objects(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[str]]:
    """
    Utility method to calculate the "unique objects" metric from the associations.
    """
    ret = {}
    for act in associations:
        ret[act] = set()
        for el in associations[act]:
            ret[act].add(el[1])
    return ret

#aggregate_total_objects函数，目的是生成一个新字典{键为活动：值为{元组(事件，对象)}}
def aggregate_total_objects(associations: Dict[str, Set[Tuple[str, str]]]) -> Dict[str, Set[Tuple[str, str]]]:
    """
    Utility method to calculate the "total objects" metric from the associations.
    """
    return associations

#find_associations_from_relations_df函数，目的是从关系数据框中关联活动与事件标识符及对象标识符的组合，输出一个字典{键为活动，值为元组集合{(事件id，对象id)}}。
def find_associations_from_relations_df(relations_df: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None) -> \
Dict[str, Set[Tuple[str, str]]]:
    """
    Associates each activity in the relationship dataframe with the combinations
    of event identifiers and objects that are associated to the activity.

    Parameters
    ------------------
    rel_df
        Relations dataframe
    parameters
        Parameters of the method, including:
        - Parameters.EVENT_ID => the attribute to use as event identifier
        - Parameters.OBJECT_ID => the attribute to use as object identifier
        - Parameters.EVENT_ACTIVITY => the attribute to use as activity

    Returns
    -----------------
    dict_associations
        Dictionary that associates each activity to its (ev. id, obj id.) combinations.
    """
    if parameters is None:
        parameters = {}
    #从参数字典中获取event_id，对象id和活动名，设置为默认值
    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel_constants.DEFAULT_EVENT_ID)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel_constants.DEFAULT_OBJECT_ID)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                ocel_constants.DEFAULT_EVENT_ACTIVITY)
    prefiltering = exec_utils.get_param_value(Parameters.PREFILTERING, parameters, "none")

    if prefiltering == "start":
        relations_df = relations_df.groupby(object_id).first().reset_index()
    elif prefiltering == "end":
        relations_df = relations_df.groupby(object_id).last().reset_index()

    #提取关联关系：从relations_df中提取特定列的值，保存在相应列表中
    ids = list(relations_df[event_id])
    oids = list(relations_df[object_id])
    acts = list(relations_df[event_activity])
    #构建关联字典
    associations = {}
    #遍历这些列表，构建关联字典。对于每个活动，将其与相关的（事件标识符，对象标识符）组合相关联，存储在字典中。键为活动，值为元组集合{(eid，oid)}。
    i = 0
    while i < len(acts):
        if acts[i] not in associations:
            associations[acts[i]] = set()
        associations[acts[i]].add((ids[i], oids[i]))
        i = i + 1

    return associations


def find_associations_from_ocel(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Set[Any]]:
    """
    Associates each activity in the OCEL with the combinations
    of event identifiers and objects that are associated to the activity.

    Parameters
    ------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the method, including:
        - Parameters.EVENT_ID => the attribute to use as event identifier
        - Parameters.OBJECT_ID => the attribute to use as object identifier
        - Parameters.EVENT_ACTIVITY => the attribute to use as activity

    Returns
    -----------------
    dict_associations
        Dictionary that associates each activity to its (ev. id, obj id.) combinations.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(Parameters.EVENT_ID, parameters, ocel.event_id_column)
    object_id = exec_utils.get_param_value(Parameters.OBJECT_ID, parameters, ocel.object_id_column)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters,
                                                ocel.event_activity)

    new_parameters = copy(parameters)
    new_parameters[Parameters.EVENT_ID] = event_id
    new_parameters[Parameters.OBJECT_ID] = object_id
    new_parameters[Parameters.EVENT_ACTIVITY] = event_activity

    return find_associations_from_relations_df(ocel.relations, parameters=new_parameters)
