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
from typing import Optional, Dict, Any
from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
import tempfile
from uuid import uuid4
from pm4py.util import vis_utils
from statistics import mean, median


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    ACT_METRIC = "act_metric"
    EDGE_METRIC = "edge_metric"
    ACT_THRESHOLD = "act_threshold"
    EDGE_THRESHOLD = "edge_threshold"
    ANNOTATION = "annotation"
    PERFORMANCE_AGGREGATION_MEASURE = "aggregationMeasure"

#----------此步骤用于将所有对象类型ot转换为对应的颜色------------------

#将字符串(参数ot)作为输入，返回一个表示颜色的字符串
def ot_to_color(ot: str) -> str:
    ot = int(hash(ot)) #将字符串ot使用哈希函数进行转换，将结果转换为整数
    num = [] #初始化一个空列表num,用于存储颜色的数值
    while len(num) < 6: #循环执行以下步骤，知道num列表的长度达到6
        num.insert(0, ot % 16) #在列表num的开头插入ot对16取余的结果
        ot = ot // 16 #将ot值除以16取整
    # 将num中每个数值转换为16进制字符串，并使用vis_utils.get_corr_hex()函数获取颜色的16进制表示
    ret = "#" + "".join([vis_utils.get_corr_hex(x) for x in num])
    return ret #表示颜色的字符串


#---------此步骤用于根据给定参数向有向图中添加一个活动结点，并设置结点的属性（标签、形状、填充颜色等）-----------------------
def add_activity(G: Digraph, act, freq, act_prefix, nodes, annotation, min_freq, max_freq):
    """
    Adds an activity node to the graph
    """
    act_uuid = str(uuid4()) #生成一个唯一的活动结点标识符act_uuid,使用uuid4()生成一个uuid字符串，并转换为字符串类型
    nodes[act] = act_uuid #[act:act_uuid]将活动名称act与活动结点标识符act_uuid的映射关系添加到nodes字典中，以便后续的引用和检索
    fillcolor = vis_utils.get_trans_freq_color(freq, min_freq, max_freq) #根据给定的频率值，使用函数获取填充颜色
    # 若注释类型为频率，则将活动名称act与频率值freq拼接为一个字符串，并作为结点的标签，结点形状为方形，样式为filled，填充色为fillcolor
    #G.node(act_uuid, label=act + "\n" + act_prefix + str(freq), shape="box", style="filled", fillcolor=fillcolor, fontsize="12")
    if annotation == "frequency":#修改变迁内注释，只包含活动+频率G.node(act_uuid, label=act + "\n" + act_prefix + str(freq), shape="box", style="filled", fillcolor=fillcolor,fontsize="28")
        G.node(act_uuid, label=act + "\n" + str(freq), shape="box", style="filled", fontsize="28")
    #若注释类型不为频率，则将活动名称act作为结点标签，并使用默认结点形状为方形
    else:
        G.node(act_uuid, label=act, shape="box")


#---------此步骤用于根据给定参数向有向图中添加一个带有频率注释的边，并设置边的属性(标签、线条宽度、颜色等)--------------------
def add_frequency_edge(G: Digraph, ot, act1, act2, freq, edge_prefix, nodes, min_freq, max_freq):
    """
    Adds a edge (frequency annotation)
    """
    otc = ot_to_color(ot) #给定对象类型ot，通过调用函数获取对应的颜色值otc
    # 从nodes字典中检索出活动act1和act2对应的活动结点标识符act_uuid1和act_uuid2
    act_uuid1 = nodes[act1]
    act_uuid2 = nodes[act2]
    # 根据给定的频率值，调用函数获取边的线条宽度
    # penwidth = vis_utils.get_arc_penwidth(freq, min_freq, max_freq)
    # G.edge(act_uuid1, act_uuid2, label=ot + " " + edge_prefix + str(freq), fontsize="8", penwidth=str(penwidth),
    #        color=otc, fontcolor=otc)
    # 使用函数向有向图中添加边，起点为act_uuid1,终点为act_uuid2，边标签的字体大小为8，边的线条宽度penwidth和颜色color和字体颜色fontcolor都根据ot类型的颜色otc设置
    ot = ot.split("ocel:type:")[1]
    #修改有向边上的注释为只含数字label=ot + " " + edge_prefix + str(freq)
    G.edge(act_uuid1, act_uuid2, label=str(freq), fontsize="24", penwidth="3.0",
           color=otc, fontcolor=otc)

