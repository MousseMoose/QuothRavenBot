import discord
import asyncio
import json
import datetime
from QuothRavenDatabaseWrapper import QuothRavenDatabaseClient


class QuothRavenDiscordClient(discord.Client):
    commands = {}
    dbc = None

    def role_in_guild(self,role,guild):
        in_guild = False
        for g_role in guild.roles:
            if role.lower() == g_role.name.lower():
                in_guild = True
                break
        return in_guild

    def command_alert(self,com,msg,dmsg):
        alertroles = self.dbc.get_alertroles(dmsg.guild.id)
        retStr = ""
        print(alertroles.resultSet)
        if(alertroles.queryStatus):
            for role in alertroles.resultSet:
                drole = dmsg.guild.get_role(role[1])
                if drole is not None:
                    retStr += drole.mention + " "
                else:
                    print("role",role[1],"no longer exists on guild",role[0],"so it will be deleted")
                    self.dbc.remove_alertrole(role[0],role[1])
            retStr += "Alert! " + msg
        return retStr

    def command_check_in(self,com,msg,dmsg):
        return "Check in! " + msg

    def command_add_alertrole(self,com, msg, dmsg):
        retStr = ""
        if int(msg) in [role.id for role in dmsg.guild.roles]:
            result = self.dbc.add_alertrole(dmsg.guild.id, msg)
            if result.queryStatus:
                retStr = "Successfully added role to alerts: " + dmsg.guild.get_role(int(msg)).name + " (" + msg + ")"
            else:
                retStr = "Couldn't add role. Make sure it's spelled correctly is correct."
        print ("returning retstr " + retStr)
        return retStr

    def command_remove_alertrole(self,com,msg,dmsg):
        return "Check in! " + msg

    def command_not_found(self,com,msg,dmsg):
        print("Command not found!")
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

    def dispatch_command(self, com, msg,dmsg):
        print("dispatching command ", com)
        com = com.lower()
        return self.commands.get(com, self.command_not_found)(com, msg,dmsg)

    async def on_ready(self):
        print('Connected!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_message(self, message):
        splt = self.handle_input(message.content)
        if message.content.startswith("!"):
            msg = self.dispatch_command(splt[0],splt[1],message)
            if len(msg)>0:
                await message.channel.send(msg)

    def __init__(self):
        self.dbc = QuothRavenDatabaseClient()
        self.commands = {
            '!checkin': self.command_check_in,
            '!addalertrole': self.command_add_alertrole,
            '!alert': self.command_alert,

        }
        super().__init__()
