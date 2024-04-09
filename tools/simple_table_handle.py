import copy
def load_table(path):
    with open(path, encoding='UTF-8') as f:
        table = eval(f.read())
    return table

'''判断是中文还是英文'''
def language_judgement(table):
    for i in range(len(table)):
        if table[i]['node_type']=='key':  #判断所有的key,如果出现中文，则判断为中文，否则判断为英文language=1
            str_context = table[i]['context']
            for char in str_context:
                if "\u4e00"<= char <= "\u9fff":
                    language = 0
                    break
                else: language = 1
        if language==0: break           #只要表头中出现中文，就判断为中文表格
    return language

'''获取表格真的行数和列数'''
def count_table(table):
    #行数是真，列数有充数，先得到真实的行数rownum和列数colnum，不分横表竖表   unrownum表示原始表格的行数；rownum表示转换成横表后的表格行数
    unrownum=table[-1]['rowspan'][1]-table[0]['rowspan'][0]+1       #表格行数rownum
#表格列数colnum，遍历每行列数colcount+=col_count（可能不是每行的列数，但不影响获取表格列数），(colcount=[]),取列数最大值即为表格列数
    colcount=[]
    retable=copy.deepcopy(table)  #复制table得到retable，只是为了保留原表，不影响后续函数的使用
    if table[0]['rowspan'][1]==table[-1]['rowspan'][1]:   #如果左侧跨列表头，遍历第二行时会少一个
        col_count=2   #在col_count=1 的基础上再+1
        del retable[0]
        for i in range(len(retable) - 1):
            if retable[i]['colspan'][1] <= retable[i + 1]['colspan'][0]:
                col_count += 1
                colcount.append(col_count)
            else:
                col_count = 2
    else:                                                  #左侧无跨列表表头
        col_count=1
        for i in range(len(retable) - 1):
            if retable[i]['colspan'][1] <= retable[i + 1]['colspan'][0]:
                col_count += 1
                colcount.append(col_count)
            else:
                 col_count = 1

    uncolnum=max(colcount)
    return unrownum,uncolnum

'''得到行列后，判断是否为竖表：将竖表进行转置，行数列数也需交换'''

def horizon_table(table,unrownum,uncolnum):

    # 判断是否是竖表
    for i in range(len(table)):
        if table[i]['node_type'] != 'key':  # 从第一个不是key类型的单元格往后，不再出现key类型的单元格，则为横表h=0，不需要转置
            for j in range(1, len(table) - i - 1):  # 遍历后面的单元格
                h = 0  # 若不会进入if,则为横表
                if table[i + j]['node_type'] == 'key':  # 再次出现key，说明是竖表h=1，需要转置
                    h = 1
                    break
            break
    if h == 1:
        retable = copy.deepcopy(table)
        rownum,colnum=uncolnum,unrownum  #竖表转置，行列数需要交换
        for i in range(len(table)):  # 每一个单元格都转置，table变成横表
            table[i]['colspan'] = retable[i]['rowspan']
            table[i]['rowspan'] = retable[i]['colspan']
        # 摆正table里元素的顺序：先比较rowspan[0]，rowspan一样时比较colspan[0],值小的排前面；
        for i in range(len(table) - 1):
            for j in range(i + 1, len(table)):
                if table[j]['rowspan'][0] < table[i]['rowspan'][0]:  # 后者行标小于或等于前者，换一下
                    table[i], table[j] = table[j], table[i]
                if table[j]['rowspan'][0] == table[i]['rowspan'][0]:  # 后者行标等于前者，比较列标
                    if table[j]['colspan'][0] < table[i]['colspan'][0]:  # 后者列标更小，应该交换位置
                        table[i], table[j] = table[j], table[i]
    else:rownum,colnum=unrownum,uncolnum

     #横表和竖表解决压力资料问题前提（小key需要紧挨着大key'压力资料'）：
    # 再在key里排序(解决压力资料的问题）当col[0]小的排前面，当col[0]一样时，row[0]小的排前面
    for i in range(len(table)-1):
        if table[i]['node_type']=='key':
            for j in range(i+1,len(table)):
                if table[j]['node_type']=='key':
                    if table[j]['colspan'][0] < table[i]['colspan'][0]:
                        table[i], table[j] = table[j], table[i]
                    if table[j]['colspan'][0] == table[i]['colspan'][0]:
                        if table[j]['rowspan'][0] < table[i]['rowspan'][0]:
                            table[i], table[j] = table[j], table[i]
                else:break
        else:break
    return table,rownum,colnum,h

