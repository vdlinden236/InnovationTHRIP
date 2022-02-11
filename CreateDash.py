from flask_database import db


def dashboard(orgid, timeframe='YTD'):

    if timeframe == 'YTD':
        timeframe = 'DATEADD(year,-1,GETDATE())'
    elif timeframe == 'MTD':
        timeframe = 'DATEADD(month,-1,GETDATE())'
    elif timeframe == 'WTD':
        timeframe = 'DATEADD(Week,-1,GETDATE())'

    total_jobs = db.engine.execute("""
                                  Select 
                                  COUNT(ContactNumber1) 
                                  from Contracts
                                  where OrgId = {} and Timestamp > {}
                                  """.format(orgid, timeframe)).fetchall()

    total_acts = db.engine.execute("""
                                  Select 
                                  COUNT(Description) 
                                  from ContractItems
                                  where OrgId = {} and Timestamped > {}
                                  """.format(orgid, timeframe)).fetchall()

    total_value = db.engine.execute("""
                                   Select 
                                   SUM(Value) 
                                   from Contracts
                                   where OrgId = {} and Timestamp > {}
                                   """.format(orgid, timeframe)).fetchall()

    JobsInProgress = db.engine.execute("""
                                                Select count(*) from Contracts 
                                                where OrgId = {} and ContactNumber1 = 'Start' and DueDate > GETDATE()
                                                """.format(orgid)).first()
    JobsInProgress = JobsInProgress[0]

    JobsOverdue = db.engine.execute("""
                                                Select count(*) from Contracts 
                                                where OrgId = {} and ContactNumber1 = 'Start' and DueDate < GETDATE()
                                                """.format(orgid)).first()
    JobsOverdue = JobsOverdue[0]

    JobsComplete = db.engine.execute("""
                                                Select count(*) from Contracts 
                                                where OrgId = {} and ContactNumber1 = 'Complete'
                                                """.format(orgid)).first()
    JobsComplete = JobsComplete[0]

    JobsCancelled = db.engine.execute("""
                                                Select count(*) from Contracts 
                                                where OrgId = {} and ContactNumber1 = 'Cancelled'
                                                """.format(orgid)).first()
    JobsCancelled = JobsCancelled[0]

    return total_jobs[0][0], total_acts[0][0], total_value[0][0], \
           JobsInProgress, JobsOverdue, JobsComplete, JobsCancelled

print(dashboard(14))