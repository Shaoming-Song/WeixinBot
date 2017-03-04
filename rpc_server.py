# coding: utf-8
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import datetime
from name_dict import name_dict
from name_dict import name_abbr
from id_group import id_dict

server = SimpleXMLRPCServer(('localhost', 12345))

memberNum = 15
state_in = [0 for i in range(memberNum)]
date_time_init = datetime.datetime.now() - datetime.timedelta(2)
time_init_temp = date_time_init.strftime('%Y-%m-%d %H:%M')
time_init = datetime.datetime.strptime(time_init_temp, '%Y-%m-%d %H:%M')
last_login = [time_init for i  in range(memberNum)]

online_time = [[datetime.timedelta(0) for i in range(memberNum)] for i in range(7)]


def readStatus(dst):
    fd = open('cache','r')
    num = 0
    for lines in fd.readlines():
        content_all = lines.split('\t')
        
        state_in[num] = (int)(content_all[0])
        last_login[num] = datetime.datetime.strptime(content_all[1], '%Y-%m-%d %H:%M:%S')
        for i in range(7):
            print(content_all[2+i])
            print((str)(i))
            temp_time = content_all[2+i][:-2]
            online_time[i][num] = datetime.timedelta(0,(int)(temp_time))
        num = num + 1
    msg = '读取成功'
    return msg

def checkLogInfo(log_info):
    action = int(log_info['state']) #'0': logout, '1': login
    name = log_info['name']
    id = int(id_dict[name])
    time = datetime.datetime.strptime(log_info['time'], '%Y-%m-%d %H:%M')
    info = ''
    flag = False

    if state_in[id] is 0 and action is 0:
        info = '【签出失败】您尚未登入'
        return info, flag
    elif state_in[id] is 1 and action is 1:
        info = '【签到失败】您尚未登出'
        return info, flag
    elif state_in[id] is 0 and action is 1:
        if last_login[id] > time:
            info = '【签到失败】签入时间在签出时间之前'
        elif time - datetime.datetime.now() >= datetime.timedelta(0, 3600): #登入时间超出当前时间一小时
            info = '【签到失败】签入时间超出当前时间1小时'
        else:
            last_login[id] = time
            state_in[id] = 1
            weekday = time.weekday()
            if online_time[weekday][id] == datetime.timedelta(0):
                info = '您刚开始沉迷学习，加油'
            else:
                info = '您今日沉迷学习时间为：' + str(online_time[weekday][id])
            flag = True
        return info, flag
    elif state_in[id] is 1 and action is 0:
        if last_login[id] > time:
            info = '【签出失败】签出时间在签入时间之前'
        elif time - datetime.datetime.now() >= datetime.timedelta(0, 3600):
            info = '【签出失败】签出时间超出当前时间1小时'
        else:
            state_in[id] = 0
            duration = time - last_login[id]
            weekday = time.weekday()
            online_time[weekday][id] = online_time[weekday][id] + duration
            #online_time_sum[id] = online_time_sum[id] + duration
            info = '本次学习时间为：' + str(duration) + '\n今日沉迷学习时间为：' + str(online_time[weekday][id])
            flag = True
        return info, flag

def handleCheck(check_info, dst):
    name = check_info['name']
    id = int(id_dict[name])
    time = datetime.datetime.strptime(check_info['time'], '%Y-%m-%d %H:%M')

    duration = (time - last_login[id]) * state_in[id]
#        if state_in[id] is 1:
#            duration = time - last_login[id]
#        else:
#            duration = datetime.timedelta(0)

    weekday = time.weekday()
    online_time_curr = online_time[weekday][id] + duration
    #rank = memberNum + 1

    #for i in range(memberNum):
    #    if online_time_curr >= online_time[weekday][i] + (time - last_login[i]) * state_in[i]:
    #        rank = rank - 1
    #msg = name + '今日在线总时间为：' + str(online_time_curr) + '\n排名第' + str(rank) + '位'
    msg = name + '今日在线总时间为：' + str(online_time_curr)
    return msg

