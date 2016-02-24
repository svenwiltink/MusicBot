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

class MusicCommand(Command):

    def stopYoutubePlayback(self):
        subprocess.Popen(['killall', 'mpv'])
        subprocess.Popen(['killall', 'mpsyt'])

    def stopSpotifyPlayback(self):
        self.executeSpotifyCommand('pause');

    def playSpecificSpotifySong(self, arg):
        self.stopYoutubePlayback()
        self.executeSpotifyCommandWithArgs(['open', arg])
        os.system("amixer -D pulse sset Master 100% >/dev/null")

    def executeSpotifyCommand(self, command):
        return subprocess.check_output([bot.spotifyScript, command])

    def executeSpotifyCommandWithArgs(self, args):
        return subprocess.check_output([bot.spotifyScript] + args)

    def executeYoutubeCommand(self, args):
        return subprocess.check_output([bot.youtubeScript] + args)

class PlayCommand(MusicCommand):
    name = 'play'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('play');

class PauseCommand(MusicCommand):
    name = 'pause'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('pause');

class NextCommand(MusicCommand):
    name = 'next'
    def execute(self, bot, user, params):
        self.executeSpotifyCommand('next')
        return "skipping song"

class PrevCommand(MusicCommand):
    name = 'prev'
    def execute(self, bot, user, params):
        self.executeSpotifyCommand('prev')
        return "playing previous song"

class SearchCommand(MusicCommand):
    name = 'search'
    def execute(self, bot, user, params):
        result = self.executeSpotifyCommandWithArgs(['search'] + params)
        linkData = result.split(':')
        spotifyWebUri = '/'.join(linkData)
        spotifyWebUri = spotifyWebUri.replace('spotify', 'https://open.spotify.com', 1)

        if linkData[0] == 'spotify':
            self.stopYoutubePlayback()
            print spotifyWebUri
            soup = BeautifulSoup(urllib2.urlopen(spotifyWebUri), "lxml")
            songTitle = soup.title.string.encode('ascii','ignore')
            songtitle = songTitle.replace('on Spotify', '')
            return "Best result: '" + songTitle + "'"
        else:
            return "No search results"

class OpenUriCommand(MusicCommand):
    name = 'open'
    def execute(self, bot, user, params):
        if len(params) < 1 or len(params) > 1:
            return "The correct syntax is: !music open <SpotifyURI>"

        linkData = params[0].split(':')
        spotifyWebUri = '/'.join(linkData)
        spotifyWebUri = spotifyWebUri.replace('spotify', 'https://open.spotify.com', 1)

        if linkData[0] == 'spotify':
            print spotifyWebUri
            soup = BeautifulSoup(urllib2.urlopen(spotifyWebUri), "lxml")
            songTitle = soup.title.string.encode('ascii','ignore')
            songtitle = songTitle.replace('on Spotify', '')
            self.executeSpotifyCommandWithArgs(['open', params[0]])
            self.stopYoutubePlayback()
            return "Will attempt to play '" + params[0] + "' (" + songTitle + ")"
        else:
            return "Invalid Spotify url (spotify:*)"

class WhichUriCommand(MusicCommand):
    name = 'which'
    def execute(self, bot, user, params):
        if len(params) < 1 or len(params) > 1:
            return "The correct syntax is: !music which <SpotifyURI>"

        linkData = params[0].split(':')
        spotifyWebUri = '/'.join(linkData)
        spotifyWebUri = spotifyWebUri.replace('spotify', 'https://open.spotify.com')

        if linkData[0] == 'spotify':
            soup = BeautifulSoup(urllib2.urlopen(spotifyWebUri), "lxml")
            songTitle = soup.title.string.replace(' on Spotify', '')
            return songTitle.encode('ascii','ignore')
        else:
            return "Invalid Spotify url (spotify:*)"

class SvennebananCommand(MusicCommand):
    name = 'svendebanaan'
    def execute(self, bot, user, params):
        self.playSpecificSpotifySong("spotify:track:0YQlHiQDUDTXQ7jiItaJPx")
        return "SVEN DE BANAAN" 

class PiranhaCommand(MusicCommand):
    name = 'piranha'
    def execute(self, bot, user, params):
        self.playSpecificSpotifySong("spotify:track:0byWk11huVUJFC0TGuy1jJ")
        return "PiripiPiripiPiripiPiripiPiranha"

class LiveIsLifeCommand(MusicCommand):
    name = 'live'
    def execute(self, bot, user, params):
        self.playSpecificSpotifySong("spotify:track:5luOvrlnzfvJQdQjrScVj4")
        return "Staat het LIVE!?!!11"

class HoeCommand(MusicCommand):
    name = 'hoe'
    def execute(self, bot, user, params):
        self.playSpecificSpotifySong("spotify:track:6YfvqnvQS7rsSm8Py2Rw8i")
        return "Hoeeeeeeeeeeee?"

class YoutubeCommand(MusicCommand):
    name = 'yt'
    def execute(self, bot, user, params):
        self.stopSpotifyPlayback()
        self.stopYoutubePlayback()
        subprocess.Popen(['/usr/local/bin/mpsyt', 'playurl'] + [params[0]+',q'])

class CurrentCommand(MusicCommand):
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

class CurrentUriCommand(MusicCommand):
    name = 'currenturi'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('uri')

class CurrentUrlCommand(MusicCommand):
    name = 'currenturl'
    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('url')

class CurrentMetaCommand(MusicCommand):
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
        return "Current volume: " + os.popen("amixer -D pulse sget Master | awk '/Front.+Playback/ {print $6==\"[off]\"?$6:$5}' | tr -d '[]' | tail -1").read()

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
