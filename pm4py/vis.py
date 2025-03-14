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
import os
from copy import copy
from typing import Optional
from typing import Union, List, Dict, Any, Tuple

import pandas as pd

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties


def view_petri_net(petri_net: PetriNet, initial_marking: Optional[Marking] = None,
                   final_marking: Optional[Marking] = None, format: str = "png"):
    """
    Views a (composite) Petri net

    Parameters
    -------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final marking
        Final marking
    format
        Format of the output picture (default: png)
    """
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.view(gviz)


def save_vis_petri_net(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str):
    """
    Saves a Petri net visualization to a file

    Parameters
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final marking
        Final marking
    file_path
        Destination path
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.save(gviz, file_path)


def view_performance_dfg(dfg: dict, start_activities: dict, end_activities: dict, format: str = "png",
                         aggregation_measure="mean"):
    """
    Views a performance DFG

    Parameters
    ----------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    format
        Format of the output picture (default: png)
    aggregation_measure
        Aggregation measure (default: mean): mean, median, min, max, sum, stdev
    """
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    from pm4py.visualization.dfg.variants import performance as dfg_perf_visualizer
    dfg_parameters = dfg_perf_visualizer.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregation_measure
    gviz = dfg_perf_visualizer.apply(dfg, parameters=parameters)
    dfg_visualizer.view(gviz)


def save_vis_performance_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str,
                         aggregation_measure="mean"):
    """
    Saves the visualization of a performance DFG

    Parameters
    ----------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    file_path
        Destination path
    aggregation_measure
        Aggregation measure (default: mean): mean, median, min, max, sum, stdev
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    from pm4py.visualization.dfg.variants import performance as dfg_perf_visualizer
    dfg_parameters = dfg_perf_visualizer.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregation_measure
    gviz = dfg_perf_visualizer.apply(dfg, parameters=parameters)
    dfg_visualizer.save(gviz, file_path)


def view_dfg(dfg: dict, start_activities: dict, end_activities: dict, format: str = "png",
             log: Optional[EventLog] = None):
    """
    Views a (composite) DFG

    Parameters
    -------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    format
        Format of the output picture (default: png)
    """
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    dfg_parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    parameters = get_properties(log)
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters=parameters)
    dfg_visualizer.view(gviz)


def save_vis_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str,
                 log: Optional[EventLog] = None):
    """
    Saves a DFG visualization to a file

    Parameters
    --------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    file_path
        Destination path
    """
    if log is not None:
        if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    dfg_parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    parameters = get_properties(log)
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters=parameters)
    dfg_visualizer.save(gviz, file_path)


def view_process_tree(tree: ProcessTree, format: str = "png"):
    """
    Views a process tree

    Parameters
    ---------------
    tree
        Process tree
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.view(gviz)


def save_vis_process_tree(tree: ProcessTree, file_path: str):
    """
    Saves the visualization of a process tree

    Parameters
    ---------------
    tree
        Process tree
    file_path
        Destination path
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.save(gviz, file_path)


def save_vis_bpmn(bpmn_graph: BPMN, file_path: str):
    """
    Saves the visualization of a BPMN graph

    Parameters
    --------------
    bpmn_graph
        BPMN graph
    file_path
        Destination path
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
    gviz = bpmn_visualizer.apply(bpmn_graph, parameters={parameters.FORMAT: format})
    bpmn_visualizer.save(gviz, file_path)


def view_bpmn(bpmn_graph: BPMN, format: str = "png"):
    """
    Views a BPMN graph

    Parameters
    ---------------
    bpmn_graph
        BPMN graph
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
    gviz = bpmn_visualizer.apply(bpmn_graph, parameters={parameters.FORMAT: format})
    bpmn_visualizer.view(gviz)


def view_heuristics_net(heu_net: HeuristicsNet, format: str = "png"):
    """
    Views an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics net
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.view(gviz)


def save_vis_heuristics_net(heu_net: HeuristicsNet, file_path: str):
    """
    Saves the visualization of an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics nte
    file_path
        Destination path
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.save(gviz, file_path)