def timeSum(check_info, dst):
    name = check_info['name']
    id = int(id_dict[name])
    time = datetime.datetime.strptime(check_info['time'], '%Y-%m-%d %H:%M')

    duration = (time - last_login[id]) * state_in[id]
#        if state_in[id] is 1:
#            duration = time - last_login[id]
#        else:
#            duration = datetime.timedelta(0)

    weekday = time.weekday()
    sum_time = datetime.timedelta(0)
    for i in range(weekday + 1):
        sum_time = sum_time + online_time[i][id]
    sum_time = sum_time + duration
    msg = name + '本周在线总时间为：' + str(sum_time)
    return msg

def timeRank(check_info, dst):
    online_time_sum = [datetime.timedelta(0) for i in range(memberNum)]
    totalseconds = [0 for i in range(memberNum)]
    name = check_info['name']
    id = int(id_dict[name])
    time = datetime.datetime.strptime(check_info['time'], '%Y-%m-%d %H:%M')
    for i in range(memberNum):
        duration = (time - last_login[i]) * state_in[i]
        weekday = time.weekday()
        for j in range(weekday + 1):
            online_time_sum[i] = online_time_sum[i] + online_time[j][i]
        online_time_sum[i] = online_time_sum[i] + duration
        totalseconds[i] = online_time_sum[i].total_seconds()
    name_list = ['xky','ssm','ly','hjf','gjq','gdx','zrb','hxf','yc','lsy','test','ldy','wjl','wj','cjn']
    lists = zip(totalseconds, online_time_sum, name_list)
    lists.sort(key=lambda x:x[0],reverse=True)
    msg = '本周目前排名：\n'
    rank = 0
    for i in range(memberNum):
        msg = msg + lists[i][2] + ' ' + str(lists[i][1]) + '\n'
        if lists[i][2] == name:
            rank = i + 1
    if rank != 0:
        msg = msg + name + "的目前排名：" + (str)(rank)
    return msg

#####
# RPC call API
#####

