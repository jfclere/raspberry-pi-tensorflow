#!/usr/bin/python
'''
	Based on the work off:
	Author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from io import StringIO
import time
from picamera2 import Picamera2
from detect import Detector

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print("do_GET")
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					# capture main.
					img_bytes = detector.detect(512, 512)
					print("sending saved image...")
					self.wfile.write(b'--')
					self.wfile.write(b"--jpgboundary")
					self.wfile.write(b'\r\n')
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(len(img_bytes)))
					self.end_headers()
					self.wfile.write(img_bytes)
					time.sleep(0.05)
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html'):
			print("html request")
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(bytes('<html><head></head><body>', "utf-8"))
			self.wfile.write(bytes('<img src="http://192.168.1.119:8080/cam.mjpg"/>', "utf-8"))
			self.wfile.write(bytes('</body></html>', "utf-8"))
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global detector
	detector = Detector()

	try:
		server = ThreadedHTTPServer(('', 8080), CamHandler)
		print("server started")
		server.serve_forever()
	except KeyboardInterrupt:
		detector.cleanup()
		server.socket.close()

if __name__ == '__main__':
	main()

