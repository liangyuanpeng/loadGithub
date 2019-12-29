import pymysql
import xlrd
data = xlrd.open_workbook('business20180929.xlsx') # 打开xls文件
table = data.sheets()[0] # 打开第一张表
nrows = table.nrows      # 获取表的行数

try:
    #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
    conn=pymysql.connect(host='47.93.201.235',user='root',passwd='root',db='fenbei',port=3389,charset='utf8')
    # conn=pymysql.connect(host='rdsn9l3p090m05l1rhc8o.mysql.rds.aliyuncs.com',user='fenbeicx',passwd='EdianFb2017*',db='fenbeicx',port=3306,charset='utf8')
    cur=conn.cursor()#获取一个游标
    # sql_select = "select * from d_business where business_name_simple like '%%%%%s%%%%'"
    sql_select = "select * from d_business where business_name_simple = '%s'"
    sql_update = "update d_business set user_name = '%s' where id = %s and user_name is null"

    try:
        for i in range(nrows):  # 循环逐行打印
            if i == 0:  # 跳过第一行
                continue
            print(sql_select % table.row_values(i)[2])
            cur.execute(sql_select % table.row_values(i)[2])
            result = cur.fetchall()
            if(len(result)>0):
                # print("business_id:{0}".format(result[0][0]))
                print(sql_update % (table.row_values(i)[6],result[0][0]))
                cur.execute(sql_update % (table.row_values(i)[6],result[0][0]))
            # print()
            # print(result)
        # print(table.row_values(i)[6])


        # 提交
        print("执行commit")
        conn.commit()

    except Exception as e:
        # 错误回滚
        print(table.row_values(i)[1])
        print(e)
        conn.rollback()

    cur.close()#关闭游标
    conn.close()#释放数据库资源
except  Exception :print("查询失败")