import pymysql
import xlrd
import xlwt

data = xlrd.open_workbook('todo2.xls') # 打开xls文件
table = data.sheets()[0] # 打开第一张表
nrows = table.nrows      # 获取表的行数

myWorkbook = xlwt.Workbook()
mySheet = myWorkbook.add_sheet('sheet1')

myStyle = xlwt.easyxf('font: name Times New Roman, color-index red, bold on',
                                      num_format_str='#,##0.00')  # 数据格式

 # mySheet.write(i, j, 1234.56, myStyle)

mySheet.write(0, 0, "借款人")
mySheet.write(0, 1, "期数")
mySheet.write(0, 2, "当前状态")
mySheet.write(0, 3, "财务状态")
mySheet.write(0, 4, "逾期天数")
mySheet.write(0, 5, "回款方式")
mySheet.write(0, 6, "是否核销")
# mySheet.write(0, 6, "核销金额")

mySheet.write(0, 7, "应还日期")
mySheet.write(0, 8, "实还日期")
mySheet.write(0, 9, "应还本金")
mySheet.write(0, 10, "实还本金")
mySheet.write(0, 11, "应还利息")
mySheet.write(0, 12, "实还利息")
mySheet.write(0, 13, "应还罚息")
mySheet.write(0, 14, "实还罚息")

mySheet.write(0, 15, "实还违约金")
mySheet.write(0, 16, "实还违约金")
mySheet.write(0, 17, "登记人")
mySheet.write(0, 18, "登记时间")
mySheet.write(0, 19, "备注")
row = 0
try:
    #获取一个数据库连接，注意如果是UTF-8类型的，需要制定数据库
    conn=pymysql.connect(host='rdsn9l3p090m05l1rhc8o.mysql.rds.aliyuncs.com',user='fenbei',passwd='AbCd12345',db='fenbei_dh',port=3306,charset='utf8')
    cur=conn.cursor()#获取一个游标
    sql_select = "select id from tb_borrower where idcard = '%s'"
    sql_select_name = "select id from tb_borrower where name = '%s'"
    sql_select_tb_loanInfo = "select * from  tb_loanInfo WHERE borrowerId = '%s'"
    sql_select_tb_loanInfo_again = "select loanStateId,loanStateName,overdueModId from tb_loanInfo where borrowerId = '%s'"
    sql_select_tb_syspara = "SELECT * FROM tb_syspara WHERE kType = 104 where text = '%s' "
    sql_select_tb_loanInfo_loanState = "select id from  tb_loanInfo WHERE borrowerId = '%s'"
    #逾期天数  overdue+overdueDays,
    #是否核销 repayModId是否等于107
    #主表 sumCanceledValue 核销金额,
    sql_select_tb_repayRecord = "SELECT repayStateName," \
                                "overdueModName,overdueDays,repayModName,repayModId,DATE_FORMAT(shouldRepayDate,'%%Y-%%m-%%d') ,DATE_FORMAT(actualRepayDate,'%%Y-%%m-%%d') ,shouldRepayPrincipal,actualRepayPrincipal," \
                                "shouldRepayInterest,actualRepayInterest,shouldRepayOverdueInterest,actualRepayOverdueInterest," \
                                "shouldRepayPenal,actualRepayPenal,lastEditStaffName,DATE_FORMAT(lastEditDate,'%%Y-%%m-%%d') ,remark " \
                                "FROM tb_repayRecord WHERE loanId= '%s' order by sNo ASC "
    sql_select_tb_syspara = "SELECT sNo FROM tb_syspara WHERE kType = 104 and text = '%s'"

    try:
        for i in range(nrows):  # 循环逐行打印
            if i == 0:  # 跳过第一行
                continue

            print(table.row_values(i)[0])
            # continue

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
                loan_info_id = result3[0][0]
                cur.execute(sql_select_tb_repayRecord % loan_info_id)
                result4 = cur.fetchall()
                # if(len(result4)==6):
                #     print(result4)
                for k in range(0, len(result4)):
                    # print(result4[i])
                    row += 1
                    # if row>10:
                    #     break
                    print(row)
                    mySheet.write(row, 0, table.row_values(i)[0])
                    mySheet.write(row, 1, k+1)
                    for v in range(0,len(result4[k])):
                        if v==4:
                            if result4[k][v]==107:
                                mySheet.write(row, v + 2, "是")
                            else:
                                mySheet.write(row, v + 2, "否")
                        else:
                            mySheet.write(row, v + 2, result4[k][v])
                        # print(result4[i][v])
            # if row>10:
            #     break;
        # 提交
        print("执行commit")

    except Exception as e:
        # 错误回滚
        print(table.row_values(i)[1])
        print(e)
        conn.rollback()

    cur.close()#关闭游标
    conn.close()#释放数据库资源
except  Exception :print("查询失败")
myWorkbook.save('d://张总-委外还款计划报表修复.xls')