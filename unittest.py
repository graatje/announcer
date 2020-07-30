import random
import databasefunctions
import datetime
def test1():
    channels = [737712298315087924, 698615458714222631, 652087685124456452]
    db = databasefunctions.DatabaseFunctions("events.db")
    for i in range(1000):
        db.addEvent(nameGenerator(), random.choice(channels), dateGenerator(), random.randint(12, 30))
def nameGenerator():
    alphabet='abcdefghijklmnopqrstuvwxyz'
    name=''
    for i in range(random.randint(5, 20)):
        name+=random.choice(alphabet)
    return name
def dateGenerator():
    """
    returns a datetime.datetime object.
    """
    year = 2020
    month=7
    day=28
    hour=random.randint(0, 23)
    minutes = random.randint(0, 59)
    realtime = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minutes, second=00, tzinfo=datetime.timezone.utc)
    return realtime
help(dateGenerator)