#---------此步骤用于根据给定参数向有向图中添加一个带有性能注释的边，并设置边的属性(标签、颜色等)-------------------------
def add_performance_edge(G: Digraph, ot, act1, act2, perf, edge_prefix, nodes, aggregation_measure):
    """
    Adds an edge (performance annotation)
    """
    otc = ot_to_color(ot) #给定对象类型ot，通过调用函数获取对应的颜色值otc
    #根据给定的聚合度量aggregation_measure，对性能值进行聚合操作
    if aggregation_measure == "median": #若为median，使用median()计算性能值的中位数
        perf = median(perf)
    elif aggregation_measure == "min": #若为min，使用min()计算性能值的最小值
        perf = min(perf)
    elif aggregation_measure == "max": #若为max，使用max()计算性能值的最大值
        perf = max(perf)
    elif aggregation_measure == "sum": #若为sum，使用sum()计算性能值的总和
        perf = sum(perf)
    else: #若不为上述，使用mean()计算性能值的均值
        perf = mean(perf)
    #从nodes字典中检索出两个活动对应的结点标识符
    act_uuid1 = nodes[act1]
    act_uuid2 = nodes[act2]
    #向有向图中添加边，起点是act_uuid1，终点是act_uuid2，边的标签是ot和性能值pref拼接而成的字符串，使用函数将性能值转换为可读形式
    #边标签字体大小为8，边和字体颜色为otc
    G.edge(act_uuid1, act_uuid2, label=ot + " " + edge_prefix + vis_utils.human_readable_stat(perf), fontsize="8", penwidth="3.0",
           color=otc, fontcolor=otc)

#---------此步骤用于根据给定参数，向有向图中添加一个开始结点，以及从开始节点指向活动结点的边，并设置结点和边的属性(标签、形状、颜色等)-------
def add_start_node(G: Digraph, ot, act, freq, edge_prefix, nodes, annotation, min_freq, max_freq):
    """
    Adds a start node to the graph
    """
    otc = ot_to_color(ot) #给定对象类型ot，通过调用函数获取对应的颜色值otc
    act_uuid = nodes[act] #从nodes字典中检索处活动act对应的活动结点标识符act_uuid
    start_ot = "start_node@#@#" + ot #创建开始结点的对象类型标识符start_ot，这个标识符用于唯一标识开始结点，并于对象类型相关联
    #若start_ot在nodes中不存在，重新添加
    if start_ot not in nodes:
        endpoint_uuid = str(uuid4())
        nodes[start_ot] = endpoint_uuid
        #起始结点的标签为对象类型ot，形状为椭圆形，样式为填充，填充颜色为otc
        label = ot.split("ocel:type:")[1]
        G.node(endpoint_uuid, label=label, shape="circle", style="filled", fillcolor=otc, fixedsize="true", fontsize="18", width="1.5", height="1.5", fontcolor="black", penwidth="2.0")
    start_ot_uuid = nodes[start_ot] #获取开始结点标识符
    edge_label = "" #根据注释类型不同，设置边的标签
    if annotation == "frequency": #若为freq，边的标签设置为ot+freq的拼接字符串
        #修改有向边注释，只包括频率edge_label = ot.split("ocel:type:")[1] + " " + edge_prefix + str(freq)
        edge_label = str(freq)
    #根据给定频率，获取边的线条宽度
    #penwidth = vis_utils.get_arc_penwidth(freq, min_freq, max_freq)
    #G.edge(start_ot_uuid, act_uuid, label=edge_label, fontsize="8", penwidth=str(penwidth), fontcolor=otc, color=otc, fontcolor="white")
    #向有向图中添加边
    G.edge(start_ot_uuid, act_uuid, label=edge_label, fontsize="24", penwidth="3.0", fontcolor=otc, color=otc)




