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
        retstr = ""
        print(alertroles.resultSet)
        if(alertroles.queryStatus):
            for role in alertroles.resultSet:
                drole = dmsg.guild.get_role(role[1])
                if drole is not None:
                    retstr += drole.mention + " "
                else:
                    print("role",role[1],"no longer exists on guild",role[0],"so it will be deleted")
                    self.dbc.remove_alertrole(role[0],role[1])
            retstr += "\n```diff\n"
            retstr += "-Alert! " + msg + "\n"
            retstr += "```"
        date = datetime.datetime.now().isoformat()
        self.dbc.add_alert(dmsg.guild.id,dmsg.author.id,date,msg)
        return retstr

    def command_add_alertrole(self,com, msg, dmsg):
        retstr = ""
        if int(msg) in [role.id for role in dmsg.guild.roles]:
            result = self.dbc.add_alertrole(dmsg.guild.id, msg)
            if result.queryStatus:
                retstr = "Successfully added role to alerts: " + dmsg.guild.get_role(int(msg)).name + " (" + msg + ")"
            else:
                retstr = "Oh Gosh, this is embarrassing. Something went wrong when adding this alert role."
        return retstr

    def command_remove_alertrole(self,com,msg,dmsg):
        retstr = ""
        roleid = int(msg)
        rs = self.dbc.remove_alertrole(dmsg.guild.id,roleid)
        drole = dmsg.guild.get_role(roleid)
        if rs.queryStatus:
            rolename = " "
            if drole is not None:
                rolename = " " + drole.name + " "
            retstr = "Removed alert role" + rolename + "with id " + roleid
        else:
            retstr = "I'm awfully sorry, but this one went belly-up. I couldn't delete that role."
        return retstr

    def command_add_check_in(self,com,msg,dmsg):
        retstr = ""
        date = datetime.datetime.now().isoformat()
        rs = self.dbc.add_checkin(dmsg.guild.id,dmsg.author.id,date,msg)
        if rs.queryStatus:
            retstr = "Check in saved."
        else:
            retstr = "Whoopsie Daisy! It appears I could not add this check-in."
        return retstr

    def command_summary(self,com,msg,dmsg):
        retstr = ""
        rs = self.dbc.get_last_checkins(dmsg.guild.id)
        if rs.queryStatus:
            if len(rs.resultSet) > 0:
                retstr = "Here's the latest: \n"
                retstr += "```diff\n"
                for ci in rs.resultSet:
                    retstr  += "+ " + ci[0][:-10] + " " + dmsg.guild.get_member(ci[1]).nick + " " + ci[2] + "\n"
                retstr += "```"
            else:
                retstr = "Would you look at that: There are no check-ins on file."
        else:
            retstr = "Ol' Data B. wouldn't give me the info. I'm afraid we'll have to do this another time."

        return retstr

    def command_last_check_in(self,com,msg,dmsg):
        retstr = ""
        return retstr

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

        if message.content.startswith("!") and isinstance(message.channel,discord.TextChannel):
            splt = self.handle_input(message.content)
            msg = self.dispatch_command(splt[0],splt[1],message)
            if len(msg)>0:
                await message.channel.send(msg)

    def __init__(self):
        self.dbc = QuothRavenDatabaseClient()
        self.commands = {
            '!checkin': self.command_add_check_in,
            '!addalertrole': self.command_add_alertrole,
            '!alert': self.command_alert,
            '!summary': self.command_summary,

        }
        super().__init__()
