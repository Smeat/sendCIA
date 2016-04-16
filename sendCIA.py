#!/usr/bin/env python

import socket, sys, os, struct, getopt


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
	#sock.recv(1024)
	total_sent = 0;
	while True:
		chunk = input_file.read(1024 * 32)
		if not chunk:
			break
		sock.sendall(chunk)
		total_sent += 1024 * 32 #TODO: calc actual size
		sys.stdout.write("\rTransfer: %i%% %fMb/%fMb" % ((total_sent/float(file_size)) * 100, total_sent/1024.0/1024.0, file_size/1024.0/1024.0))
		sys.stdout.flush()

	print("\n")
	sock.recv(1024)


def main(argv):
   inputfile = ''
   host = ''
   try:
      opts, args = getopt.getopt(argv,"hi:c:",["cia=","ip="])
   except getopt.GetoptError:
      print 'sendCIA.py -c cia file -i ip'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'sendCIA.py -c <cia file> -i <ip>'
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
