#!/usr/bin/env python

import subprocess
import threading
import os
import time
import json

class Pinger(object):
    status = {'alive': [], 'dead': []} # Populated while we are running
    hosts = [] # List of all hosts/ips in our input queue
    # How many ping process at the time.
    thread_count = 4
    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()
#    def clear(self):
#        self.status = []

    def ping(self, ip):
        # Use the system ping command with count of 1 and wait time of 1.
        ret = subprocess.call(['ping', '-c', '1', '-W', '1', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        return ret == 0 # Return True if our ping command succeeds
    
    def pop_queue(self):
        ip = None
        self.lock.acquire() # Grab or wait+grab the lock.
        if self.hosts:
            ip = self.hosts.pop()
        self.lock.release() # Release the lock, so another thread could grab it.
        return ip

    def dequeue(self):
        while True:
            ip = self.pop_queue()
                
            if not ip:
                return None
        
            result = 'alive' if self.ping(ip) else 'dead'
            self.status[result].append(ip)

    def start(self):
#        self.status = {}
        threads = []
#        print "internal status"
#        print self.status
        self.status = {'dead': [], 'alive': []} #this resets the list
        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)
        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]
        return self.status


home_network = "10.0.1."
ip = []
for each in range(210,230):
    ip.append(home_network + str(each))
print "testing ips"
print sorted(ip)


if __name__ == '__main__':
    while True:
        ping = Pinger()
        ping.thread_count = 16
        home_network = "10.0.1."
        ip = []
        for each in range(210,230):
    #    for each in range(1,256):
            ip.append(home_network + str(each))
#        print "testing ips"
#        print ip
        ping.hosts = ip
    #    ping.hosts = [
    #                  '10.0.1.211','10.0.1.212','10.0.1.213','10.0.1.214','10.0.1.215',
    #                  '10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4', '10.0.0.0', '10.0.0.255', '10.0.0.100',
    #                  'google.com', 'github.com', 'nonexisting', '127.0.1.2', '*not able to ping!*', '8.8.8.8'
    #                  ]
    #    print status
#        print ""
        status = ping.start()
#        print "All ips"
#        print status
#        print ""
        print "Alive ips",
        print sorted(status['alive'])
#        print ""
#        print "sleeping for 5 seconds"
#        f = open('outputfile.txt', 'w')
#        f.write(str(status))
#        f.close()

#        with open("/var/www/index.html","w") as outfile:
        with open("outputfile.json","w") as outfile:
            json.dump(status,outfile,indent=4)
        time.sleep(5)
#        os.system("clear")
