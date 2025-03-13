import uuid
import tempfile
from graphviz import Digraph
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

#绿色、紫色、红色、青绿、红色、绿色、蓝、深绿、蓝、绿、紫、绿、橙、黄、绿、紫、绿、橙、蓝、蓝绿、青绿、蓝、橙、绿、红、红、蓝
#新增5种颜色"#993300", "#006600", "#6D70C5", "#696969", "#398C93",
COLORS = ["#993300", "#006600", "#6D70C5", "#696969", "#398C93", "#05B202", "#A13CCD", "#BA0D39", "#39F6C0", "#E90638",
          "#07B423", "#306A8A", "#678225", "#2742FE", "#4C9A75","#4C36E9", "#7DB022", "#EDAC54", "#EAC439", "#EAC439",
          "#1A9C45", "#8A51C4", "#496A63", "#FB9543", "#2B49DD","#13ADA5", "#2DD8C1", "#2E53D7", "#EF9B77", "#06924F",
          "#AC2C4D", "#82193F", "#0140D3"]


def apply(obj, parameters=None):
    if parameters is None:#若参数为空，将其赋值为空字典，避免引发错误
        parameters = {}
#---------------------此步用来进行设置图片保存类型和名称、有向图对象g、图形的长宽高函数、所有对象和变迁名称都设置为空字典、库所变迁和弧初始数目--------
    image_format = "png"
    if "format" in parameters:
        image_format = parameters["format"]
    # 创建一个具有特定后缀gv的临时文件，该文件的名称存储在filename中
    filename = tempfile.NamedTemporaryFile(suffix='.gv').name
    # 创建一个有向图对象g=Digraph("有向图名称",有向图存储位置，渲染图的dot引擎，设置图像属性：背景色为透明色)
    # 可使用该对象g进行进一步的操作，如添加结点、边等
    g = Digraph("", filename=filename, engine='dot',
                graph_attr={'bgcolor': 'transparent'})
    # 检查参数字典中是否存在ratio键，若存在，则将该键的对应值赋给变量ratio，然后将该值作为有向图对象的ratio属性的值进行设置，用于控制生成的图形的宽高比
    if "ratio" in parameters:
        ratio = parameters["ratio"]
        g.attr(ratio=ratio)
    # 创建两个空的字典对象
    all_objs = {} #存放所有的pl:pl.name和tr:tr.name键值对
    trans_names = {}
    # 库所、变迁和弧的数目都初始化为1
    pl_count = 1
    tr_count = 1
    arc_count = 1

#-------------------此步用来给所有对象类型创建颜色映射，用字典color_mapping[ot]来表示-------------------------------------

    #根据索引值index，从颜色列表中选定颜色赋值给变量color，
    #若索引值超过颜色列表的长度则对总长度取余，使用索引值为0 - (len(COLORS) - 1)
    # color = COLORS[index % len(COLORS)]
    #color = "#05B202" #绿色
    color = "#993300" #新增绿色
    color_mapping = dict() #创建一个空字典，存储颜色映射关系
    object_types = obj.object_types #确定对象类型
    for index, ot in enumerate(object_types): #使用一个循环，为给定对象类型列表中的（对象类型索引和对象类型）创建颜色映射，并将结果存储在color_mapping字典中
        color_mapping[ot] = COLORS[index % len(COLORS)]

#------------------此步用来设置库所的唯一标识符、名称、形状、样式、填充颜色、边框颜色、标签字体大小---------------------------------------

    for pl in obj.places:#遍历所有库所pl并设置唯一标识符
        # this_uuid = str(uuid.uuid4())
        this_uuid = "p%d" % (pl_count) #this_uuid=p pl_count   (%d表示整数占位符，uuid通用唯一标识符)
        # pl_str = this_uuid
        pl_count += 1 #库所+1
        color = color_mapping[pl.object_type] #库所对应的对象类型的颜色
        # 使用graphviz库中的图形对象g创建一个结点，设置其名称=pl.name、结点标签=pl.name、形状=圆形、样式=被填充、填充颜色=库所对应的对象类型颜色、边框颜色=同上，和标签的字体大小=13
        if pl.initial == True: #如果库所为开始库所
            #新增：圆形框的宽和高都为0.5英寸
            #第二个pl.name如果换成this_uuid，就是p1，而不是现在plane1
            g.node(pl.name, pl.name, shape="circle", style="filled", fillcolor=color, color=color, width="0.5", height="0.5",
                   fontsize="13.0", labelfontsize="13.0")
        # 使用graphviz库中的图形对象g创建一个结点，设置其名称=pl.name、形状=圆形、样式=被填充、填充颜色=库所对应的对象类型颜色、边框颜色=同上，和标签的字体大小=13
        elif pl.final == True:#如果库所为结束库所
            #新增：圆形框的宽和高都为0.5英寸
            g.node(pl.name, pl.name, shape="circle", style="filled", fillcolor=color, color=color, width="0.5", height="0.5",
                   fontsize="13.0", labelfontsize="13.0")
        else:#若是普通库所就不用填充
            # 新增：圆形框的宽和高都为0.5英寸
            g.node(pl.name, pl.name, shape="circle", style="filled", fillcolor=color, color=color, width="0.5", height="0.5",
                   fontsize="13.0", labelfontsize="13.0")
        #将pl.name:pl键值对，存储在all_objs字典中
        all_objs[pl] = pl.name


