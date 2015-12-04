from twisted.words.protocols import irc
from twisted.internet import ssl, reactor, protocol
from twisted.python import log

import os
import time
import sys
import getpass
import ConfigParser

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class MusicBot(irc.IRCClient):
    """A logging IRC bot."""

    commandPrefix = "!music"

    def __init__(self):
        self.commandHandler = CommandHandler(CommandManager())

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        if channel == self.factory.channel:
            if str.startswith(msg, self.commandPrefix):
                print "command prefix found!\n"
                words = msg.split(" ")
                commandName = "help"
                if len(words) > 1:
                    commandName = words[1]

                arguments = words[2::]
                output = self.commandHandler.handleCommand(self, user, commandName, arguments)
                if output is not None:
                    self.sendMessage(output)

    def registerCommand(self, command):
        self.commandHandler.getCommandManager().addCommand(command)

    def sendMessage(self, message):
        print "sending message"
        print message
        lines = message.split("\n")
        for line in lines:
                self.say(self.factory.channel, line)

    def getCommandHandler(self):
        return self.commandHandler

    def getMaster(self):
        return self.factory.master




class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, nickname, password, master, filename):
        self.channel = channel
        self.filename = filename
        self.nickname = nickname
        self.password = password
        self.master = master

    def buildProtocol(self, addr):
        p = MusicBot()
        p.registerCommand(HelpCommand())
        p.registerCommand(NextCommand())
        p.registerCommand(PrevCommand())
        p.registerCommand(CurrentCommand())
        p.registerCommand(VolUpCommand())
        p.registerCommand(VolDownCommand())
        p.registerCommand(WhitelistCommand())
        p.factory = self
        p.nickname = self.nickname
        p.password = self.password
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    from command import CommandManager, CommandHandler, HelpCommand, NextCommand, PrevCommand, CurrentCommand, VolUpCommand, VolDownCommand, WhitelistCommand

    config = ConfigParser.ConfigParser()
    config.read('bot.config')

    server = config.get('main', 'server')
    port = config.getint('main', 'port')
    channel = config.get('main', 'channel')
    user = config.get('main', 'user')
    password = config.get('main', 'password')
    master = config.get('main', 'master')

    if password == -1:
        password = getpass.getpass()

        # initialize logging
    log.startLogging(sys.stdout)
    # create factory protocol and application
    f = LogBotFactory(channel, user, password, master, "log")

    # connect factory to this host and port
    reactor.connectSSL(server, port, f, ssl.ClientContextFactory())

    # run bot
    reactor.run()

spotifyScript = os.path.realpath(os.path.dirname(__file__)) + "/spotify.sh"
whitelistFile = "whitelist.txt"