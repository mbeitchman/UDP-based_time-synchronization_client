# Marc Beitchman
# CSE P 552
# HW1
# 4/12/3013 

import socket
import time

# class to hold data from a sucessful interaction
class InteractionData:
	RTT = 0
	Clock_Offset = 0
	Smoothed_Clock_Offset = 0

# data needed for interactions with the timer server
UDP_IP = "futureproof.cs.washington.edu"
UDP_PORT = 5555
MESSAGE = ""
seq_number = 0
ITERATIONS = 4320
LIST_SIZE = 8
TIMEOUT = 8 # in seconds

# list of interaction data to be used for smoothing
RecentInteractions = list()

# open file for storing data
f = open('log.txt', 'w')

# create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)

# run th client for 12 hours
while (seq_number < ITERATIONS):

	print seq_number

	data = ""

	INITIAL_TIME = time.time()
	MESSAGE = '{0} {1}'.format(seq_number, "%f" % INITIAL_TIME)

	# send the packet and get the response from the server
	# if the response times out, log the timeout and start a new iteration
	try:
		sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
		data, addr = sock.recvfrom(64)
		RECEIVED_TIME = time.time()
	except socket.timeout:
		seq_number += 1;
		f.write("timeout\n")
		continue
	
	# parse the response
	d = data.split()

	# if the sequence number doesn't match the current packet
	# then drop the packet and continue
	if int(d[0]) != seq_number:
		f.write("invalid seq number\n")
		seq_number += 1
		continue;

	# create a new result object and calculate data
	resultData = InteractionData()
	resultData.RTT = (float(d[2]) - float(d[1])) + (RECEIVED_TIME - float(d[3]))
	resultData.Clock_Offset = ((float(d[2]) - float(d[1])) - (RECEIVED_TIME - float(d[3])))/2

	# remove a data object off the end of the list if the list is full
	if len(RecentInteractions) == LIST_SIZE:
		RecentInteractions.pop(0)

	# add the new data object to the beginning of the list
	RecentInteractions.append(resultData)

	# find the lowest RTT value in the list and used the associated offset as the smoothed offset
	lowrtt = RecentInteractions[0].RTT
	smooted_co = RecentInteractions[0].Clock_Offset
	for r in RecentInteractions:
		if r.RTT < lowrtt:
			lowrtt = r.RTT
			smooted_co = r.Clock_Offset

	resultData.Smoothed_Clock_Offset = smooted_co
	
	curtime = time.time()

	# write data to log
	f.write('message {0},{1},{2},{3},{4},{5}\n'.format(seq_number, resultData.RTT, resultData.Clock_Offset, "%f" % curtime, "%f" % (curtime+resultData.Smoothed_Clock_Offset), resultData.Smoothed_Clock_Offset))

	# increment the sequence number and wait 10 seconds to do the next request
	seq_number += 1
	time.sleep(10)

# close the file and the socket
sock.close()
f.close()