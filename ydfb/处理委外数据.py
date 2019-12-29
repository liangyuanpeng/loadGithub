import pymysql
import xlrd
data = xlrd.open_workbook('todo.xls') # 打开xls文件
table = data.sheets()[0] # 打开第一张表
nrows = table.nrows      # 获取表的行数
# for i in range(nrows):   # 循环逐行打印
#     if i == 0: # 跳过第一行
#         continue
#     print(table.row_values(i)[0]) # 取前十三列
#     print(table.row_values(i)[1])  # 取前十三列

try:
    #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
    conn=pymysql.connect(host='rdsn9l3p090m05l1rhc8o.mysql.rds.aliyuncs.com',user='fenbei',passwd='AbCd12345',db='fenbei_dh',port=3306,charset='utf8')
    # conn=pymysql.connect(host='jdbc:mysql://rdsn9l3p090m05l1rhc8o.mysql.rds.aliyuncs.com:3306/fenbei_dh?characterEncoding=UTF-8',user='fenbei',passwd='AbCd12345',db='fenbei_dh',port=3306,charset='utf8')
    # conn=pymysql.connect(host='10.0.0.12',user='root',passwd='root1',db='fenbei_dh4',port=3306,charset='utf8')
    cur=conn.cursor()#获取一个游标
    sql_select = "select id from tb_borrower where idcard = '%s'"
    sql_select_name = "select id from tb_borrower where name = '%s'"
    sql_select_tb_loanInfo = "select * from  tb_loanInfo WHERE borrowerId = '%s'"
    sql_update_tb_loanInfo = "update tb_loanInfo set loanStateId = 116 , loanStateName = '委外',overdueModId='%s' where borrowerId = '%s'"
    sql_select_tb_loanInfo_again = "select loanStateId,loanStateName,overdueModId from tb_loanInfo where borrowerId = '%s'"
    sql_select_tb_syspara = "SELECT * FROM tb_syspara WHERE kType = 104 where text = '%s' "
    sql_select_tb_loanInfo_loanState = "select overdueModName from  tb_loanInfo WHERE borrowerId = '%s'"

    sql_select_tb_syspara = "SELECT sNo FROM tb_syspara WHERE kType = 104 and text = '%s'"

    try:
        for i in range(nrows):  # 循环逐行打印
            if i == 0:  # 跳过第一行
                continue

            cur.execute(sql_select % (table.row_values(i)[1]))  # 像sql语句传递参数

            borrowerId = ''
            result = cur.fetchall()
            # print("result:{0},idcard:{1}".format(result,table.row_values(i)[1]))
            # print(len(result))
            # print(result)
            if(len(result)==0):
                cur.execute(sql_select_name % (table.row_values(i)[0]))
                result2 = cur.fetchall()
                if(len(result2)==0):
                    continue;
                borrowerId = result2[0][0]
                print("idcard is none,name query:{0}".format(result2))
            else:
                borrowerId = result[0][0]

            cur.execute(sql_select_tb_loanInfo_loanState % (borrowerId))
            result3 = cur.fetchall()
            # print("result3:{0}".format(result3))
            # print(result3)
            if(len(result3)>0):
                # print(result3[0][0])
                cur.execute(sql_select_tb_syspara % (result3[0][0]))
                result4 = cur.fetchall()
                if(len(result4)>0):
                    # print(result4[0][0])
                    overdueModId = result4[0][0]
                    print(sql_update_tb_loanInfo % (overdueModId,borrowerId))
                    cur.execute(sql_update_tb_loanInfo % (overdueModId,borrowerId))

            # print(sql_update_tb_loanInfo % borrowerId)
            # cur.execute(sql_update_tb_loanInfo % borrowerId)

            # print(result[0][0])

        # 提交
        print("执行commit")
        conn.commit()

        for i in range(nrows):
            if i == 0:  # 跳过第一行
                continue
            cur.execute(sql_select % (table.row_values(i)[1]))  # 像sql语句传递参数

            borrowerId = ''
            result = cur.fetchall()
            if(len(result)==0):
                cur.execute(sql_select_name % (table.row_values(i)[0]))
                result2 = cur.fetchall()
                if (len(result2) == 0):
                    continue;
                borrowerId = result2[0][0]
                print("idcard is none,name query:{0}".format(result2))
            else:
                borrowerId = result[0][0]

            # print(sql_select_tb_loanInfo_again % (borrowerId))
            cur.execute(sql_select_tb_loanInfo_again % (borrowerId))  # 像sql语句传递参数
            result = cur.fetchall()
            if(result[0][0]!=116):
                print("fail:{0}".format(result))
            # else:
                # print("success:{0}".format(result[0][0]))
            # print(result[0][0])
    except Exception as e:
        # 错误回滚
        print(table.row_values(i)[1])
        print(e)
        conn.rollback()

    cur.close()#关闭游标
    conn.close()#释放数据库资源
except  Exception :print("查询失败")