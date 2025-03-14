from enum import Enum
from pm4py.util import exec_utils, constants
from pm4py.objects.ocel.util import filtering_utils
from copy import copy
from typing import Dict, Any, Optional, Collection
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel import constants as ocel_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    TEMP_COLUMN = "temp_column"
    TEMP_SEPARATOR = "temp_separator"


def apply(ocel: OCEL, correspondence_dict: Dict[str, Collection[str]],
          parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    过滤对象为中心的事件日志，只保留具有指定活动集的指定对象类型(过滤掉其他对象)
    Filters an object-centric event log keeping only the specified object types
    with the specified activity set (filters out the rest).

    Parameters
    ----------------
    ocel
        Object-centric event log
    *****这个字典用于指定感兴趣的每个对象类型以及与这些对象类型关联的允许活动的集合
    correspondence_dict
        Dictionary containing, for every object type of interest, a
        collection of allowed activities.  Example:

        {"order": ["Create Order"], "element": ["Create Order", "Create Delivery"]}

        Keeps only the object types "order" and "element".
        For the "order" object type, only the activity "Create Order" is kept.
        For the "element" object type, only the activities "Create Order" and "Create Delivery" are kept.
    *****给出的示例表示：有两个感兴趣的对象类型order和element，其中order保留一个活动，element保留两个活动
    parameters
        Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY => the activity key
            - Parameters.OBJECT_TYPE => the object type column

    Returns
    -----------------
    filtered_ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, ocel.event_activity)
    object_type_column = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
    temp_column = exec_utils.get_param_value(Parameters.TEMP_COLUMN, parameters, "@@temp_column")
    temp_separator = exec_utils.get_param_value(Parameters.TEMP_SEPARATOR, parameters, "@#@#")

    ocel = copy(ocel)

    inv_dict = set()
    for ot in correspondence_dict:
        for act in correspondence_dict[ot]:
            inv_dict.add(act + temp_separator + ot)

    ocel.relations[temp_column] = ocel.relations[activity_key] + temp_separator + ocel.relations[object_type_column]
    ocel.relations = ocel.relations[ocel.relations[temp_column].isin(inv_dict)]

    del ocel.relations[temp_column]

    return filtering_utils.propagate_relations_filtering(ocel, parameters=parameters)
