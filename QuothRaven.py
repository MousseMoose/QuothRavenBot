import discord
import asyncio
import json
import sqlite3
import datetime


class QuothRavenDiscordClient(discord.Client):
    commands = {}
    alertRoles = []
    def command_alert(self,com,msg):
        retStr = ""
        for role in self.alertRoles:
            retStr += ("@" + role + " ")
        retStr += "Alert!" + msg
        return retStr

    def command_check_in(self,com,msg):
        return "Check in! " + msg

    def command_not_found(self,com,msg):
        return ""

    def handle_input(self,msg):
        strIn = msg
        splt = strIn.split(" ")
        com = ""
        argStr = ""
        if strIn.startswith("!"):
            argStr = " ".join(splt[1:])
            com = splt[0]

        return [com,argStr]

    def dispatch_command(self, com, msg):
        print("dispatching command ", com)
        com = com.lower()
        return self.commands.get(com, self.command_not_found)(com, msg)

    async def on_ready(self):
        print('Connected!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_message(self, message):
        splt = self.handle_input(message.content)
        msg = self.dispatch_command(splt[0],splt[1])
        if len(msg)>0:
            await message.channel.send(msg)

    async def on_message_edit(self, before, after):
        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        await before.channel.send(fmt.format(before, after))

    def __init__(self, alertRoles = ["Here"]):
        self.commands = {
            '!checkin': self.command_check_in,
            '!alert': self.command_alert,
        }
        self.alertRoles = alertRoles
        super().__init__()