def __dotted_attribute_selection(log, attributes):
    """
    Default attribute selection for the dotted chart

    Parameters
    -----------------
    log
        Event log

    Returns
    -----------------
    attributes
        List of attributes
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if attributes is None:
        from pm4py.util import xes_constants
        from pm4py.objects.log.util import sorting
        from pm4py.convert import convert_to_event_log
        log = convert_to_event_log(log)
        log = sorting.sort_timestamp(log, xes_constants.DEFAULT_TIMESTAMP_KEY)
        for index, trace in enumerate(log):
            trace.attributes["@@index"] = index
        attributes = ["time:timestamp", "case:@@index", "concept:name"]
    return log, attributes


def view_dotted_chart(log, format: str = "png", attributes=None):
    """
    Displays the dotted chart

    Parameters
    -----------------
    log
        Event log
    format
        Image format
    attributes
        Attributes that should be used to construct the dotted chart.
        If None, the default dotted chart will be shown:
            x-axis: time
            y-axis: cases (in order of occurrence in the event log)
            color: activity
        For custom attributes, use a list of attributes
        of the form [x-axis attribute, y-axis attribute, color attribute], e.g., ["concept:name", "org:resource", "concept:name"])

    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    log, attributes = __dotted_attribute_selection(log, attributes)
    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters={"format": format})
    dotted_chart_visualizer.view(gviz)


def save_vis_dotted_chart(log, file_path: str, attributes=None):
    """
    Saves the visualization of the dotted chart

    Parameters
    -----------------
    log
        Event log
    file_path
        Destination path
    attributes
        Attributes that should be used to construct the dotted chart (for example, ["concept:name", "org:resource"])
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    format = os.path.splitext(file_path)[1][1:]
    log, attributes = __dotted_attribute_selection(log, attributes)
    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters={"format": format})
    dotted_chart_visualizer.save(gviz, file_path)


def view_sna(sna_metric):
    """
    Represents a SNA metric (.html)

    Parameters
    ---------------
    sna_metric
        Values of the metric
    """
    from pm4py.visualization.sna import visualizer as sna_visualizer
    gviz = sna_visualizer.apply(sna_metric, variant=sna_visualizer.Variants.PYVIS)
    sna_visualizer.view(gviz)


def save_vis_sna(sna_metric, file_path: str):
    """
    Saves the visualization of a SNA metric in a .html file

    Parameters
    ----------------
    sna_metric
        Values of the metric
    file_path
        Destination path
    """
    from pm4py.visualization.sna import visualizer as sna_visualizer
    gviz = sna_visualizer.apply(sna_metric, variant=sna_visualizer.Variants.PYVIS)
    sna_visualizer.save(gviz, file_path)


def view_case_duration_graph(log: Union[EventLog, pd.DataFrame], format: str = "png"):
    """
    Visualizes the case duration graph

    Parameters
    -----------------
    log
        Log object
    format
        Format of the visualization (png, svg, ...)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log))
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log))
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                        parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_case_duration_graph(log: Union[EventLog, pd.DataFrame], file_path: str):
    """
    Saves the case duration graph in the specified path

    Parameters
    ----------------
    log
        Log object
    file_path
        Destination path
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log))
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log))
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                        parameters={"format": format})
    graphs_visualizer.save(graph_vis, file_path)


def view_events_per_time_graph(log: Union[EventLog, pd.DataFrame], format: str = "png"):
    """
    Visualizes the events per time graph

    Parameters
    -----------------
    log
        Log object
    format
        Format of the visualization (png, svg, ...)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log))
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log))
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                        parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_events_per_time_graph(log: Union[EventLog, pd.DataFrame], file_path: str):
    """
    Saves the events per time graph in the specified path

    Parameters
    ----------------
    log
        Log object
    file_path
        Destination path
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log))
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log))
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                        parameters={"format": format})
    graphs_visualizer.save(graph_vis, file_path)


def view_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], format: str = "png"):
    """
    Displays the performance spectrum

    Parameters
    ----------------
    perf_spectrum
        Performance spectrum
    format
        Format of the visualization (png, svg ...)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities, parameters=get_properties(log))
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.view(gviz)


