import uuid
from typing import Optional, Dict, Any
from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
import tempfile
from pm4py.util import vis_utils
from pm4py.objects.petri_net.obj import PetriNet

#通过参数获取可视化的格式("format") 背景颜色("bgcolor") 和排列方向("rankdir")等可选参数
class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"

import hashlib
#ot_to_color函数目的是将对象类型转换为表示颜色的16进制字符串
def ot_to_color(ot: str) -> str:
    ot = int(hash(ot))
    num = []
    while len(num) < 6:
        num.insert(0, ot % 16)
        ot = ot // 16
    ret = "#" + "".join([vis_utils.get_corr_hex(x) for x in num])
    return ret
    # hash_value = hash(ot)
    # # 根据哈希值的奇偶性选择颜色
    # if hash_value % 2 == 0:
    #     return "#FF0000"  # 红色
    # else:
    #     return "#00FF00"  # 绿色

#apply函数目的是给定ocpn和可选参数字典，输出一个Graphviz的”Diagraph“对象
def apply(ocpn: Dict[str, Any], parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Obtains a visualization of the provided object-centric Petri net (without decoration).

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    ----------------
    ocpn
        Object-centric Petri net
    variant
        Variant of the algorithm to be used
    parameters
        Variant-specific parameters:
        - Parameters.FORMAT => the format of the visualization ("png", "svg", ...)
        - Parameters.BGCOLOR => the background color
        - Parameters.RANKDIR => the rank direction (LR = left-right, TB = top-bottom)

    Returns
    ---------------
    gviz
        Graphviz digraph
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, "transparent")
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, "LR")

    #创建一个Digraph对象用于可视化，设置图像的一些属性
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("ocdfg", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    #创建对象类型、活动、库所和变迁的结点，并设置他们的样式和标签
    activities_map = {}
    source_places = {}
    target_places = {}
    transition_map = {}
    places = {}

    #为Petri网的每个活动创建一个结点，以便清晰的显示网络中的各个活动，每个活动有一个唯一的标识符和相应的活动名称。
    for act in ocpn["activities"]:
        activities_map[act] = str(uuid.uuid4())
        viz.node(activities_map[act], label=act, shape="box")
    #为每个对象类型创建两个结点，一个表示开始库所，一个表示结束库所，并根据对象类型的名称设置颜色和形状
    for ot in ocpn["object_types"]:
        otc = ot_to_color(ot) #为每个类型设置颜色
        source_places[ot] = str(uuid.uuid4()) #为每个类型创建两个唯一的标识符作为开始和结束库所
        target_places[ot] = str(uuid.uuid4())
        # 创建一个结点表示开始库所，标签为类型ot，形状为椭圆形，样式为filled填充颜色，fillcolor=otc指定结点的填充颜色
        viz.node(source_places[ot], label=ot, shape="ellipse", style="filled", fillcolor=otc)
        # 创建一个结点表示结束库所，标签为类型ot，形状为underline下划线，fontcolor=otc指定标签的字体颜色
        viz.node(target_places[ot], label=ot, shape="underline", fontcolor=otc)
    #可视化Petri网元素，包括库所、变迁和弧
    #遍历ocpn字典中的不同Petri网类型
    for ot in ocpn["petri_nets"]:
        #为类型设置颜色
        otc = ot_to_color(ot)
        #获取该类型的petri网、输入映射和输出映射
        net, im, fm = ocpn["petri_nets"][ot]
        #遍历该类型网中的所有库所
        for place in net.places:
            #检查库所是否位于输入映射中，若是则与起始节点关联
            if place in im:
                places[place] = source_places[ot]
            #检查库所是否位于输出映射中，若是则与结束结点关联
            elif place in fm:
                places[place] = target_places[ot]
            #若为中间库所，创建一个带有填充颜色的圆形结点，结点名称使用唯一标识符。
            else:
                places[place] = str(uuid.uuid4())
                viz.node(places[place], label=" ", shape="circle", style="filled", fillcolor=otc)
        #遍历该类型网中的所有变迁
        for trans in net.transitions:
            #若有标签，表示这是一个活动变迁，将其与相应的活动结点关联
            if trans.label is not None:
                transition_map[trans] = activities_map[trans.label]
            #若无标签，表示这是一个无标签变迁，创建一个带有填充颜色的矩形结点
            else:
                transition_map[trans] = str(uuid.uuid4())
                viz.node(transition_map[trans], label=" ", shape="box", style="filled", fillcolor=otc)
        #遍历该类型网中的所有弧
        # for arc in net.arcs:
        #     #检查弧的源是否是库所，若是，表示这是一个从库所到变迁的弧
        #     if type(arc.source) is PetriNet.Place:
        #         #检查弧的目标变迁是否在ocpn["double_arcs_on_activity"][ot]中，若为双弧活动，设置penwidth表示弧的粗细
        #         is_double = arc.target.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.target.label]
        #         penwidth = "4.0" if is_double else "1.0"
        #         #用edge方法创建一个边，将库所(弧源)与变迁(弧的目标)相连，设置边的颜色、线宽等属性，以及双弧的标志。
        #         viz.edge(places[arc.source], transition_map[arc.target], color=otc, penwidth=penwidth)
        #     #若弧源是变迁，表示这是从变迁到库所的弧，同样检查是否需要绘制双弧，并创建边连接变迁和库所
        #     elif type(arc.source) is PetriNet.Transition:
        #         is_double = arc.source.label in ocpn["double_arcs_on_activity"][ot] and ocpn["double_arcs_on_activity"][ot][arc.source.label]
        #         penwidth = "4.0" if is_double else "1.0"
        #         viz.edge(transition_map[arc.source], places[arc.target], color=otc, penwidth=penwidth)

        for arc in net.arcs:
            # 检查弧的源是否是库所，若是，表示这是一个从库所到变迁的弧
            if type(arc.source) is PetriNet.Place:
                # 如果目标变迁的活动标签为 "VirtualStart"
                if arc.target.label == "VirtualStart":
                    # 删除目标变迁及其相关的弧
                    del transition_map[arc.target]
                    # 删除以这些弧为目标的库所
                    for source_place in net.source(arc.target):
                        if source_place in places:
                            del places[source_place]
                    # 更新以这些弧为目标的弧的源为原始弧的源
                    for new_arc in net.arcs:
                        if new_arc.target == arc.target:
                            new_arc.target = arc.source
                    continue  # 跳过当前弧
                # 检查弧的目标变迁是否在 ocpn["double_arcs_on_activity"][ot] 中，若为双弧活动，设置 penwidth 表示弧的粗细
                is_double = arc.target.label in ocpn["double_arcs_on_activity"][ot] and \
                            ocpn["double_arcs_on_activity"][ot][arc.target.label]
                penwidth = "4.0" if is_double else "1.0"
                # 用 edge 方法创建一个边，将库所（弧源）与变迁（弧的目标）相连，设置边的颜色、线宽等属性，以及双弧的标志。
                viz.edge(places[arc.source], transition_map[arc.target], color=otc, penwidth=penwidth)
            # 若弧源是变迁，表示这是从变迁到库所的弧，同样检查是否需要绘制双弧，并创建边连接变迁和库所
            elif type(arc.source) is PetriNet.Transition:
                is_double = arc.source.label in ocpn["double_arcs_on_activity"][ot] and \
                            ocpn["double_arcs_on_activity"][ot][arc.source.label]
                penwidth = "4.0" if is_double else "1.0"
                viz.edge(transition_map[arc.source], places[arc.target], color=otc, penwidth=penwidth)

    #设置可视化中图的排列方向，选择从左到右、或从上到下等不同的排列方式。
    viz.attr(rankdir=rankdir)
    #设置可视化的格式，根据image_format的值设置不同的图像格式如png等
    viz.format = image_format
    #返回构建好的可视化图viz
    return viz

