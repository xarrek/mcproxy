#!/usr/bin/env python
import asyncore, socket, struct

protocol = 61
mcVersion = '1.5.2'
ssHost = ''
ssPort = 25555
mcMotd = 'A Minecraft Server'
mcMaxplayers = 666
mcOnlineplayers = 666
mcHost = ''
mcPort = 25565
mcKick = 'Graczu: %s nie ma Cie na whiteliscie!'

def log(text):
    print ""+text

class SuperServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(asyncore.socket.AF_INET, asyncore.socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        log("Listening on: '%s:%d'" % (host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            socket, address = pair
        log(' Incoming connection from %s' % repr(address))
        handler = ProxyHandler(socket)

class ProxyHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.sent = None
        
    def handle_read(self):
        data = self.recv(8192)
        #log(repr(data))
        if len(data) != 0:
            c = data[:1]
            if c == '\xFE':
                log('Server List Ping')
                self.sent = self.close
                string = '%d\x00%s\x00%s\x00%d\x00%d' % (protocol, mcVersion, mcMotd, mcOnlineplayers, mcMaxplayers)
                strlen = len(string)+3
                string = string.encode('utf-16be')
                string = '\x00\xa7\x00\x31\x00\x00' + string
                desc = '\xFF' + struct.pack('>h%ds' % len(string), strlen, string)
                self.send(desc)
                #log(repr(desc))
            elif c == '\x02':
                log('Handshake')
                if len(data) >= 3:
                    uname = data[4:len(data)-2]
                    uname = uname.split('\x00\t')
                    log(' Username: %s' % uname[0].decode('utf-16be'))
                    self.sent = self.close
                    string = mcKick % uname[0].decode('utf-16be')
                    strlen = len(string)
                    string = string.encode('utf-16be')
                    desc = '\xFF' + struct.pack('>h%ds' % len(string), strlen, string)
                    self.send(desc)
            else:
                log("Lol pakiet!")
                self.close()
        else:
            self.close()
        
def main():
    global ss
    ss = SuperServer(ssHost, ssPort)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print "Exit"

if __name__ == "__main__":
    main()