def save_vis_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], file_path: str):
    """
    Saves the visualization of the performance spectrum to a file

    Parameters
    ---------------
    log
        Event log
    activities
        List of activities (in order) that is used to build the performance spectrum
    file_path
        Destination path (including the extension)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities, parameters=get_properties(log))
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    format = os.path.splitext(file_path)[1][1:]
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.save(gviz, file_path)


def __builds_events_distribution_graph(log: Union[EventLog, pd.DataFrame], distr_type: str = "days_week"):
    """
    Internal method to build the events distribution graph
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    if distr_type == "days_month":
        title = "Distribution of the Events over the Days of a Month";
        x_axis = "Day of month";
        y_axis = "Number of Events"
    elif distr_type == "months":
        title = "Distribution of the Events over the Months";
        x_axis = "Month";
        y_axis = "Number of Events"
    elif distr_type == "years":
        title = "Distribution of the Events over the Years";
        x_axis = "Year";
        y_axis = "Number of Events"
    elif distr_type == "hours":
        title = "Distribution of the Events over the Hours";
        x_axis = "Hour (of day)";
        y_axis = "Number of Events"
    elif distr_type == "days_week":
        title = "Distribution of the Events over the Days of a Week";
        x_axis = "Day of the Week";
        y_axis = "Number of Events"
    elif distr_type == "weeks":
        title = "Distribution of the Events over the Weeks of a Year";
        x_axis = "Week of the Year";
        y_axis = "Number of Events"
    else:
        raise Exception("unsupported distribution specified.")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        x, y = attributes_get.get_events_distribution(log, distr_type=distr_type, parameters=get_properties(log))
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        x, y = attributes_get.get_events_distribution(log, distr_type=distr_type, parameters=get_properties(log))

    return title, x_axis, y_axis, x, y


def view_events_distribution_graph(log: Union[EventLog, pd.DataFrame], distr_type: str = "days_week", format="png"):
    """
    Shows the distribution of the events in the specified dimension

    Parameters
    ----------------
    log
        Event log
    distr_type
        Type of distribution (default: days_week):
        - days_month => Gets the distribution of the events among the days of a month (from 1 to 31)
        - months => Gets the distribution of the events among the months (from 1 to 12)
        - years => Gets the distribution of the events among the years of the event log
        - hours => Gets the distribution of the events among the hours of a day (from 0 to 23)
        - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday)
        - weeks => Gets the distribution of the events among the weeks of a year (from 0 to 52)
    format
        Format of the visualization (default: png)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    title, x_axis, y_axis, x, y = __builds_events_distribution_graph(log, distr_type)
    parameters = copy(get_properties(log))
    parameters["title"] = title;
    parameters["x_axis"] = x_axis;
    parameters["y_axis"] = y_axis;
    parameters["format"] = format
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    gviz = graphs_visualizer.apply(x, y, variant=graphs_visualizer.Variants.BARPLOT, parameters=parameters)
    graphs_visualizer.view(gviz)


def save_vis_events_distribution_graph(log: Union[EventLog, pd.DataFrame], file_path: str,
                                       distr_type: str = "days_week"):
    """
    Saves the distribution of the events in a picture file

    Parameters
    ----------------
    log
        Event log
    file_path
        Destination path (including the extension)
    distr_type
        Type of distribution (default: days_week):
        - days_month => Gets the distribution of the events among the days of a month (from 1 to 31)
        - months => Gets the distribution of the events among the months (from 1 to 12)
        - years => Gets the distribution of the events among the years of the event log
        - hours => Gets the distribution of the events among the hours of a day (from 0 to 23)
        - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday)
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")

    format = os.path.splitext(file_path)[1][1:]
    title, x_axis, y_axis, x, y = __builds_events_distribution_graph(log, distr_type)
    parameters = copy(get_properties(log))
    parameters["title"] = title;
    parameters["x_axis"] = x_axis;
    parameters["y_axis"] = y_axis;
    parameters["format"] = format
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    gviz = graphs_visualizer.apply(x, y, variant=graphs_visualizer.Variants.BARPLOT, parameters=parameters)
    graphs_visualizer.save(gviz, file_path)


#-------------------------此步骤用来可视化对象为中心的直接跟随图-----------------------------

