import re


import lux
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList

def process_vis_str(vis_str, table_name):
    Select = []
    From = []
    Where = []
    Groupby = []
    AGG_OPS = ('none', 'max', 'min', 'count', 'sum', 'mean')

    # e.g. vis_str='<Vis  (x: BIN(Expenditure), y: COUNT(Record)) mark: histogram, score: 2.5241522522787068 >'
    intent = re.findall(r'[(](.*)[)]', vis_str)  # 提取intent  e.g. ['x: BIN(Expenditure), y: COUNT(Record)']

    x_y_color = intent[0].split(',')  # e.g.  ['x: BIN(Expenditure)', ' y: COUNT(Record)']
    x_y_color = [{'channel': each.split(':')[0].strip(), 'attribute': each.split(':')[1].strip()} for each in
                 x_y_color]  # e.g. [{'channel': 'x', 'attribute': 'BIN(Expenditure)'},{'channel': 'y', 'attribute': 'COUNT(Record)'}]
    #print("x_y_color", x_y_color)
    for each in x_y_color:
        if each['channel'] == 'x':
            x_attribute = each['attribute']
        if each['channel'] == 'y':
            y_attribute = each['attribute']
    for each in x_y_color:
        #print('each', each)
        if each['channel'] == 'color':
            Groupby.append(each['attribute'])
            Select.append(each['attribute'])
        elif each['channel'] == 'x' or each['channel'] == 'y':
            temp = each['attribute'].split('--')
            #print('temp', temp)
            x = temp[0].strip()
            # 判断有没有agg以及去掉BIN(x),Record
            x_temp = x.split('(')
            if len(x_temp) == 1:
                Select.append(x.strip())
            elif len(x_temp) == 2:
                if x_temp[0] == 'BIN':
                    Select.append(x_temp[1][:-1])
                else:
                    if x_temp[0].lower() in AGG_OPS and x_temp[1][:-1] != 'Record':
                        Select.append(x.strip())
                        if each['channel'] == 'x':
                            Groupby.append(y_attribute)
                        if each['channel'] == 'y':
                            Groupby.append(x_attribute)

            if len(temp) > 1:
                Where.append(temp[1].strip()[1:-1])
                #Select.append(temp[1].strip()[1:-1].split('=')[0])
    From.append(table_name)
    Select=[each.replace(' ',"_") for each in Select]
    From=[each.replace(' ',"_") for each in From]
    Where=[each.replace(' ',"_") for each in Where]
    Groupby=[each.replace(' ',"_") for each in Groupby]
    return {'SELECT': Select, 'FROM': From, 'WHERE': Where, "GROUP BY": Groupby}
def combine_sql(sql_element):
    sql=""
    for each in sql_element.keys():
        if sql_element[each]!=[]:

            sql=sql+each+' '
            for i in sql_element[each]:
                if i !=sql_element[each][-1]:
                    sql+=i+','
                elif i== sql_element[each][-1]:
                    sql+=i+' '
    return sql
def vis2sql(vis_str,table_name):
    sql_element=process_vis_str(vis_str,table_name)
    sql=combine_sql(sql_element)
    return sql
def sql_element2vis(sql_element):
    lux_intent=[]
    for each in sql_element['SELECT']:
        temp=each.split("(")  #判断有没有aggregation e.g. MEAN(x)
        if len(temp)==1:
            lux_intent.append(each)
        if len(temp)==2:
            lux_intent.append(lux.Clause(temp[1][:-1],aggregation=temp[0].lower()))
    for each in sql_element['WHERE']:
        lux_intent.append(each)
    if len(sql_element['FROM'])>1:
        print('lux does not support cross-df recommendation!!!!')
    table_name=sql_element['FROM'][0]
    return lux_intent,table_name


if __name__=='__main__':
    str1 = '<Vis  (x: SATAverage, y: ACTMedian -- [Geography=Mid-size City]) mark: scatter, score: 0.9916226012723789 >'
    str2 = '<Vis  (x: BIN(Expenditure), y: COUNT(Record)) mark: histogram, score: 2.5241522522787068 >'
    str3 = '<Vis  (x: SATAverage, y: ACTMedian, color: HighestDegree) mark: scatter, score: 0.3333333333333333 >'
    str4 = '<Vis  (x: MEAN(SATAverage), y: HighestDegree) mark: bar, score: 1 >'
    sql=process_vis_str(str4,'table_name111')
    print('sql',sql)
    combined_sql=combine_sql(sql_element=sql)
    print('combined_sql',combined_sql)
    vis=sql_element2vis(sql)
    print('vis_intent',vis[0])


