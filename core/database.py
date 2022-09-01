import sqlite3, pathlib

# Database:     cache\index.db
# Table:        files
# Values:       uuid url type size accessed encoding statuscode
#               0    1   2    3    4        5        6
# Primary key:  uuid

# Filepath for cached files: uuid\file

def connect():
    pathlib.Path(".\\cache").mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(".\\cache\\index.db")
    cursor = connection.cursor()
    return connection, cursor

def create():
    connection, cursor = connect()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `files` (
            uuid TEXT PRIMARY KEY,
            url TEXT,
            type TEXT,
            size INTEGER, 
            accessed REAL,
            encoding TEXT,
            statuscode INTEGER
        )""")
    connection.close()

def insert(wf):
    connection, cursor = connect()
    sql = """
    INSERT INTO `files` VALUES ('%s', '%s', '%s', %i, %f, '%s', %i)
    """ % (
        wf.uuid,
        wf.url,
        wf.type,
        wf.size,
        wf.accessed,
        wf.encoding,
        wf.status_code
    )
    cursor.execute(sql)
    connection.commit()
    connection.close()

# def update(wf):
#     connection, cursor = connect()
#     sql = """
#     UPDATE `files` SET
#         url = '%s',
#         file = '%s',
#         type = '%s',
#         size = %i,
#         accessed = %f,
#         encoding = '%s',
#         statuscode = %i
#     WHERE uuid = %s""" % (
#         wf.url,
#         wf.file,
#         wf.type,
#         wf.size,
#         wf.accessed,
#         wf.encoding,
#         wf.status_code,
#         wf.uuid
#     )
#     cursor.execute(sql)
#     connection.commit()
#     connection.close()

# def exists(url):
#     return bool(get(url))

def get(url):
    connection, cursor = connect()
    sql = """
    SELECT *
    FROM `files`
    WHERE url = '%s'
    """ % url
    cursor.execute(sql)
    row = cursor.fetchone()
    connection.close()
    return row


def get_history():
    connection, cursor = connect()
    sql = """
    SELECT *
    FROM `files`
    WHERE type = 'text/html'
    ORDER BY accessed DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    connection.close()
    return rows


create()