#---------此步骤用于根据给定参数，向有向图中添加一个结束结点，以及从活动节点指向结束结点的边，并设置结点和边的属性(标签、形状、颜色等)-------
def add_end_node(G: Digraph, ot, act, freq, edge_prefix, nodes, annotation, min_freq, max_freq):
    """
    Adds an end node to the graph
    """
    otc = ot_to_color(ot)
    act_uuid = nodes[act]
    end_ot = "end_node@#@#" + ot
    if end_ot not in nodes:
        endpoint_uuid = str(uuid4())
        nodes[end_ot] = endpoint_uuid
        #G.node(endpoint_uuid, label=ot, shape="circle", style="filled", fillcolor=otc, fixedsize="true", width="1.5", height="1.5")
        #label = ot.split("部分")[1]  # 替换 "部分" 为需要去除的部分的具体内容
        #G.node(endpoint_uuid, label=label, shape="circle", style="filled", fillcolor=otc, fixedsize="true", width="1.5", height="1.5")
        label = ot.split("ocel:type:")[1]
        G.node(endpoint_uuid, label=label, shape="circle", style="filled", fillcolor=otc, fixedsize="true", fontsize="18", width="1.5", height="1.5", fontcolor="black", penwidth="2.0") #结束结点用下划线边框 #更新为圆形 #固定形状大小
    end_ot_uuid = nodes[end_ot]
    edge_label = ""
    if annotation == "frequency":
        #修改有向边注释，只包括频率edge_label = ot.split("ocel:type:")[1] + " " + edge_prefix + str(freq)
        edge_label = str(freq)
    # penwidth = vis_utils.get_arc_penwidth(freq, min_freq, max_freq)
    # G.edge(act_uuid, end_ot_uuid, label=edge_label, fontsize="8", penwidth=str(penwidth), fontcolor=otc, color=otc)
    G.edge(act_uuid, end_ot_uuid, label=edge_label, fontsize="24", penwidth="3.0", fontcolor=otc, color=otc)

