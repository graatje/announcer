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

tourneyDict={0:"little cup", 1:"self caught", 2:"anything goes", 3:"set level 100", 4:"monotype", 5:"clan wars", 6:"clan wars"}
def readToken():
    tokenfile = open('token.txt')
    token=tokenfile.read()
    return token
class AnnouncementObject:
    def __init__(self, name="", dt=datetime.datetime.now(tz=datetime.timezone.utc), announced=False, timedelta = 30, channel=0, pingrole="@everyone"):
        self.name = name
        
        self.dt = dt

        self.announced = announced
        self.channel=channel

        self.announcementtime=self.dt + datetime.timedelta(minutes=-int(timedelta))
        self.pingrole =pingrole
        self.timedelta=timedelta
   
        
class Announcer:
    def __init__(self):
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
        some_number = 0
        while True:
            #getting soonest event
            earliesttime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=400)
            for i in self.events:
                if i.announcementtime <=earliesttime and datetime.datetime.now(datetime.timezone.utc) <= i.announcementtime and not i.announced:
                    earliesttime = i.announcementtime
            #setting interval

            
            if datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15) >= earliesttime:
                interval = 60
            else:
                interval=600
            
            #looking if an event can be announced.
            for i in self.events:
                if datetime.datetime.now(tz=datetime.timezone.utc) >= i.announcementtime and datetime.datetime.now(tz=datetime.timezone.utc) <= i.dt and not i.announced:
                    i.announced = True
                    #calculating the actual time difference
                    timedifference = str(int(math.ceil((i.dt-datetime.datetime.now(tz=datetime.timezone.utc)).seconds / 60)))
                    #creating channel object to send the message.
                    self.channel=self.client.get_channel(int(i.channel))
                    await self.channel.send(str(i.pingrole) + " " + str(i.name) + " starting in " + timedifference +  " minutes")
                    print("sended message" + str(i.pingrole) + " " + str(i.name) + " starting in " + timedifference +  " minutes")
                    #setting the event to announced in the database as well.
                    self.db.setAnnounced(i.name, i.channel, i.dt, i.timedelta, 0)

            self.db.clearDueEvents()
            self.fetchEvents     
            #looking if daily events must be created.
            if datetime.datetime.now(tz=datetime.timezone.utc).day != self.thisday:
                time.sleep(5)
                self.createDaily()
                self.thisday =datetime.datetime.now(tz=datetime.timezone.utc).day
                self.db.clearDueEvents()
                self.fetchEvents()
            time.sleep(interval)
    def createDaily(self):
        events = self.db.getRepeatingEvents()
        weekday = datetime.datetime.now(tz=datetime.timezone.utc).weekday()
        for i in events:

            if weekday == i[5] or i[5] == None:
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                #name, channel, dateEvent, minsbeforeAnnouncement=3
                 #repeating_events.name, repeating_events.channel, repeating_events.time, servers.pingrole , repeating_events.minsbeforeAnnouncement, repeating_events.weekday
               # name, channel, dateEvent, minsbeforeAnnouncement=30
                self.db.addEvent(i[0], i[1], datetime.datetime(now.year, now.month, now.day, i[2].hour,i[2].minute, tzinfo=datetime.timezone.utc), i[4])

    def fetchEvents(self):
        self.events = []
       
        events = self.db.getEvents()
        for i in events:
            #name="", dt=datetime.datetime.now(), announced=False, timedelta = 30, channel=0, pingrole="@everyone"
            #events.name, events.channel, events.dateEvent, servers.pingrole , events.minsbeforeAnnouncement, events.isAnnounced

            self.events.append(AnnouncementObject(i[0], i[2], i[5], i[4], i[1], i[3].replace("\n", "")))

    def addAnnouncement(self, announcementObject):
        self.events.append(announcementObject)
    def startBot(self):
        token=readToken()
        self.client.loop.create_task(self.checkForEvents())
        self.client.run(token)
def startCommandTaker():
    os.system("python commandtaker.py")

if __name__ == "__main__":
   t = threading.Thread(target=startCommandTaker)
   t.start()
   d = Announcer()
   d.startBot()
