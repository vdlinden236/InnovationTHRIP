import threading
import os
import os.path
from flask_database import db
import pymssql
import datetime
import json

table_lock = threading.Lock()


def execute_update(survey_id, user_id, org_id, results, comments):
    table_lock.acquire()
    print(survey_id)
    print(user_id)
    print(org_id)
    print(results)
    print(comments)

    for x, y in results.items():
        db.execute("""Insert into [thrip].[selections]
                    (OrgID, userID, orgsurveyID, optionID, questionID)
                    values ({}, {}, {}, {}, {})""".format(org_id, user_id, survey_id, y, x))

    for x, y in comments.items():
        db.execute("""UPDATE [thrip].[selections]
                    SET comment = '{}' where OrgID = {} and questionID = {}""".format(y, org_id, int(x)))

    db.execute("""Insert into [thrip].[usersurveys]
                        (surveyID, OrgID, UserID)
                        values ({}, {}, {})""".format(survey_id, org_id, user_id))

    db.commit()
    table_lock.release()