#-----------------此步用来设置不可见变迁和可见变迁的结点名称、标签、字体颜色、结点形状、填充颜色、结点样式、结点标签的字体大小-------------

    for tr in obj.transitions:
        # this_uuid = str(uuid.uuid4())
        this_uuid = "t%d" % (tr_count)
        tr_count += 1
        if tr.silent == True:#如果变迁为不可见变迁，
            # g.node(this_uuid, this_uuid, fontcolor="#FFFFFF", shape="box",
            #       fillcolor="#000000", style="filled", xlabel="Test", labelfontsize="18.0")

            #有向图g的结点(结点名=变迁名，结点标签=唯一标识符，结点标签的字体颜色=白色，结点形状=方形，填充颜色=黑色，结点样式=填充，结点标签的附加标签=Test，结点标签字体大小=18)
            g.node(tr.name, tr.name, fontcolor="#FFFFFF", shape="box",
                   fillcolor="#000000", style="filled", xlabel="Test", labelfontsize="18.0", penwidth="1.0", width="0.5", height="0.5")
            #将tr:tr.name键值对，存储到字典all_objs中
            all_objs[tr] = tr.name  # this_uuid
        elif tr.name not in trans_names:#判断变迁名称是否在trans_names字典中，避免重复添加或处理
            # g.node(this_uuid, "%s \n (%s)" % (tr.name, this_uuid), shape="box", fontsize="36.0",
            #       labelfontsize="36.0")

            #有向图g中的结点(结点名称=tr.name,结点标签=tr.name,结点形状=方形,结点标签的字体大小=36,标签的字体大小为36)
            #新增:字体大小为18(原36.0)
            g.node(tr.name, tr.name, shape="box", fontsize="18.0",
                   labelfontsize="18.0", penwidth="1.0", width="0.5", height="0.5")
            #将tr.name:tr.name作为键值对，存储到字典trans_names中
            trans_names[tr.name] = tr.name  # this_uuid
            #将tr.name:tr作为键值对，存储到字典all_objs中
            all_objs[tr] = tr.name  # this_uuid
        else:#如果变迁已存在，直接存储到字典中
            all_objs[tr] = trans_names[tr.name]

#-----------------此步用来设置弧的格式-----------------------------------------------------------------------

    for arc in obj.arcs:#遍历所有弧
        # this_uuid = str(uuid.uuid4())
        this_uuid = "a%d" % (arc_count) #设置唯一标识符
        arc_count += 1

        source_node = arc.source #弧的来源是source结点，库所/变迁
        target_node = arc.target #弧的去处是target结点，库所/变迁

        if type(source_node) == ObjectCentricPetriNet.Place:#若source结点类别是库所，则着其对象类型对应的颜色
            color = color_mapping[source_node.object_type]
        if type(target_node) == ObjectCentricPetriNet.Place:#若target结点类别是库所，则着其对象类型对应的颜色
            color = color_mapping[target_node.object_type]

        if arc.variable == True:#若为可变弧
            #若source结点和target结点都在all_objs字典中，就创建一条从all_objs[source_node]到all_objs[target_node]的有向边
            if source_node in all_objs and target_node in all_objs:
                #有向图g中的可变弧(字典中的sorce结点，字典中的target结点，弧的名称为空字符串即无标签，弧的颜色为带白色边界的color，弧标签字体大小=13)
                #新增：弧线变粗两个单位
                #
                g.edge(all_objs[source_node], all_objs[target_node],arrowhead="dotted",style="dashed", 
                       label="+", labeldistance="100.0", fontcolor=color, fontweight="bold", color=color + ":white:" + color, penwidth="2.0", fontsize="18.0")
                g.edge_attr.update(style="radial")
                

           #若不是都在，就输出二者都不在字典中
            else:
                print("Either {} or {} not existing in nodes".format(
                    source_node, target_node))

        else:#若为普通弧，弧颜色为color
            if source_node in all_objs and target_node in all_objs:
                #新增：弧线变粗两个单位
                g.edge(all_objs[source_node], all_objs[target_node],
                       label="", color=color, penwidth="2.0", fontsize="13.0")
            else:
                print("Either {} or {} not existing in nodes".format(
                    source_node, target_node))
        #将this_uuid：arc键值对，存储在字典中
        all_objs[arc] = this_uuid

    #overlap是图形中节点是否允许重叠的属性，通过将其设置为false，表示禁止节点之间的重叠
    g.attr(overlap='false')
    #新增：fontsize是图形中文本的字体大小属性，大小设置为18(原11)
    g.attr(fontsize='18')
    #指定图像输出格式
    g.format = image_format
    return g