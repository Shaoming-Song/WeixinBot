# coding: utf-8
import sys
import re
import xmlrpclib


s = xmlrpclib.ServerProxy('http://localhost:12345')

re_dict = {
        '^查询$':s.lookup,
        '^查询 [a-z]{2,3}$':s.lookup,
        '^签入$':s.login,
        '^签到$':s.login,
        '^签出$':s.logout,
        '^统计$':s.summary,
        '^排名$':s.rank,
        '^读取状态$':s.read_state,
        '^sudo清空重置$':s.reset,
        '^[0-9]{9} [a-z]{2,3}$':s.date_login,
        }


