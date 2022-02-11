from flask import session
import csv, pymssql, datetime
import threading

table_lock = threading.Lock()
def create_csv_rep(orgid, filename):
    table_lock.acquire()
    host = "197.189.232.50"
    username = "FE-User"
    password = "Fourier.01"
    database = "PGAluminium"

    conn = pymssql.connect(host, username, password, database)
    cursor = conn.cursor()



    def add_headers(columns):
        with open('static/reports/'+filename,mode='w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(columns)
            csvFile.close()

    def add_data(data):
        #for col, val in enumerate(data):
         #   if isinstance(val, datetime.datetime):
          #      lysie = list(data)
           #     lysie[col] = lysie[col].date()
            #    data = tuple(lysie)
        with open('static/reports/'+filename,mode='a') as csvFile:
            writer = csv.writer(csvFile, delimiter=",",quoting=csv.QUOTE_MINIMAL)
        #for col, val in enumerate(data):
            writer.writerow(data)
        csvFile.close()
        return


    # Main --------------------------------------------------------------
    org = orgid
    forceUpdate = 1

    sql1 = """EXEC [dbo].[my_sp] @orgid=?,@forceUpdate=?;"""
    sql1 = "DECLARE	@return_value int; \
            EXEC	@return_value = [dbo].[ReportContractItemsForOrg] \
                @orgid = ?, \
                @forceUpdate = ?; \
            SELECT	'Return Value' = @return_value;"

    sql1 = """DECLARE @RC int;
        EXEC @RC = [dbo].[ReportContractItemsForOrg] {}, {};
        SELECT @RC AS rc;""".format(orgid, forceUpdate)
    report_table_name = "ReportContractItems_" + str(orgid)
    # sql = "EXEC [dbo].[ReportContractItemsForOrg] {}, {};".format(orgid, forceUpdate)
    sql = "EXEC [dbo].[GenerateDynamicReport] {}, {};".format(orgid, forceUpdate)
    sql2 = "EXEC [dbo].[CreateReportTableForOrg] {}".format(session["OrgId"])
    cursor.execute(sql)
    # cursor2.execute(sql2)
    columns = [column[0] for column in cursor.description]
    add_headers(columns)

    row = 1
    data = cursor.fetchone()
    while data is not None:
        row += 1
        add_data(data)
        data = cursor.fetchone()
        print(row)
        # worksheet1.autofilter('B2:AG39')
    conn.commit()
    table_lock.release()

