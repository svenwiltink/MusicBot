import bot
import subprocess
import os
import urllib2
from bs4 import BeautifulSoup

class CommandManager():

    commands = {}

    def addCommand(self, command):
        if command.getName() in self.commands:
            raise AttributeError("command with name " + command.getName() + " is already registered")
        self.commands[command.getName()] = command

    def getCommand(self, name):
        if name in self.commands:
            return self.commands[name]
        return None

    def getAvailableCommands(self):
        return self.commands.keys()

class CommandHandler:

    def __init__(self, commandManager):
        self.commandManager = commandManager
        whitelistFile = open(bot.whitelistFile)
        lines = whitelistFile.read().splitlines()
        self.whitelist = lines

    def handleCommand(self, bot, user, commandName, arguments):
        if user not in self.whitelist:
            return
        print "Received command " + commandName
        command = self.commandManager.getCommand(commandName)
        if command is None:
            return "Command not found"
        return command.execute(bot, user, arguments)

    def getCommandManager(self):
        return self.commandManager

    def addUserToWhitelist(self, user):
        if user not in self.whitelist:
            self.whitelist.append(user)
            self.saveWhitelist()
            return

    def removeUserFromWhitelist(self, user):
        if user in self.whitelist:
            self.whitelist.remove(user)
            self.saveWhitelist()

    def saveWhitelist(self):
        filename = bot.whitelistFile
        whitelistfile = open(filename, 'w')
        for user in self.whitelist:
            whitelistfile.write(user + "\n")
        whitelistfile.close()

    def getWhitelist(self):
        return self.whitelist

class Command(object):

    name = 'help'

    def execute(self, bot, user, params):
        return "not implemented"

    def getName(self):
        return self.name

class HelpCommand(Command):
    name = 'help'
    def execute(self, bot, user, params):
        helpText = "Available commands: "
        commands = bot.getCommandHandler().getCommandManager().getAvailableCommands()
        helpText += ", ".join(commands)
        bot.sendMessage(helpText)

class SpotifyCommand(Command):

    def executeSpotifyCommand(self, command):
        return subprocess.check_output([bot.spotifyScript, command])

    def executeSpotifyCommandWithArgs(self, args):
        return subprocess.check_output([bot.spotifyScript] + args)

class PlayCommand(SpotifyCommand):
    name = 'play'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('play');

class PauseCommand(SpotifyCommand):
    name = 'pause'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('pause');

class NextCommand(SpotifyCommand):
    name = 'next'
    def execute(self, bot, user, params):
        self.executeSpotifyCommand('next')
        return "skipping song"

class PrevCommand(SpotifyCommand):
    name = 'prev'
    def execute(self, bot, user, params):
        self.executeSpotifyCommand('prev')
        return "playing previous song"

class SearchCommand(SpotifyCommand):
    name = 'search'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommandWithArgs(['search'] + params)

class OpenUriCommand(SpotifyCommand):
    name = 'open'
    def execute(self, bot, user, params):
        if len(params) < 1 or len(params) > 1:
            return "The correct syntax is: !music open <SpotifyURI>"

        linkData      = params[0].split(':')
        spotifyWebUri = '/'.join(linkData)
        spotifyWebUri = spotifyWebUri.replace('spotify', 'https://open.spotify.com')

        if linkData[0] == 'spotify':
            soup      = BeautifulSoup(urllib2.urlopen(spotifyWebUri), "lxml")
            songTitle = soup.title.string.encode('ascii', 'ignore')
            self.executeSpotifyCommandWithArgs(['open', params[0]])
            return "Will attempt to play '" + params[0] + "' (" + songTitle + ")"
        else:
            return "Invalid Spotify url (spotify:*)"

class WhichUriCommand(SpotifyCommand):
    name = 'which'
    def execute(self, bot, user, params):
        if len(params) < 1 or len(params) > 1:
            return "The correct syntax is: !music which <SpotifyURI>"

        linkData      = params[0].split(':')
        spotifyWebUri = '/'.join(linkData)
        spotifyWebUri = spotifyWebUri.replace('spotify', 'https://open.spotify.com')

        if linkData[0] == 'spotify':
            soup      = BeautifulSoup(urllib2.urlopen(spotifyWebUri), "lxml")
            songTitle = soup.title.string.replace(' on Spotify', '')
            return songTitle.encode('ascii','ignore')
        else:
            return "Invalid Spotify url (spotify:*)"

class SvennebananCommand(SpotifyCommand):
    name = 'svendebanaan'
    def execute(self, bot, user, params):
        self.executeSpotifyCommandWithArgs(['open', "spotify:track:0YQlHiQDUDTXQ7jiItaJPx"])
        return "SVEN DE BANAAN" 

class PiemelsCommand(SpotifyCommand):
    name = 'piemels'
    def execute(self, bot, user, params):
        self.executeSpotifyCommandWithArgs(['open', "spotify:track:2cIw6pBoYvy0c8t4NgclB3"])
        return "ODE AAN DE PIEMELS!"

class CurrentCommand(SpotifyCommand):
    name = 'current'
    def execute(self, bot, user, params):
        output = self.executeSpotifyCommand('current')
        output = output.strip()
        output = output.replace('Artist  ', 'Artist: ');
        output = output.replace('Album   ', 'Album: ');
        output = output.replace('Title   ', 'Title: ');
        output = output.split('\n')
        output = ' | '.join(output);
        return output

class CurrentUriCommand(SpotifyCommand):
    name = 'currenturi'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('url')

class CurrentUrlCommand(SpotifyCommand):
    name = 'currenturl'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('url')

class CurrentMetaCommand(SpotifyCommand):
    name = 'currentmeta'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('metadata')

class VolUpCommand(Command):
    name = 'vol++'
    def execute(self, bot, user, params):
        os.system("amixer -D pulse sset Master 10%+ >/dev/null")

class VolDownCommand(Command):
    name = 'vol--'
    def execute(self, bot, user, params):
        os.system("amixer -D pulse sset Master 10%- >/dev/null")

class SetVolumeCommand(Command):
    name = 'vol'
    def execute(self, bot, user, params):
        if len(params) != 0:
            os.system("amixer -D pulse sset Master " + params[0]  + "%  >/dev/null")
            return
        return os.popen("amixer -D pulse sget Master | awk '/Front.+Playback/ {print $6==\"[off]\"?$6:$5}' | tr -d '[]' | tail -1").read()

class WhitelistCommand(Command):
    name = 'whitelist'
    def execute(self, instance, user, params):
        if user == instance.getMaster():
            handler = self._getCommandHandler(instance)
            if len(params) == 2:
                addOrRemove = params[0]
                if addOrRemove == 'add':
                    handler.addUserToWhitelist(params[1])
                    return "user added to whitelist"
                elif addOrRemove == 'remove':
                    handler.removeUserFromWhitelist(params[1])
                    return "user removed from whitelist"
            elif len(params) == 1:
                if params[0] == 'show':
                    whitelist = handler.getWhitelist()
                    return "whitelisted people: " + ", ".join(whitelist)

    def _getCommandHandler(self, botInstance):
        return botInstance.getCommandHandler()
