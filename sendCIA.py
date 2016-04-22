#!/usr/bin/env python

import socket, sys, os, struct, getopt, time, collections

speed_samples = collections.deque(maxlen=20)

def add_transfer_speed_sample(size, time):
	speed_samples.append((size/1024.0)/time)
	
def get_avg_transfer_speed():
	i = 0
	acc_speed = 0
	for speed in speed_samples:
		acc_speed += speed
		i+=1
		
	return acc_speed/i

def connect(host, port):
	for info in socket.getaddrinfo(host, "5000", socket.AF_UNSPEC, socket.SOCK_STREAM):
		af, socktype, proto, canonname, sa = info

	sock = socket.socket(af, socktype, proto)
	sock.connect(sa)
	
	return sock

def send_cia(sock, path):
	input_file = open(path, "rb")

	file_num_net = struct.pack('!L', 1)
	file_size = os.stat(path).st_size
	file_size_net = struct.pack('!Q', file_size)

	sock.send(file_num_net)
	sock.send(file_size_net)
	sock.recv(1024)
	total_sent = 0;
	while True:
		start = time.perf_counter()
		chunk_size = 1024 * 1024 #TODO: test other values
		chunk = input_file.read(chunk_size)
		if not chunk:
			break
		
		sock.sendall(chunk)
		total_sent += chunk_size #TODO: calc actual size
		add_transfer_speed_sample(chunk_size, time.perf_counter() - start) #TODO: is it even accurate?
		sys.stdout.write("\rTransfer: %i%% %.2fMb/%.2fMb %.2fkb/s                     " % ((total_sent/float(file_size)) * 100, total_sent/1024.0/1024.0, file_size/1024.0/1024.0, get_avg_transfer_speed()))
		sys.stdout.flush()

	print("\n")
	sock.recv(1024)


def main(argv):
   inputfile = ''
   host = ''
   try:
      opts, args = getopt.getopt(argv,"hi:c:",["cia=","ip="])
   except getopt.GetoptError:
      print ("sendCIA.py -c cia file -i ip\n")
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ("sendCIA.py -c <cia file> -i <ip>\n")
         sys.exit()
      elif opt in ("-c", "--cia"):
         inputfile = arg
      elif opt in ("-i", "--ip"):
         host = arg   
   
   sock = connect(host, "5000")
   
   send_cia(sock, inputfile)
   print("File 1 complete\n") #TODO: multiple files
   
   sock.close()

if __name__ == "__main__":
   main(sys.argv[1:])