#view_ocdfg(ocdfg:字典[键是字符串，值是任意类型]，annotation:字符串，表示注释，默认为频率，act_metric:字符串，表示活动度量，默认为事件，
#edge_metric:字符串，表示边度量，默认为事件间的共现频率，act_threshold:整数，表示活动阈值，默认为0，edge_threshold:整数，表示边阈值，默认为0)
#performance_aggregation:字符串，表示性能聚合，默认为mean，format:表示格式，默认为png
def view_ocdfg(ocdfg: Dict[str, Any], annotation: str = "frequency", act_metric: str = "events", edge_metric="event_couples", act_threshold: int = 0, edge_threshold: int = 0, performance_aggregation: str = "mean", format: str = "png"):
    """
    #使用提供的配置参数可视化 OC-DFG
    Views an OC-DFG (object-centric directly-follows graph) with the provided configuration.

    Parameters
    ----------
    ocdfg
        Object-centric directly-follows graph
    annotation #注释类型有两种：频率注释，事件出现的频率或数量；性能注释，事件的性能指标或度量
        The annotation to use for the visualization. Values:
            - "frequency": frequency annotation
            - "performance": performance annotation
    act_metric #活动的度量指标有三种：事件数量(默认)，事件发生的次数；唯一对象数量，涉及的唯一对象的数量；总对象数量，涉及的所有对象数量，包括重复出现的对象
        The metric to use for the activities. Available values:
            - "events" => number of events (default)
            - "unique_objects" => number of unique objects
            - "total_objects" => number of total objects
    edge_metric #边的度量指标有三种：事件对数量(默认)，基于事件间的直接后续关系(事件对)数量；唯一对象数量，基于涉及的唯一对象的数量；
                #总对象数量，基于涉及的所有对象的数量，包括重复出现的对象
        The metric to use for the edges. Available values:
            - "event_couples" => number of event couples (default)
            - "unique_objects" => number of unique objects
            - "total_objects" => number of total objects
    act_threshold #对活动频率应用阈值，用于筛选在图中保留的活动；默认情况下，阈值为0，表示所有活动都留；
                  #若阈值>0，则只有频率大于或等于阈值的活动才会被保留在图中，过滤低频活动
        The threshold to apply on the activities frequency (default: 0). Only activities
        having a frequency >= than this are kept in the graph.
    edge_threshold #对边频率应用阈值，默认为0，其他同上
        The threshold to apply on the edges frequency (default 0). Only edges
        having a frequency >= than this are kept in the graph.
    performance_aggregation #性能度量的聚合方式有5种：mean性能度量值的平均值，median性能度量值排序后取中位数，min性能度量值中的最小值，max性能度量值中的最大值，sum性能度量值累加
        The aggregation measure to use for the performance: mean, median, min, max, sum
    format
        The format of the output visualization (default: "png")
    """
    from pm4py.visualization.ocel.ocdfg import visualizer #从可视化dfg中导入visualizer函数
    from pm4py.visualization.ocel.ocdfg.variants import classic #从可变dfg的变体中导入classic变体，此处定义了默认的参数和配置选项
    parameters = {} #创建空字典用于存储可视化参数，然后将提供的配置参数设置到参数字典中
    parameters[classic.Parameters.FORMAT] = format #设置可视化格式
    parameters[classic.Parameters.ANNOTATION] = annotation #设置注释类型
    parameters[classic.Parameters.ACT_METRIC] = act_metric #设置活动度量
    parameters[classic.Parameters.EDGE_METRIC] = edge_metric #设置边度量
    parameters[classic.Parameters.ACT_THRESHOLD] = act_threshold #设置活动阈值
    parameters[classic.Parameters.EDGE_THRESHOLD] = edge_threshold #设置边阈值
    parameters[classic.Parameters.PERFORMANCE_AGGREGATION_MEASURE] = performance_aggregation #设置性能聚合方式
    gviz = classic.apply(ocdfg, parameters=parameters)
    visualizer.view(gviz)




