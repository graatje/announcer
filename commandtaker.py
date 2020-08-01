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
def getHelp():
    file = open("help.txt")
    return file.read()

client = commands.Bot(command_prefix="/")
client.remove_command('help')
#help(client)
@client.event
async def on_ready():
    print("commandtaker ready")

##@client.command()
##async def help(ctx):
##    """
##    sends a help message.
##    """
##    await ctx.send(getHelp())

def allowedToAdd(ctx):
    query = "SELECT count(guild) FROM servers WHERE guild = "
    query += str(ctx.guild.id)
    d = databasefunctions.DatabaseFunctions('events.db')
    result = d.executeQuery(query)[0][0]
    if result ==1:
        query= "SELECT count(guild) FROM servers WHERE guild = " + str(ctx.guild.id) + " AND id = " + str(ctx.channel.id)
        result = d.executeQuery(query)[0][0]
        if result == 0:
            query = "SELECT id FROM servers WHERE guild = "
            query += str(ctx.guild.id)
            result = int(d.executeQuery(query)[0][0])
            
            return "the event will be announced on "+ str(client.get_channel(result)) + ". (do /addServer to register this channel too.)", True
        else:
            return "event added and will be announced on this channel.", True
    elif result== 0:
        return "register a channel to announce things on this server.", False
    elif result >= 2:
        return "you can only register events on a registered channel (do /addServer)", False
    else:
        return "what the fuck did you do", False
@client.command()
async def Time(ctx):
    """
    sends current utc time to the user.
    """
    await ctx.send(str(datetime.datetime.now(datetime.timezone.utc))[:16])
@client.command()
async def addEventFromNow(ctx, time, announceminsbefore, *thename):
    """
    adds event from now +the given time.
    parameters time, minutes before announcement, the name.
    """
    allowed = allowedToAdd(ctx)
    if allowed[1]:
        #since every space in the name is looked at like a new argument the name is stored as a list and will be assembled and made as a string.
        name=""
        for i in thename:
            name += str(i) + " "
        #converting hh:mm to minutes.
        toMinutes = int(time.split(":")[0])*60 + int(time.split(":")[1])
        #making the datetime of the event.
        timeEvent = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=toMinutes)
        timeEvent=datetime.datetime(year=timeEvent.year, month=timeEvent.month, day=timeEvent.day, hour=timeEvent.hour, minute=timeEvent.minute, second=timeEvent.second, tzinfo=datetime.timezone.utc)

        try:#try writing to the database..
            databasefunctions.DatabaseFunctions("events.db").addEvent(name, ctx.channel.id, timeEvent, int(announceminsbefore))
            await ctx.send("event added and will be announced on " + str(timeEvent - datetime.timedelta(minutes=int(announceminsbefore))))
        except:
            print("time:" + str(time) + "minsbeforeevent:" + str(announceminsbefore) + " name: " + str(thename))
            await ctx.send("Failed. Please check /help to view what arguments must be used for this command.")
    else:
        await ctx.send(allowed[0])
@client.command()
async def addEvent(ctx, date, time, announceminsbefore=30, *thename):
    """
    adds event.
    parameters date, time, minutes before announcement, the name.
    """
    #since every space in the name is looked at like a new argument the name is stored as a list and will be assembled and made as a string.
    allowed = allowedToAdd(ctx)
    if allowed[1]:
        
        name=""
        for i in thename:
            name += str(i) + " "

        #converting string to datetime.datetime object.
        temptime=datetime.datetime.strptime(str(date + " " + time) , '%m-%d %H:%M')
        now=datetime.datetime.now(tz=datetime.timezone.utc)

        #converting to the actual time containing the year as well.
        realtime = datetime.datetime(year=now.year, month=temptime.month, day=temptime.day, hour=temptime.hour, minute=temptime.minute, second=00, tzinfo=datetime.timezone.utc)

        try:
            databasefunctions.DatabaseFunctions("events.db").addEvent(name, ctx.channel.id, realtime, announceminsbefore)
            await ctx.send(allowed[0])
            await ctx.send("will be announced on " + str(realtime -datetime.timedelta(minutes=announceminsbefore)))
            
        except:
            print("date: " + str(date) + " time:" + str(time) + "minsbeforeevent:" + str(announceminsbefore) + " name: " + str(thename))
            await ctx.send("Failed. Please check /help to view what arguments must be used for this command.")
    else:
        await ctx.send(allowed[0])
@client.command()
#self, name, channel, time, minsbeforeAnnouncement, weekday
async def addRepeatingEvent(ctx, thetime, minsbeforeAnnouncement, weekday=None, *thename):
    """
    adds a repeating event.
    parameters:time, minutes before announcement, weekday as string, the name.
    """
    name = ""
    #converting none as string to None.
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
        else:
            await ctx.send("Invalid day. possible days: monday, tuesday, wednesday, thursday, friday, saturday, sunday, none (note this must be the text none)")
@client.command()
async def addChannel(ctx, role):
    """
    adds a channel.
    parameter: role.
    """
    role = role.replace("\n", "")
    databasefunctions.DatabaseFunctions("events.db").addChannel(ctx.channel.id, ctx.guild.id, role)
    await ctx.send(str(ctx.channel) + " added to channels.")
    
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