''' 将横表处理成标准化表'''
def split_table(table, colnum, rownum,h,language):

    '''将横跨表格行或表格列的表头与普通key融合'''
    head = []
    if table[0]['colspan'][1] - table[0]['colspan'][0] + 1 == colnum:  # 若是列表头，删除列表头，列数减一，行数不变生成表格
        if language ==0:
            str = table[0]['context'] + "的"
        else:
            str =table[0]['context'] + "'s "
        head += str
        rownum = rownum - 1
        del table[0]
    elif table[0]['rowspan'][1] - table[0]['rowspan'][0] + 1 == rownum: #同理
        if language == 0:
            str = table[0]['context'] + "的"
        else:
            str = table[0]['context'] + "'s "
        head += str
        colnum = colnum - 1
        del table[0]
    head="".join(head)

    ''' 处理 压力资料 类型（需要区分横表竖表）'''
    if h==0:#横表处理：
        i=0
        while table[i]['node_type'] == 'key':# 当标签是key ,一行之内，若有压力资料类型，则碰上；若第一行没有碰上，则无”压力资料“类型

            if table[i]['rowspan'][1]==table[i]['rowspan'][0]:
                for j in range(1, len(table) - i):
                    if table[i + j]['node_type'] == "key" and table[i + j]['colspan'][0] >= table[i]['colspan'][0] and \
                            table[i + j]['colspan'][1] <= table[i]['colspan'][1] and table[i + j]['rowspan'][0] == \
                            table[i]['rowspan'][1] + 1:# 在下一行且是小key
                        table[i + j]['context'] = table[i]['context'] + '的' + table[i + j]['context']
                        if table[i + j]['colspan'][1] == table[i]['colspan'][1]:
                            del table[i]
                            i -= 1
                            break
            if table[i]['rowspan'][1] != table[i]['rowspan'][0]:  # 普通表头
                table[i]['rowspan'][0] = table[i]['rowspan'][1]
            i += 1

    elif h==1:#竖表处理
        i = 0
        while table[i]['node_type'] == 'key':  # 当标签是key ,一行之内，若有压力资料类型，则碰上；若第一行没有碰上，则无”压力资料“类型

            if table[i]['colspan'][1] != table[i]['colspan'][0]:
                for j in range(1, len(table) - i):
                    if table[i + j]['node_type'] == "key" and table[i + j]['colspan'][0] >= table[i]['colspan'][0] and \
                            table[i + j]['colspan'][1] <= table[i]['colspan'][1] and table[i + j]['rowspan'][0] == \
                            table[i]['rowspan'][1] + 1:  # 在下一行且是小key
                        table[i + j]['context'] = table[i]['context'] + '的' + table[i + j]['context']
                        table[i + j]['rowspan'][0]=table[i + j]['rowspan'][1]
                        if table[i + j]['colspan'][1] == table[i]['colspan'][1]:
                            del table[i]
                            i -= 1
                            break
            if table[i]['colspan'][1] == table[i]['colspan'][0]:  # 普通表头
                table[i]['rowspan'][0] = table[i]['rowspan'][1]
            i += 1

    '''标准化坐标'''
    rowdecrease = table[0]['rowspan'][0] - 1  # 行标准化坐标需减的差
    coldecrease = table[0]['colspan'][0] - 1
    if coldecrease!=0 or rowdecrease!=0:
        for i in range(len(table)):
            table[i]['rowspan'][0] = table[i]['rowspan'][0] - rowdecrease
            table[i]['rowspan'][1] = table[i]['rowspan'][1] - rowdecrease
            table[i]['colspan'][0] = table[i]['colspan'][0] - coldecrease
            table[i]['colspan'][1] = table[i]['colspan'][1] - coldecrease