def save_vis_ocdfg(ocdfg: Dict[str, Any], file_path: str, annotation: str = "frequency", act_metric: str = "events", edge_metric="event_couples", act_threshold: int = 0, edge_threshold: int = 0, performance_aggregation: str = "mean"):
    """
    Saves the visualization of an OC-DFG (object-centric directly-follows graph) with the provided configuration.

    Parameters
    ----------
    ocdfg
        Object-centric directly-follows graph
    file_path
        Destination path (including the extension)
    annotation
        The annotation to use for the visualization. Values:
            - "frequency": frequency annotation
            - "performance": performance annotation
    act_metric
        The metric to use for the activities. Available values:
            - "events" => number of events (default)
            - "unique_objects" => number of unique objects
            - "total_objects" => number of total objects
    edge_metric
        The metric to use for the edges. Available values:
            - "event_couples" => number of event couples (default)
            - "unique_objects" => number of unique objects
            - "total_objects" => number of total objects
    act_threshold
        The threshold to apply on the activities frequency (default: 0). Only activities
        having a frequency >= than this are kept in the graph.
    edge_threshold
        The threshold to apply on the edges frequency (default 0). Only edges
        having a frequency >= than this are kept in the graph.
    performance_aggregation
        The aggregation measure to use for the performance: mean, median, min, max, sum
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.ocel.ocdfg import visualizer
    from pm4py.visualization.ocel.ocdfg.variants import classic
    parameters = {}
    parameters[classic.Parameters.FORMAT] = format
    parameters[classic.Parameters.ANNOTATION] = annotation
    parameters[classic.Parameters.ACT_METRIC] = act_metric
    parameters[classic.Parameters.EDGE_METRIC] = edge_metric
    parameters[classic.Parameters.ACT_THRESHOLD] = act_threshold
    parameters[classic.Parameters.EDGE_THRESHOLD] = edge_threshold
    parameters[classic.Parameters.PERFORMANCE_AGGREGATION_MEASURE] = performance_aggregation
    parameters[classic.Parameters.ANNOTATION] = "performance"
    gviz = classic.apply(ocdfg, parameters=parameters)
    visualizer.save(gviz, file_path)


def view_ocpn(ocpn: Dict[str, Any], format: str = "png"):
    """
    Visualizes on the screen the object-centric Petri net

    Parameters
    --------------
    ocpn
        Object-centric Petri net
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
    gviz = ocpn_visualizer.apply(ocpn, parameters={"format": format})
    ocpn_visualizer.view(gviz)


def save_vis_ocpn(ocpn: Dict[str, Any], file_path: str):
    """
    Saves the visualization of the object-centric Petri net into a file

    Parameters
    ----------------
    ocpn
        Object-centric Petri net
    file_path
        Target path of the visualization
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
    gviz = ocpn_visualizer.apply(ocpn, parameters={"format": format})
    ocpn_visualizer.save(gviz, file_path)


def view_network_analysis(network_analysis: Dict[Tuple[str, str], Dict[str, Any]], variant: str = "frequency", format: str = "png", activity_threshold: int = 1, edge_threshold: int = 1):
    """
    Visualizes the network analysis

    Parameters
    -----------------
    network_analysis
        Network analysis
    variant
        Variant of the visualization:
            - frequency (if the discovered network analysis contains the frequency of the interactions)
            - performance (if the discovered network analysis contains the performance of the interactions)
    format
        Format of the visualization (default: png)
    activity_threshold
        The minimum number of occurrences for an activity to be included (default: 1)
    edge_threshold
        The minimum number of occurrences for an edge to be included (default: 1)
    """
    from pm4py.visualization.network_analysis import visualizer as network_analysis_visualizer
    variant = network_analysis_visualizer.Variants.PERFORMANCE if variant == "performance" else network_analysis_visualizer.Variants.FREQUENCY
    gviz = network_analysis_visualizer.apply(network_analysis, variant=variant, parameters={"format": format, "activity_threshold": activity_threshold, "edge_threshold": edge_threshold})
    network_analysis_visualizer.view(gviz)


def save_vis_network_analysis(network_analysis: Dict[Tuple[str, str], Dict[str, Any]], file_path: str, variant: str = "frequency", activity_threshold: int = 1, edge_threshold: int = 1):
    """
    Saves the visualization of the network analysis

    Parameters
    -----------------
    network_analysis
        Network analysis
    file_path
        Target path of the visualization
    variant
        Variant of the visualization:
            - frequency (if the discovered network analysis contains the frequency of the interactions)
            - performance (if the discovered network analysis contains the performance of the interactions)
    activity_threshold
        The minimum number of occurrences for an activity to be included (default: 1)
    edge_threshold
        The minimum number of occurrences for an edge to be included (default: 1)
    """
    format = os.path.splitext(file_path)[1][1:]
    from pm4py.visualization.network_analysis import visualizer as network_analysis_visualizer
    variant = network_analysis_visualizer.Variants.PERFORMANCE if variant == "performance" else network_analysis_visualizer.Variants.FREQUENCY
    gviz = network_analysis_visualizer.apply(network_analysis, variant=variant, parameters={"format": format, "activity_threshold": activity_threshold, "edge_threshold": edge_threshold})
    network_analysis_visualizer.save(gviz, file_path)
