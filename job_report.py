import pymssql, xlsxwriter, datetime
from flask import session

def job_report(orgid, filename):
    # prepair excel sheets ------------------------------------------------------------
    workbook = xlsxwriter.Workbook('static/reports/'+filename)
    date = workbook.add_format({'num_format':'dd-mm-yyyy'})
    bold = workbook.add_format({'bold':1})
    worksheet1 = workbook.add_worksheet('Filters')
    bg_darkBlue = workbook.add_format({'bg_color':'#005ce6'})
    bg_lightBlue1 = workbook.add_format({'bg_color':'#99c2ff'})
    bg_lightBlue2 = workbook.add_format({'bg_color':'#cce0ff'})
    bg_lightBlue1Date = workbook.add_format({'bg_color':'#99c2ff','num_format':'dd-mm-yyyy'})
    bg_lightBlue2Date = workbook.add_format({'bg_color':'#cce0ff','num_format':'dd-mm-yyyy'})


    # connect --------------------------------------------------------------------------

    host = "197.189.232.50"
    username = "FE-User"
    password = "Fourier.01"
    database = "PGAluminium"

    conn = pymssql.connect(host, username, password, database)
    cursor = conn.cursor()
    #cursor2 = conn.cursor()
    # Functions ---------------------------------------------------------
    def add_headers(columns):
        row = 0
        for col,name in enumerate(columns):
            worksheet1.write(row, col, name, bg_darkBlue)
            worksheet1.set_column(row, col, 20)
        return

    def add_data(data,row):
        if row%2==0:
            gbColour= bg_lightBlue1
            gbColourDate = bg_lightBlue1Date
        else:
            gbColour = bg_lightBlue2
            gbColourDate = bg_lightBlue2Date
        for col,val in enumerate(data):
            if isinstance(val,datetime.datetime):
                worksheet1.write(row, col, val, gbColourDate)
            else:
                worksheet1.write(row, col, val,gbColour)
        return

    # Main --------------------------------------------------------------
    org=orgid

    
    sql1 = """EXEC [dbo].[my_sp] @orgid=?,@forceUpdate=?;"""
    sql1 = "DECLARE	@return_value int; \
        EXEC	@return_value = [dbo].[ReportContractItemsForOrg] \
            @orgid = ?, \
            @forceUpdate = ?; \
        SELECT	'Return Value' = @return_value;"


    sql = "EXEC [dbo].[JobReportView] {};".format(orgid)

    cursor.execute(sql)
    #cursor2.execute(sql2)
    columns = [column[0] for column in cursor.description]
    add_headers(columns)

    row = 0
    data = cursor.fetchone()
    #add_data(data,row)
    while data is not None:
        row +=1
        add_data(data,row)
        data = cursor.fetchone()
        #print(row)
    #worksheet1.autofilter('B2:AG39')
    worksheet1.autofilter(0,0,row,len(columns)-1)
    workbook.close()
    conn.commit()