def lookup(content, dst, srcName):
    log_info = ''
    content_new = content.replace('<br/>', '\n')
    buffer_content = content.split()
    info = ''

    date_time = datetime.datetime.now()
    name = ''
    if len(buffer_content) == 1:
        name = srcName.decode('UTF-8')
    elif len(buffer_content) == 2 and buffer_content[1].isalpha():
        name = buffer_content[1].decode('UTF-8')

    if name_dict.has_key(name):
        info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[name] + ' login' 
        check_info = {'name' : name_dict[name], 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
        log_info = ''
        msg = handleCheck(check_info, dst)
    else:
        msg = ''
    return msg, ''

def login(content, dst, srcName):
    date_time = datetime.datetime.now()
    print repr(srcName)
    print srcName
    name = srcName.decode('UTF-8')
    if name_dict.has_key(name):
        info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[name] + ' login' 
        log_info = {'name' : name_dict[name], 'state' : '1', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
        msg = info + '【自动回复】'
        extra_msg, flag = checkLogInfo(log_info)
        if not flag:
            msg = ''
    else:
        msg = ''
        extra_msg = ''

    return msg, extra_msg

def logout(content, dst, srcName):
    date_time = datetime.datetime.now()
    name = srcName.decode('UTF-8')
    if name_dict.has_key(name):
        info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[name] + ' logout' 
        log_info = {'name' : name_dict[name], 'state' : '0', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
        msg = info + '【自动回复】'
        extra_msg, flag = checkLogInfo(log_info)
        if not flag:
            msg = ''
    else:
        msg = ''
        extra_msg = ''

    return msg, extra_msg

def summary(content, dst, srcName):
    content_new = content.replace('<br/>', '\n')
    buffer_content = content.split()
    date_time = datetime.datetime.now()
    name = ''
    if len(buffer_content) == 1:
        name = srcName.decode('UTF-8')
    elif len(buffer_content) == 2 and buffer_content[1].isalpha():
        name = buffer_content[1].decode('UTF-8')

    if name_dict.has_key(name):
        check_info = {'name' : name_dict[name], 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
        msg = timeSum(check_info, dst)
    else:
        msg = ''

    return msg, ''

def rank(content, dst, srcName):
    date_time = datetime.datetime.now()
    name = srcName.decode('UTF-8')
    check_info = {'name' : name_dict[name], 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
    msg = timeRank(check_info, dst)
    return msg, ''

def read_state(content, dst, srcName):
    msg = readStatus(dst)
    return msg, ''

def reset(content, dst, srcName):
    date_time = datetime.datetime.now()
    fn = 'data\data_' + date_time.strftime('%Y-%m-%d')
    fd = open(fn,'w+')
    for i in range(memberNum):
        line = (str)(state_in[i]) + '\t' + (str)(last_login[i])
        for j in range(7):
            line = line + '\t' + (str)(online_time[j][i].total_seconds())
        line = line + '\t'+ 'end' + '\n'
        fd.write(line)
    fd.close()
    for i in range(memberNum):
        state_in[i] = 0
        last_login[i] = time_init
        for j in range(7):
            online_time[j][i] = datetime.timedelta(0)
    fd = open('cache','w+')
    for i in range(memberNum):
        line = (str)(state_in[i]) + '\t' + (str)(last_login[i])
        for j in range(7):
            line = line + '\t' + (str)(online_time[j][i].total_seconds())
        line = line + '\t'+ 'end' + '\n'
        fd.write(line)
    fd.close()
    return 'reset'

def date_login(content, dst, srcName):
    try:
        if len(buffer_content) == 2 and buffer_content[0].isdigit() and buffer_content[1].isalpha():
            if len(buffer_content[0]) == 9:
                time = buffer_content[0][0:8]
                state = buffer_content[0][8]
                usr = buffer_content[1]

                date_time = datetime.datetime(datetime.date.today().year, 
                    int(buffer_content[0][0:2]), int(buffer_content[0][2:4]),
                    int(buffer_content[0][4:6]), int(buffer_content[0][6:8]))

                if state is '1' :
                    if name_dict.has_key(usr):
                        if usr == 'gjq':
                            date_time = date_time + datetime.timedelta(0, 46800)
                            info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[usr] + ' login' 
                            log_info = {'name' : name_dict[usr], 'state' : '1', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
                        else:
                            info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[usr] + ' login' 
                            log_info = {'name' : name_dict[usr], 'state' : '1', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
                    else:
                        info = '用户未注册'
                        log_info = ''
                elif state is '0':
                    if name_dict.has_key(usr):
                        if usr == 'gjq':
                            date_time = date_time + datetime.timedelta(0, 46800)
                            info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[usr] + ' logout' 
                            log_info = {'name' : name_dict[usr], 'state' : '0', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
                        else:
                            info = '[' + date_time.strftime('%Y-%m-%d %H:%M') + ']: ' + name_dict[usr] + ' logout' 
                            log_info = {'name' : name_dict[usr], 'state' : '0', 'time' : date_time.strftime('%Y-%m-%d %H:%M')}
                    else:
                        info = '用户未注册'
                        log_info = ''
                else:
                    info = 'error'
                    log_info = ''
            else:
                msg = '时间格式错误【自动回复】'
                log_info = ''
    except Exception, e:
        msg = ''
        log_info = ''
        pass

    if log_info == '':
        msg, extra_msg = '', ''
    else:
        msg = info + '【自动回复】'
        extra_msg, flag = checkLogInfo(log_info)
        if not flag:
            msg = ''

    return msg, extra_msg

server.register_function(lookup, 'lookup')
server.register_function(login, 'login')
server.register_function(logout, 'logout')
server.register_function(summary, 'summary')
server.register_function(rank, 'rank')
server.register_function(read_state, 'read_state')
server.register_function(reset, 'reset')
server.register_function(date_login, 'date_login')

server.serve_forever()
