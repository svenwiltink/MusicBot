import bot
import subprocess
import os
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
        whitelistFile = open('whitelist.txt')
        lines = whitelistFile.read().splitlines()
        self.whitelist = lines

    def handleCommand(self, bot, user, commandName, arguments):
        if user not in self.whitelist:
            return
        print "handeling command " + commandName
        command = self.commandManager.getCommand(commandName)
        if command is None:
            return "Command not found"
        return command.execute(bot, user, arguments)

    def getCommandManager(self):
        return self.commandManager


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


class CurrentCommand(SpotifyCommand):
    name = 'current'

    def execute(self, bot, user, params):
        return self.executeSpotifyCommand('current')


class VolUpCommand(Command):
    name = 'vol++'

    def execute(self, bot, user, params):
        os.system("amixer -D pulse sset Master 10%+ >/dev/null")


class VolDownCommand(Command):
    name = 'vol--'

    def execute(self, bot, user, params):
        os.system("amixer -D pulse sset Master 10%- >/dev/null")