def apply(ocdfg: Dict[str, Any], parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes an OC-DFG as a Graphviz di-graph

    Parameters
    ---------------
    ocdfg
        OC-DFG
    parameters
        Parameters of the algorithm:
        - Parameters.FORMAT => the format of the output visualization (default: "png")
        - Parameters.BGCOLOR => the default background color (default: "bgcolor")
        - Parameters.ACT_METRIC => the metric to use for the activities. Available values:
            - "events" => number of events (default) #事件数量：活动在事件日志中出现的次数【默认】
            - "unique_objects" => number of unique objects #唯一对象数量：活动涉及的不同对象的数量
            - "total_objects" => number of total objects #总对象数量：活动涉及的对象总数量
        - Parameters.EDGE_METRIC => the metric to use for the edges. Available values:
            - "event_couples" => number of event couples (default) #事件对数量：两个活动间直接跟随关系的数量
            - "unique_objects" => number of unique objects #边中涉及的不同对象数量
            - "total_objects" => number of total objects #边中涉及的对象总数量
        - Parameters.ACT_THRESHOLD => the threshold to apply on the activities frequency (default: 0). Only activities
        having a frequency >= than this are kept in the graph. #活动阈值默认为0
        - Parameters.EDGE_THRESHOLD => the threshold to apply on the edges frequency (default 0). Only edges
        having a frequency >= than this are kept in the graph. #边阈值默认为0
        - Parameters.ANNOTATION => the annotation to use for the visualization. Values: #结点和边的标签上的注释：频率还是性能
            - "frequency": frequency annotation
            - "performance": performance annotation
        - Parameters.PERFORMANCE_AGGREGATION_MEASURE => the aggregation measure to use for the performance: #性能度量指标
            - mean
            - median
            - min
            - max
            - sum

    Returns
    ---------------
    viz
        Graphviz DiGraph
    """
    if parameters is None:
        parameters = {}

#从参数中提取特定的配置值，若没有指定相应的值，则使用默认值。用于后续可视化
    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")
    act_metric = exec_utils.get_param_value(Parameters.ACT_METRIC, parameters, "events")
    edge_metric = exec_utils.get_param_value(Parameters.EDGE_METRIC, parameters, "event_couples")
    act_threshold = exec_utils.get_param_value(Parameters.ACT_THRESHOLD, parameters, 0)
    edge_threshold = exec_utils.get_param_value(Parameters.EDGE_THRESHOLD, parameters, 0)
    annotation = exec_utils.get_param_value(Parameters.ANNOTATION, parameters, "frequency")
    performance_aggregation_measure = exec_utils.get_param_value(Parameters.PERFORMANCE_AGGREGATION_MEASURE, parameters,
                                                                 "mean")

    act_count = {} #空字典，用于存储活动的计数信息
    act_ot_count = {} #空字典，用于存储活动的对象类型的计数信息
    sa_count = {}
    ea_count = {}
    act_prefix = "" #为活动结点的标签添加前缀
    edges_count = {}
    edges_performance = {}
    edge_prefix = "" #为边的标签添加前缀
#------此步用来配置活动的度量指标共3种：事件数量、唯一对象数量、总对象数量----------
    if act_metric == "events": #如果选择事件数量作为活动的度量指标
        act_count = ocdfg["activities_indep"]["events"]
        act_ot_count = ocdfg["activities_ot"]["events"]
        sa_count = ocdfg["start_activities"]["events"]
        ea_count = ocdfg["end_activities"]["events"]
        act_prefix = "E="
    elif act_metric == "unique_objects": #
        act_count = ocdfg["activities_indep"]["unique_objects"]
        act_ot_count = ocdfg["activities_ot"]["unique_objects"]
        sa_count = ocdfg["start_activities"]["unique_objects"]
        ea_count = ocdfg["end_activities"]["unique_objects"]
        act_prefix = "UO="
    elif act_metric == "total_objects":
        act_count = ocdfg["activities_indep"]["total_objects"]
        act_ot_count = ocdfg["activities_ot"]["total_objects"]
        sa_count = ocdfg["start_activities"]["total_objects"]
        ea_count = ocdfg["end_activities"]["total_objects"]
        act_prefix = "TO="

    if edge_metric == "event_couples":
        edges_count = ocdfg["edges"]["event_couples"]
        edges_performance = ocdfg["edges_performance"]["event_couples"]
        edge_prefix = "EC="
    elif edge_metric == "unique_objects":
        edges_count = ocdfg["edges"]["unique_objects"]
        edge_prefix = "UO="
    elif edge_metric == "total_objects":
        edges_count = ocdfg["edges"]["total_objects"]
        edges_performance = ocdfg["edges_performance"]["total_objects"]
        edge_prefix = "TO="

    if annotation == "performance" and edge_metric == "unique_objects":
        raise Exception("unsupported performance visualization for unique objects!")

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("ocdfg", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    min_edges_count = {}
    max_edges_count = {}

    for ot in edges_count:
        all_edges_count = [len(y) for y in edges_count[ot].values()]
        min_edges_count[ot] = min(all_edges_count)
        max_edges_count[ot] = max(all_edges_count)
        all_sa_count = [len(y) for y in sa_count[ot].values()]
        min_edges_count[ot] = min(min(all_sa_count), min_edges_count[ot])
        max_edges_count[ot] = max(max(all_sa_count), max_edges_count[ot])
        all_ea_count = [len(y) for y in ea_count[ot].values()]
        min_edges_count[ot] = min(min(all_ea_count), min_edges_count[ot])
        max_edges_count[ot] = max(max(all_ea_count), max_edges_count[ot])

    act_count_values = [len(y) for y in act_count.values()]
    min_act_count = min(act_count_values)
    max_act_count = max(act_count_values)

    nodes = {}
    for act in act_count:
        if len(act_count[act]) >= act_threshold:
            add_activity(viz, act, len(act_count[act]), act_prefix, nodes, annotation, min_act_count, max_act_count)

    for ot in edges_count:
        for act_cou in edges_count[ot]:
            if act_cou[0] in nodes and act_cou[1] in nodes:
                if len(edges_count[ot][act_cou]) >= edge_threshold:
                    if annotation == "frequency":
                        add_frequency_edge(viz, ot, act_cou[0], act_cou[1], len(edges_count[ot][act_cou]), edge_prefix,
                                           nodes, min_edges_count[ot], max_edges_count[ot])
                    elif annotation == "performance":
                        add_performance_edge(viz, ot, act_cou[0], act_cou[1], edges_performance[ot][act_cou],
                                             edge_prefix, nodes, performance_aggregation_measure)

    for ot in sa_count:
        if ot in edges_count:
            for act in sa_count[ot]:
                if act in nodes:
                    if len(sa_count[ot][act]) >= edge_threshold:
                        # add_start_node(G: Digraph, ot, act, freq, edge_prefix, nodes, annotation)
                        add_start_node(viz, ot, act, len(sa_count[ot][act]), edge_prefix, nodes, annotation,
                                       min_edges_count[ot], max_edges_count[ot])

    for ot in ea_count:
        if ot in edges_count:
            for act in ea_count[ot]:
                if act in nodes:
                    if len(ea_count[ot][act]) >= edge_threshold:
                        add_end_node(viz, ot, act, len(ea_count[ot][act]), edge_prefix, nodes, annotation,
                                     min_edges_count[ot], max_edges_count[ot])

    viz.attr(rankdir='LR')
    viz.format = image_format

    return viz
