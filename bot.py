import configparser
import ssl
import socket
import threading
from MusicPlayer import MusicPlayer, YoutubeQueueItem, SpotifyQueueItem


class IrcClient(object):

    def __init__(self, options):
        self.server = options.get('server')
        self.port = options.get('port')
        self.ident = options.get('ident')
        self.nick = options.get('nick')
        self.realname = options.get('realname')
        self.password = options.get('password')
        self.ssl = options.get('ssl', False)

        self.connection_thread = None
        self.disconnect = threading.Event()
        self.event_listeners = {}

    def connect(self):
        self.connection_thread = threading.Thread(target=self.__connect)
        self.connection_thread.start()
        print("exit")

    def disconnect(self):
        self.disconnect.set()

    def __connect(self):
        read_buffer = ""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl:
            self.s = ssl.wrap_socket(self.s)

        self.s.connect((self.server, self.port))
        self.__send_string("PASS {}\r\n".format(self.password))
        self.__send_string("NICK {}\r\n".format(self.nick))
        self.__send_string("USER {} {} bla :{}\r\n".format(self.ident, self.server, self.realname))

        while 1:
            read_buffer = read_buffer+self.s.recv(1024).decode()

            temp = read_buffer.split("\n")
            read_buffer = temp.pop()

            for line in temp:
                print(line)
                line = line.rstrip()
                line = line.split()
                print(line)
                if line[0] == "PING":
                    self.__send_string("PONG %s\r\n" % line[1])

                # we assume it is safe to send data after receiving the welcome message
                if len(line) > 1 and line[1] == '001':
                    self.on_connect()

                if len(line) > 1 and line[1] == 'PRIVMSG':
                    identString = line[0][1:]
                    nick = identString.split("!")[0]
                    realname = identString.split("!")[1].split("@")[0]
                    ip = identString.split("@")[1]

                    ident = Ident(nick, realname, ip)

                    channel = line[2]
                    message = " ".join(line[3:])[1:]

                    self.on_message(ident, channel, message)

    def __send_string(self, string):
        self.s.send(string.encode())

    def __emit(self, eventname, data):
        event_listeners = self.event_listeners
        if eventname in event_listeners:
            for listener in event_listeners[eventname]:
                listener(self, data)

    def send_message(self, dest, message):
        lines = message.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                self.__send_string("PRIVMSG {} {}\r\n".format(dest, line))

    def on_message(self, ident, channel, message):
        self.__emit('PRIVMSG', (ident, channel, message))

    def on_connect(self):
        self.__emit('connected', None)

    def join_channel(self, channel):
        self.__send_string("JOIN {}\r\n".format(channel))

    def on(self, eventname, callback):
        if eventname not in self.event_listeners:
            self.event_listeners[eventname] = []

        self.event_listeners[eventname].append(callback)


class Ident(object):

    def __init__(self, nick, ident, ip):
        self.nick = nick
        self.ident = ident
        self.ip = ip

    def get_nick(self):
        return self.nick

    def get_ident(self):
        return self.ident

    def get_ip(self):
        return self.ip

config = configparser.ConfigParser()
config.read('bot.cfg')

spotify_user = config.get('main', 'spotify_user')
spotify_pass = config.get('main', 'spotify_pass')

options = {
    'server': config.get('main', 'server'),
    'port': config.getint('main', 'port'),
    'channel': config.get('main', 'channel'),
    'ident': config.get('main', 'ident'),
    'nick': config.get('main', 'nick'),
    'realname': config.get('main', 'realname'),
    'password': config.get('main', 'password'),
    'ssl': True
}

wait_for_connect = threading.Event()


def on_connect(bot, data):
    wait_for_connect.set()


def on_message(bot, data):
    """

    :type bot: IrcClient
    :type data: list
    """

    def print_help(bot, dest):
        bot.send_message(dest, "---------MusicBot---------")
        bot.send_message(dest, "!music yt <link> -- plays a youtube link")
        bot.send_message(dest, "!music sp <link> -- plays a spotify link")

    (ident, channel, message) = data
    words = message.split(" ")
    args = words[1:]
    first_word = words[0]
    if first_word == "!music":
        if len(args) == 2 and args[0] == 'yt':
            url = args[1]
            item = YoutubeQueueItem(url)
            player.add_to_queue(item)
        elif len(args) == 2 and args[0] == 'sp':
            url = args[1]
            item = SpotifyQueueItem(url)
            player.add_to_queue(item)
        elif len(args) == 1 and args[0] == 'list':
            queue = "Items in queue:\r\n"
            queue += player.get_queue_string()
            bot.send_message(channel, queue)
        else:
            print_help(bot, ident.get_nick())

player = MusicPlayer(spotify_user, spotify_pass)
player.start()

bot = IrcClient(options)
bot.on('connected', on_connect)
bot.on('PRIVMSG', on_message)

bot.connect()
wait_for_connect.wait()
bot.join_channel(config.get('main', 'channel'))
