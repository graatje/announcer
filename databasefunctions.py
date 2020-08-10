import sqlite3
import datetime
class DatabaseFunctions:
    """
    this class has methods to interact with the database. parameter filename.
    """
    def __init__(self, file):
        self.conn=sqlite3.connect(file)
    def executeQuery(self, query):
        """
        executes a query, parameter is a query. returns cursor.fetchall()
        """
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()
        result = cur.fetchall()
        return result
    def getEvents(self):
        """
        returns events as a list. Also changes the time as a string to a datetime object.
        """
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
        """
        gives a list of info from repeating events.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT repeating_events.name, repeating_events.channel, repeating_events.time, servers.pingrole , repeating_events.minsbeforeAnnouncement, repeating_events.weekday , repeating_events.id FROM repeating_events, servers WHERE repeating_events.channel = servers.id")
        temp = list(cur.fetchall())
        rows=[]
        #converting tuple to list
        for i in temp:
            rows.append(list(i))
        for i in range(len(rows)):

            rows[i][2] = datetime.datetime.strptime(rows[i][2], '%H:%M')
        return rows
    def addRepeatingEvent(self, name, channel, time, minsbeforeAnnouncement, weekday=None):
        """
        the name explains itself.
        parameters string name, int channelid, time as a string, int minutes before announcement, int weekday (0=monday, 1=tuesday etc.)
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO repeating_events(name, channel, time, minsbeforeAnnouncement, weekday) VALUES(?,?,?,?,?)", (name,channel,time,minsbeforeAnnouncement, weekday))
        self.conn.commit()
    def deleteRepeatingEvent(self, id, ctx):
        """
        delete repeating event by id.
        parameter id, ctx
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM repeating_events, servers WHERE repeating_events.id=? AND servers.id = repeating_events.channel and servers.guild = ?", (id, ctx.guild.id))
        result = cur.fetchall()
        if len(result) == 0:
            return "no event found. do /showRepeatingEvents to get the id's of repeating events."
        else:
            cur.execute("DELETE FROM repeating_events WHERE id=?", (id,))
            self.conn.commit()
            return "event deleted."
    def addChannel(self, channelID, guildID, pingrole = "@everyone"):
        """
        adds channel to servers table. default pingrole is @everyone
        parameters int channelid, string pingrole.
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO servers(id, pingrole, guild) VALUES(?, ?, ?)", (channelID, pingrole, guildID))
        self.conn.commit()
    def removeChannel(self, ctx):
        """
        removes a channel based on channel id.
        parameter ctx
        """
        cur = self.conn.cursor()
        cur.execute("DELETE FROM servers WHERE id=?", (ctx.channel.id,))
        if cur.rowcount ==0:
            return "Channel wasn't registered at all."
        else:
            self.conn.commit()
            return "Channel removed."

    def addEvent(self, name, channel, dateEvent, minsbeforeAnnouncement=30):
        """
        looks if an event is in the database and adds it if its not.
        parameters string name, int channelid, string or datetime object dateEvent, int minutesbeforeannouncement (default 30)
        """
        if not self.isIn(name, channel, dateEvent, minsbeforeAnnouncement):
            cur = self.conn.cursor()
            cur.execute("INSERT INTO events(name, channel, dateEvent, minsbeforeAnnouncement, isAnnounced) VALUES(?,?,?,?, 0)", (name, channel, dateEvent, minsbeforeAnnouncement))
            self.conn.commit()
    def clearDueEvents(self):
        """
        clears due events from the database.

        """
        cur =self.conn.cursor()
        cur.execute("SELECT id, dateEvent FROM events")
        events = cur.fetchall()
        for i in events:
            if datetime.datetime.now(datetime.timezone.utc) >= datetime.datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S%z'):
                cur.execute("DELETE FROM events WHERE id=?", (int(i[0]),))
        self.conn.commit()
    def setAnnounced(self, name, channel, dateEvent, minsbeforeAnnounced, isAnnounced):
        """
        sets announced to 1 where it has the above attributes.
        parameters: string name, int channelid, string or datetime object dateEvent, int minutesbeforeannounced, isAnnounced
        """
        cur= self.conn.cursor()
        cur.execute("UPDATE events SET isAnnounced=1 WHERE name=? and channel=? and dateEvent=? and minsbeforeAnnouncement=? and isAnnounced=?",(name, channel, dateEvent, minsbeforeAnnounced, isAnnounced))
    def isIn(self, name, channel, dateEvent, minsbeforeAnnouncement):
        """
        checks if something already is in the database.
        parameters string name, int channelid, string or datetime object dateEvent, int minutesbeforeAnnouncement
        return: True if it aint in, False otherwise.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM events WHERE name=? and channel=? and dateEvent=? and minsbeforeAnnouncement=?", (name, channel, dateEvent, minsbeforeAnnouncement))
        if len(cur.fetchall()) != 0:
            return True
        return False
    def showEvents(self, ctx, client):
        """
        shows the events of a channel.
        parameter channelid.
        return string of events in text form.
        """
        channelID = ctx.channel.id
        guild = ctx.guild.id
        allevents = "events happening:\n"
        cur =self.conn.cursor()
        cur.execute("SELECT events.id, events.name, events.dateEvent, events.minsbeforeAnnouncement, events.channel FROM events, servers WHERE servers.guild = ? and servers.id = events.channel", (guild,))
        rows = cur.fetchall()
      
        for i in rows:
            allevents += str("id: " + str(i[0])+ ", name event: " + str(i[1]) + ", date event: " + str(i[2].replace(":00+00:00", "")) + ", amount of minutes before announcement: " + str(i[3]) + ", will be announced on channel:" + str(client.get_channel(i[4])) + "\n")

        allevents += "please note that tournaments are added daily around midnight."
        return allevents
    def showAllEvents(self, ownid):
        """
        shows the events of all channels. Only available to kevin123456#2069
        parameter ownid, the id of the person who sent the command.
        return string of events in text form.
        """
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
    def deleteEvent(self, eventid, ctx):
        """
        this deletes an event.
        parameters int eventid, int channelID
        return string.
        """
        
        if ctx.message.author.id == 300644437334425601:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM events WHERE id = ?", (eventid,))
            self.conn.commit()
            return "deleted."
        else:
            channelID =ctx.channel.id
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
    def showChannels(self, ctx, client):
        """
        shows channels as a string.
        parameters: ctx, client
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM servers WHERE guild = ?",(ctx.guild.id,))
        result = cur.fetchall()
        stringRepresentation = "the following channels are registered:"
        for i in result:
            stringRepresentation+= str(client.get_channel(i[0])) + ", "
        return stringRepresentation
    def migrate(self, ctx):
        resultmessage = ""
        cur = self.conn.cursor()
        cur.execute("SELECT channel1 FROM migrations WHERE guild=?", (ctx.guild.id,))

        result = cur.fetchall()
        if len(result) == 0:
            cur.execute("INSERT INTO migrations(channel1, guild) VALUES(?, ?)", (ctx.channel.id, ctx.guild.id))
            self.conn.commit()
            return "type /migrate in another channel to move everything from the current channel to another channel. Type /migrate in this channel to abort."
        elif len(result) == 1:
            if int(result[0][0]) == ctx.channel.id:
                return "migration aborted."
            cur.execute("UPDATE events SET channel=? WHERE channel=?", (ctx.channel.id, result[0][0]))
            resultmessage+="events have been set to channel " + str(ctx.channel) + "\n"
            cur.execute("UPDATE repeating_events SET channel=? WHERE channel=?", (ctx.channel.id, result[0][0]))
            resultmessage += "repeating events have been set to the channel " + str(ctx.channel) + "\n"
            try:
                cur.execute("UPDATE servers SET id=? WHERE id=?", (ctx.channel.id, result[0][0]))
                resultmessage += "current channel has been set to the new one."
            except:
                resultmessage += "server already added."
            cur.execute("DELETE FROM migrations WHERE channel1=?", (result[0][0],))
            resultmessage+= "migration complete."
            self.conn.commit()
        return resultmessage
            #"UPDATE events SET isAnnounced=1 WHERE name=? and channel=? and dateEvent=? and minsbeforeAnnouncement=? and isAnnounced=?
def createDB():
    """
    this creates the database.
    """
    functions = DatabaseFunctions("events.db")
    functions.executeQuery("CREATE TABLE events(id integer primary key, name text not null, channel integer not null, dateEvent datetime, minsbeforeAnnouncement integer not null, isAnnounced integer not null)")
    functions.executeQuery("CREATE TABLE servers(id integer primary key, pingrole text not null, guild integer)")
    functions.executeQuery("CREATE TABLE repeating_events(id integer primary key, name text not null, channel integer not null, time text not null, minsbeforeAnnouncement integer not null, weekday integer)")
    functions.executeQuery("CREATE TABLE migrations(channel1 integer primary key, guild integer unique)")
#create a database when importing if it doesn't exist yet.
try:
    open('events.db')
except FileNotFoundError:
    createDB()

if __name__ == "__main__":
    d = DatabaseFunctions('events.db')
    print(d.executeQuery("SELECT count(guild) FROM servers")[0][0])

