import discord
import asyncio
import json
import datetime
from QuothRavenDatabaseWrapper import QuothRavenDatabaseClient


class QuothRavenDiscordClient(discord.Client):
    commands = {}
    dbc = None

    async def role_in_guild(self,role,guild):
        in_guild = False
        for g_role in guild.roles:
            if role.lower() == g_role.name.lower():
                in_guild = True
                break
        return in_guild

    async def command_alert(self,com,msg,dmsg):
        alertroles = self.dbc.get_alertroles(dmsg.guild.id)
        retstr = ""
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

    async def command_add_alertrole(self,com, msg, dmsg):
        retstr = ""
        if int(msg) in [role.id for role in dmsg.guild.roles]:
            result = self.dbc.add_alertrole(dmsg.guild.id, msg)
            if result.queryStatus:
                retstr = "Successfully added role to alerts: " + dmsg.guild.get_role(int(msg)).name + " (" + msg + ")"
            else:
                retstr = "Oh Gosh, this is embarrassing. Something went wrong when adding this alert role."
        return retstr

    async def command_remove_alertrole(self,com,msg,dmsg):
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

    async def command_add_check_in(self,com,msg,dmsg):
        retstr = ""
        date = datetime.datetime.now().isoformat()
        rs = self.dbc.add_checkin(dmsg.guild.id,dmsg.author.id,date,msg)
        if rs.queryStatus:
            await self.update_statuschannel(dmsg)
            retstr = "Check in saved."
        else:
            retstr = "Whoopsie Daisy! It appears I could not add this check-in."
        return retstr

    async def command_summary(self,com,msg,dmsg):
        retstr = ""
        rs = self.dbc.get_last_checkins(dmsg.guild.id)
        if rs.queryStatus:
            if len(rs.resultSet) > 0:
                retstr = "Here's the latest: \n"
                retstr += "```diff\n"
                for ci in rs.resultSet:
                    name = dmsg.guild.get_member(ci[1]).nick
                    if name is None:
                        name = dmsg.guild.get_member(ci[1]).name
                    retstr  += "+ " + ci[0][:-10] + " | " + name + " | " + ci[2] + "\n"
                retstr += "```"
            else:
                retstr = "Would you look at that: There are no check-ins on file."
        else:
            retstr = "Ol' Data B. wouldn't give me the info. I'm afraid we'll have to do this another time."

        return retstr

    async def setup_statuschannel(self,channel,dmsg):
        dchannel = dmsg.guild.get_channel(channel)
        self.statuschannels.setdefault(dmsg.guild.id, []).append(channel)
        summary = await self.command_summary("", "", dmsg)
        try:
            await dchannel.send(summary)
            return True
        except discord.Forbidden as e:
            return False
        return False

    async def command_add_statuschannel(self,com,msg,dmsg):
        retstr = ""
        channel = int(msg)
        dchannel = dmsg.guild.get_channel(channel)
        if dchannel is not None:
            rs = self.dbc.add_statuschannel(dmsg.guild.id,channel)
            if rs.queryStatus:
                if await self.setup_statuschannel(channel,dmsg):
                    retstr = "Splendid! You'll find what you need in channel " + dmsg.guild.get_channel(channel).name
                else:
                    retstr = "Well, this is awkward: It couldn't post my notice in that channel."
            else:
                retstr = "Apologies. I couldn't register the channel " + dmsg.guild.get_channel(channel).name
        else:
            retstr = "Curious. It appears the channel does not exist. At least I cannot see it."
        return retstr

    async def command_remove_statuschannel(self,com,msg,dmsg):
        retstr = ""
        channel = int(msg)
        dchannel = dmsg.guild.get_channel(channel)
        if dchannel is not None:
            if(self.remove_statuschannel(dmsg.guild,dchannel)):
                retstr = "I shall not update the channel " + dchannel.name + " any longer."
        else:
            retstr = "I cannot find this channel."

        return retstr

    def remove_statuschannel(self,dguild,dchannel):
        rs = self.dbc.remove_statuschannel(dguild.id,dchannel.id)
        if(rs.queryStatus):
            try:
                self.statuschannels.setdefault(dguild.id,[]).remove(dchannel.id)
                # todo: Maybe delete last message
                return True
            except ValueError as e:
                # todo: Determine how much of a problem this case would be
                return True
        else:
            return False

    async def update_statuschannel(self,dmsg):
        channels = self.statuschannels.setdefault(dmsg.guild.id,[])
        for channel in channels:
            dchannel = dmsg.guild.get_channel(channel)
            dmsg_last = await dchannel.fetch_message(dchannel.last_message_id)
            summary = await self.command_summary("!summary","",dmsg)
            if dmsg_last is not None:
                if dmsg_last.author.id == self.user.id:
                    await dmsg_last.edit(content=summary)
                else:
                    await dchannel.send(summary)
            else:
                await dchannel.send(summary)
        return

    async def command_last(self,com,msg,dmsg):
        # todo: refactor and generalise to "get last x check-ins" function
        retstr = ""
        rs = self.dbc.get_last_checkin(dmsg.guild.id)
        if rs.queryStatus:
            if len(rs.resultSet) > 0:
                dt1 = datetime.datetime.now()
                dt2 = datetime.datetime.fromisoformat(rs.resultSet[0][0])
                tdiff = dt1-dt2
                retstr+= "The last check-in was posted " + str(round(tdiff.seconds/3600,1)) + " hours ago. \n"
                rs.resultSet = rs.resultSet[:1]
                retstr += "```diff\n"
                for ci in rs.resultSet:
                    name = dmsg.guild.get_member(ci[1]).nick
                    if name is None:
                        name = dmsg.guild.get_member(ci[1]).name
                    retstr += "+ " + ci[0][:-10] + " | " + name + " | " + ci[2] + "\n"
                retstr += "```"
            else:
                retstr = "Would you look at that: There are no check-ins on file."
        else:
            retstr = "Ol' Data B. wouldn't give me the info. I'm afraid we'll have to do this another time."
        return retstr

    async def command_not_found(self,com,msg,dmsg):
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

    async def dispatch_command(self, com, msg,dmsg):
        print("dispatching command ", com)
        com = com.lower()
        function = self.commands.get(com, self.command_not_found)
        result = await function(com, msg,dmsg)
        return result

    async def on_ready(self):
        print('Connected!')
        print('Username: {0.name}\nID: {0.id}'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith("!") and isinstance(message.channel,discord.TextChannel):
            splt = self.handle_input(message.content)
            msg = await self.dispatch_command(splt[0],splt[1],message)
            if len(msg)>0:
                await message.channel.send(msg)

    def __init__(self):
        self.dbc = QuothRavenDatabaseClient()
        rs = self.dbc.get_statuschannels()
        self.statuschannels = {}
        if rs.queryStatus:
            for pair in rs.resultSet:
                self.statuschannels.setdefault(pair[0],[]).append(pair[1])
        else:
            print("Could not load status channels")
        self.commands = {
            '!checkin': self.command_add_check_in,
            '!addalertrole': self.command_add_alertrole,
            '!alert': self.command_alert,
            '!summary': self.command_summary,
            '!addstatuschannel': self.command_add_statuschannel,
            '!removestatuschannel': self.command_remove_statuschannel,
            '!last': self.command_last,
        }
        super().__init__()
