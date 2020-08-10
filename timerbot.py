import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import datetime
import threading
import time
import os
import math
import databasefunctions

def readToken():
    """
    used to read the token since I don't want anyone to read the token on the github.
    """
    tokenfile = open('token.txt')
    token = tokenfile.read()
    return token


class AnnouncementObject:
    def __init__(self, name="", dt=datetime.datetime.now(tz=datetime.timezone.utc), announced=False, timedelta = 30, channel=0, pingrole="@everyone"):
        """
        parameters:name="", dt=datetime.datetime.now(tz=datetime.timezone.utc), announced=False, timedelta = 30, channel=0, pingrole="@everyone"
        attributes:
        name
        dt (datetime of the event),
        announced (boolean if the event has been announced already.
        channel (the id of the channel the message should be send to.)
        pingrole (the role that should be pinged)
        timedelta (amount of minutes before the event happens that should be announced.)
        """
        self.name = name
        self.dt = dt
        self.announced = announced
        self.channel=channel
        self.announcementtime=self.dt + datetime.timedelta(minutes=-int(timedelta))
        self.pingrole =pingrole
        self.timedelta=timedelta
    def __str__(self):
        return "name: " + str(self.name) + ", time event: " + str(self.dt) + ", channel: " + str(self.channel) + ", announcementtime: " + str(self.announcementtime) + ", pingrole: " + str(self.pingrole) + ", timedelta: "+ str(self.timedelta)
    
class Announcer:
    """
    this class announces things at a certain time in discord.
    """
    def __init__(self):
        """
        attributes:
        db, databasefunctions.DatabaseFunctions object.
        events, list of AnnounceObjects
        thisday, int date day.
        client, discord.Client()
        """
        self.db = databasefunctions.DatabaseFunctions("events.db")
        dt= datetime.datetime.now(tz=datetime.timezone.utc)
        self.events = []
        self.thisday=datetime.datetime.now(tz=datetime.timezone.utc).day
        self.createDaily()
        self.fetchEvents()
        self.client = discord.Client()
        #self.taker = CommandTaker()
        #self.taker.runBot()
    async def checkForEvents(self):
        await self.client.wait_until_ready()
        while True:
            """
            this gets the time of the soonest event, if the soonest event is more than 15 minutes away it checks if it must announce events every 10 minutes. 
            else it checks every minute. this is due to saving RAM and energy.
            """
            earliesttime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=400)
            for i in self.events:
                if i.announcementtime <=earliesttime and datetime.datetime.now(datetime.timezone.utc) <= i.announcementtime and not i.announced:
                    earliesttime = i.announcementtime
            #setting interval


            if datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15) >= earliesttime:
                interval = 60
            else:
                interval=600
            
            """
            this checks if an event can be announced and it announces the event if it can be announced.
            If an event can be announced it sets an event announced in both the database and in the list of announcementobjects.
            also prints the message to the screen for debugging purposes.
            """
            for i in self.events:
                if datetime.datetime.now(tz=datetime.timezone.utc) >= i.announcementtime and datetime.datetime.now(tz=datetime.timezone.utc) <= i.dt and not i.announced:
                    i.announced = True
                    #calculating the actual time difference instead of the supposed time difference.
                    timedifference = str(int(math.ceil((i.dt-datetime.datetime.now(tz=datetime.timezone.utc)).seconds / 60)))
                    #creating channel object to send the message.
                    self.channel=self.client.get_channel(int(i.channel))
                    await self.channel.send(str(i.pingrole) + " " + str(i.name) + " starting in " + timedifference +  " minutes")
                    print("sended message" + str(i.pingrole) + " " + str(i.name) + " starting in " + timedifference +  " minutes")
                    #setting the event to announced in the database as well.
                    self.db.setAnnounced(i.name, i.channel, i.dt, i.timedelta, 0)
            """
            clearing due events and catching new events
            """
            self.db.clearDueEvents()
            self.fetchEvents()
            """
            creating daily events if a new day has arrived. Also fetching events and clearing due events.
            """
            if datetime.datetime.now(tz=datetime.timezone.utc).day != self.thisday:
                time.sleep(5)
                self.createDaily()
                self.thisday =datetime.datetime.now(tz=datetime.timezone.utc).day
                self.db.clearDueEvents()
                self.fetchEvents()
                """
                now it sleeps for the interval time.
                """
            time.sleep(interval)
    def createDaily(self):
        """
        this adds repeating events to the database. Compares if the current weekday is the same as the weekday on which an event should be announced.
        if te weekday is None it will be added every day.
        """
        events = self.db.getRepeatingEvents()
        weekday = datetime.datetime.now(tz=datetime.timezone.utc).weekday()
        for i in events:
            if weekday == i[5] or i[5] == None:
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                self.db.addEvent(i[0], i[1], datetime.datetime(now.year, now.month, now.day, i[2].hour,i[2].minute, tzinfo=datetime.timezone.utc), i[4])

    def fetchEvents(self):
        """
        adds events from the database to the list of announcementobjects.
        starts from an empty list.
        """
        self.events = []

        events = self.db.getEvents()
        for i in events:
            
            self.events.append(AnnouncementObject(i[0], i[2], i[5], i[4], i[1], i[3].replace("\n", "")))

    def startBot(self):
        """
        reads token and runs bot, also starts task checkForEvents.
        """
        token=readToken()
        self.client.loop.create_task(self.checkForEvents())
        self.client.run(token)
def startCommandTaker():
    """
    cause it doesn't let us run 2 bots in the same program commandtaker gets called from a thread. The thread contains this function.
    """
    os.system("python commandtaker.py")

if __name__ == "__main__":
   t = threading.Thread(target=startCommandTaker)
   t.start()
   d = Announcer()
   d.startBot()
