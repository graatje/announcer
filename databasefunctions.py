import sqlite3
import datetime



class DatabaseFunctions:
    def __init__(self, file):
        self.conn=sqlite3.connect(file)
    def executeQuery(self, query):
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchall()
        
    def getEvents(self):
        cur = self.conn.cursor()
        cur.execute("SELECT events.name, events.channel, events.dateEvent, servers.pingrole , events.minsbeforeAnnouncement, events.isAnnounced FROM events, servers WHERE events.channel = servers.id")
        
        temp = list(cur.fetchall())
        rows=[]
        #converting tuple to list
        for i in temp:
            rows.append(list(i))

        #making datetime object from the string, setting booleans
        for i in range(len(rows)):
            if "+00:00" not in rows[i][2]:
                rows[i][2] += "+00:00"
            try:
                
                rows[i][2] = datetime.datetime.strptime(rows[i][2], '%Y-%m-%d %H:%M:%S.%f')
            except:
                
                rows[i][2] = datetime.datetime.strptime(rows[i][2], '%Y-%m-%d %H:%M:%S%z')
        
            if rows[i][5] == 0:
                rows[i][5] = False
            else:
                rows[i][5]=True
        return rows
    def getRepeatingEvents(self):
        cur = self.conn.cursor()
        cur.execute("SELECT repeating_events.name, repeating_events.channel, repeating_events.time, servers.pingrole , repeating_events.minsbeforeAnnouncement, repeating_events.weekday FROM repeating_events, servers WHERE repeating_events.channel = servers.id")
        temp = list(cur.fetchall())
        rows=[]
        #converting tuple to list
        for i in temp:
            rows.append(list(i))
        for i in range(len(rows)):

            rows[i][2] = datetime.datetime.strptime(rows[i][2], '%H:%M')
        return rows
    def addRepeatingEvent(self, name, channel, time, minsbeforeAnnouncement, weekday=None):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO repeating_events(name, channel, time, minsbeforeAnnouncement, weekday) VALUES(?,?,?,?,?)", (name,channel,time,minsbeforeAnnouncement, weekday))
        self.conn.commit()
    def addChannel(self, channelID, pingrole = "@everyone"):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO servers(id, pingrole) VALUES(?, ?)", (channelID, pingrole))
        self.conn.commit()
    def addEvent(self, name, channel, dateEvent, minsbeforeAnnouncement=30):
        if not self.isIn(name, channel, dateEvent, minsbeforeAnnouncement):
            cur = self.conn.cursor()
            cur.execute("INSERT INTO events(name, channel, dateEvent, minsbeforeAnnouncement, isAnnounced) VALUES(?,?,?,?, 0)", (name, channel, dateEvent, minsbeforeAnnouncement))
            self.conn.commit()
    def clearDueEvents(self):
        cur =self.conn.cursor()
        cur.execute("DELETE FROM events WHERE ? >= dateEvent", (datetime.datetime.now(),))
        self.conn.commit()
    def setAnnounced(self, name, channel, dateEvent, minsbeforeAnnounced, isAnnounced):
        cur= self.conn.cursor()
        cur.execute("UPDATE events SET isAnnounced=1 WHERE name=? and channel=? and dateEvent=? and minsbeforeAnnouncement=? and isAnnounced=?",(name, channel, dateEvent, minsbeforeAnnounced, isAnnounced))
    def isIn(self, name, channel, dateEvent, minsbeforeAnnouncement):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM events WHERE name=? and channel=? and dateEvent=? and minsbeforeAnnouncement=?", (name, channel, dateEvent, minsbeforeAnnouncement))
        if len(cur.fetchall()) != 0:
            return True
        return False
    def showEvents(self, channelID):
        allevents = "events happening:\n"
        cur =self.conn.cursor()
        cur.execute("SELECT id, name, dateEvent, minsbeforeAnnouncement FROM events WHERE channel = ?", (channelID,))
        rows = cur.fetchall()
      
        for i in rows:
            allevents += str("id: " + str(i[0])+ ", name event: " + str(i[1]) + ", date event: " + str(i[2].replace(":00+00:00", "")) + ", amount of minutes before announcement: " + str(i[3]) + "\n")

        allevents += "please note that tournaments are added daily around midnight."
        return allevents
    def showAllEvents(self, ownid):
        allevents = "events happening:\n"
        cur =self.conn.cursor()
        cur.execute("SELECT id, name, dateEvent, minsbeforeAnnouncement, channel FROM events")
        rows = cur.fetchall()
      
        for i in rows:
            allevents += str("id: " + str(i[0])+ ", name event: " + str(i[1]) + ", date event: " + str(i[2].replace(":00+00:00", "")) + ", amount of minutes before announcement: " + str(i[3]) + "server:" + str(i[4] )+ "\n")

        allevents += "please note that tournaments are added daily around midnight."
        if ownid == 300644437334425601:
        	return allevents
        else:
        	return "you have no permission to do that."
    def deleteEvent(self, eventid, channelID):
        cur =self.conn.cursor()
        cur.execute("SELECT id, name, dateEvent, minsbeforeAnnouncement FROM events WHERE channel = ? and id = ?", (channelID, eventid))
        rows=cur.fetchall()
        if len(rows) == 0:
            return "no event found, nothing deleted."
        elif len(rows)==1:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM events WHERE channel = ? and id = ?", (channelID, eventid))
            self.conn.commit()
            i = rows[0]
            return str("the following event is deleted\n id: " + str(i[0])+ ", name event: " + str(i[1]) + ", date event: " + str(i[2].replace(":00+00:00", "")) + ", amount of minutes before announcement: " + str(i[3]) + "\nit could take a few minutes before this has effect.")
        else:
            return "please contact kevin123456#2069, you should not see this."
def createDB():
    functions = DatabaseFunctions("events.db")
    functions.executeQuery("CREATE TABLE events(id integer primary key, name text not null, channel integer not null, dateEvent datetime, minsbeforeAnnouncement integer not null, isAnnounced integer not null)")
    functions.executeQuery("CREATE TABLE servers(id integer primary key, pingrole text not null)")
    functions.executeQuery("CREATE TABLE repeating_events(id integer primary key, name text not null, channel integer not null, time text not null, minsbeforeAnnouncement integer not null, weekday integer)")

    
try:
    open('events.db')
except FileNotFoundError:
    createDB()

#if __name__ == "__main__":
#    d = DatabaseFunctions('events.db')
#    print(d.executeQuery("DELETE FROM servers WHERE id=69420", "45100110866358486100089760976273759394536782658028105952776286101841047216437103925179861099255210592104878"))