#此时，rowspan从1开始，colspan从1开始，但colspan[1]-[0]没改变，意味着下面的规则表可能会出现几个相同的列(竖表出现的是相同行）

    '''生成规则表格'''
    splitted_table = [['' for _ in range(table[-1]['colspan'][1])] for _ in range(table[-1]['rowspan'][1])]  # 建立空表结构
    #生成第一行表头，其余都是value的规则表
    k=0
    for i in range(rownum):
        for j in range(colnum):
            if i+j+k<len(table):
                element = table[i + j + k]
                colstart = element['colspan'][0] - 1
                rowstart = element['rowspan'][0] - 1
                colend = element['colspan'][1]
                rowend = element['rowspan'][1]
                context = element['context']
                node_type = element['node_type']
                for m in range(rowstart, rowend):
                    for n in range(colstart, colend):
                        if node_type == 'key' and rowstart == 0:  # 两行表头
                            splitted_table[m][n] = head + context
                        else:
                            splitted_table[m][n] = context

        k+= (colnum-1)
    return splitted_table

'''删除重复的多余的行与列，得到 第一行表头，其余为对应value 的表格'''
def del_table(splitted_table,h):

    if h==1: #竖表，只会多重复的行
        for i in range(len(splitted_table)-1):
            if splitted_table[i+1]==splitted_table[i]:
                del splitted_table[i+1]
    if h == 0:  # 横表，只会多重复的列
        for i in range(len(splitted_table[0])-1):  #横表在第一行找相同的表头
            if i==0: k=1
            if k==0: i-=1  #上个循环删过列，i要减一    #阻止i+1超过列表索引
            if i<len(splitted_table[0])-1:
                if splitted_table[0][i + 1] == splitted_table[0][i]:  # 找到相邻相同表头
                    for j in range(1, len(splitted_table)):  # 看是否每一行的此两列元素都相同
                        k = 0  # 先默认相同
                        if splitted_table[j][i + 1] != splitted_table[j][i]:  # 若不相同
                            k = 1  # 表示有不同内容，不该删除
                            break
                    if k == 0:
                        for j in range(0, len(splitted_table)):
                            del splitted_table[j][i]

    return splitted_table

'''得到表头描述'''
def get_description(splitted_table,language):
    table_description = ""
    for i in range(1,len(splitted_table)):   #第i行
        for j in range(len(splitted_table[0])):   #第j列
            if language ==0:
                table_description += splitted_table[0][j] + "是" + splitted_table[i][j]  # 表头描述对应表格内容，按行描述
            else:
                table_description += splitted_table[0][j] + " is " + splitted_table[i][j]
            if j<len(splitted_table[0])-1:
                if language==0:
                    table_description += '，'
                else: table_description += ', '
            elif j==len(splitted_table[0])-1 and i != len(splitted_table)-1:
                 table_description += '； '
            else:
                if language==0:
                    table_description += '。'
                else:table_description += '. '
    return table_description

if __name__=='__main__':
    table=load_table('unhorizon(yaliziliao3).py')
    language=language_judgement(table)
    #print(count_table(table))
    unrownum,uncolnum=count_table(table)
    table,rownum,colnum,h=horizon_table(table,unrownum,uncolnum)
    splitted_table=split_table(table, colnum, rownum,h,language)
    splitted_table=del_table(splitted_table,h)
    #print(splitted_table)
    print(get_description(splitted_table,language))


