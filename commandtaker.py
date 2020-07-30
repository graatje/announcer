import discord
from discord.ext.commands import Bot
import asyncio
from discord.ext import commands
import datetime
import threading
import re
import time
import os
import databasefunctions
# I don't want everyone to know the token so it will be read from a text file that wont be pushed to the git repo.
def readToken():
    """
    reads the content of token.txt and returns that content.
    """
    tokenfile = open('token.txt')
    token=tokenfile.read()
    return token
client = commands.Bot(command_prefix="/")
client.remove_command('help')
@client.event
async def on_ready():
    print("commandtaker ready")

@client.command()
async def help(ctx):
    """
    sends a help message.
    @todo: read help message from a text file. this aint very clear at the moment.
    """
    await ctx.send("addEvent: this adds a event and announces it once at said datetime. \naddEvent: arguments: date(month-day), time(hh:mm), minutes before announcement(default = 30), name\nexample:/addEvent 10-20 8:42 30 world boss\n\naddRepeatingEvent: this adds a event and repeats it on said day. type none instead of weekday to repeat it every day. addRepeatingEvent: arguments:time, minutes before announcement, weekday(example:friday), name of the event\nexample: /addRepeatingEvent 12:00 30 friday set level 100 tournament\n\naddchannel: this adds the channel where this command has been typed to channels. after this events can be added and announced.\naddchannel: argument: the role to ping.(example:@somerole)\n example: /addchannel @somerole")
@client.command()
async def Time(ctx):
    """
    sends current utc time to the user.
    """
    await ctx.send(str(datetime.datetime.now(datetime.timezone.utc))[:16])
@client.command()
async def addEvent(ctx, date, time, announceminsbefore=30, *thename):
    """
    adds event.
    parameters date, time, minutes before announcement, the name.
    """
    name=""
    for i in thename:
        name += str(i) + " "
    #name, channel, dateEvent, minsbeforeAnnouncement=30):
    #%Y-%m-%d %H:%M:%S
    
    temptime=datetime.datetime.strptime(str(date + " " + time) , '%m-%d %H:%M')
    
    now=datetime.datetime.now(tz=datetime.timezone.utc)

    realtime = datetime.datetime(year=now.year, month=temptime.month, day=temptime.day, hour=temptime.hour, minute=temptime.minute, second=00, tzinfo=datetime.timezone.utc)

    databasefunctions.DatabaseFunctions("events.db").addEvent(name, ctx.channel.id, realtime, announceminsbefore)
  
    print(announceminsbefore)
    await ctx.send("event added and will be announced on " + str(realtime -datetime.timedelta(minutes=announceminsbefore)))
    #except:
     #   await ctx.send("make sure the datetime is in the form 'month-day hour:minute'")

@client.command()
#self, name, channel, time, minsbeforeAnnouncement, weekday
async def addRepeatingEvent(ctx, thetime, minsbeforeAnnouncement, weekday=None, *thename):
    """
    adds a repeating event.
    parameters:time, minutes before announcement, weekday as string, the name.
    """
    name = ""
    if weekday == "none":
        weekday = None
    for i in thename:
        name +=" " +str(i)
    daystuff = {"monday":0, "tuesday":1, "wednesday":2, "thursday":3, "friday":4, "saturday":5, "sunday":6, None:None}
    if ":" not in thetime:
        await ctx.send("must have the form 'hh:mm'")
    else:
        thetime = thetime.replace("\n", "")
        timelist = thetime.split(':')
        passed=True
        try:
            print(daystuff[weekday])
        except:
            await ctx.send(str(weekday) + " is not a known day.")
            passed = False
        if passed:
            databasefunctions.DatabaseFunctions("events.db").addRepeatingEvent(name, ctx.channel.id, thetime, minsbeforeAnnouncement, daystuff[weekday])

            something=datetime.datetime(year=2000, month=5, day=5, hour=int(timelist[0]), minute=int(timelist[1]))
            somet = something - datetime.timedelta(minutes=int(minsbeforeAnnouncement))
            await ctx.send("repeating event added and will be announced on " + str(somet.hour) + ":" + str(somet.minute) +" every " + str(weekday))
@client.command()
async def addChannel(ctx, role):
    """
    adds a channel.
    parameter: role.
    """
    try:
        role = role.replace("\n", "")
        databasefunctions.DatabaseFunctions("events.db").addChannel(ctx.channel.id, role)
        await ctx.send(str(ctx.channel) + "added to channels.")
    except:
        await ctx.send("failed to add channel. possible cause: channel is already added.")
@client.command()
async def showEvents(ctx):
    """
    shows all events happening on the channel where this command is used.
    """
    await ctx.send(str(databasefunctions.DatabaseFunctions("events.db").showEvents(ctx.channel.id)))

@client.command()
async def showAllEvents(ctx):
    """
    shows all events for debugging purposes to kevin123456#2069 only.
    """
    await ctx.send(str(databasefunctions.DatabaseFunctions("events.db").showAllEvents(ctx.message.author.id)))

@client.command()
async def deleteEvent(ctx, eventid):
    """
    deletes an event. parameter event id.
    """
    try:
        eventid = int(eventid)
    except:
        await ctx.send("eventid should be a number. see /showEvents to view the id's of events.")
    await ctx.send(str(databasefunctions.DatabaseFunctions("events.db").deleteEvent(eventid, ctx.channel.id)))

if __name__ == "__main__":
    token = readToken()
    client.run(token)

