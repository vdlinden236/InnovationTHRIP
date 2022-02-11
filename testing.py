import pymssql

host = "197.189.232.50"
username = "FE-User"
password = "Fourier.01"
database = "PGAluminium"

conn = pymssql.connect(host, username, password, database)
c1 = conn.cursor()

c1.execute(
    """
    Select distinct
    u.UserId, u.UserName
    from Users u
    left join UserRoles r on
    u.UserId=r.UserId
    where r.RoleId>1 and u.IsActive = 1


    """)

print(c1.fetchall())

conn.commit()

conn.close()

