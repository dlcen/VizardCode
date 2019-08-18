from PyDAQmx import *
import viz, vizact, viztask, vizshape, viznet, numpy, time, os, copy, csv, vizproximity

viz.go()
# constants
global t, Response, x, colors, off, real_tg_dist
x = 10 * numpy.hstack((numpy.zeros(95), numpy.ones(5)))
real_tg_dist = (0, 6.5, 0.5)

# Local network
monitor_record_Network = viz.addNetwork('SimonR-PC')
VRPNhost = 'SimonR-PC'

# Setup VRPN
vrpn = viz.add('vrpn7.dle')
head = vrpn.addTracker('Tracker0@'+VRPNhost, 9)
body = vrpn.addTracker('Tracker0@'+VRPNhost, 10)
tracker = vrpn.addTracker('Tracker0@'+VRPNhost, 4)
head.swapPos([1,2,-3])
head.swapQuat([-1, -2, 3, 4])
body.swapPos([1,2,-3])
body.swapQuat([-1, -2, 3, 4])

# Set up proximity sensor
manager = vizproximity.Manager()
target = vizproximity.Target(head)
manager.addTarget(target)

# LED flashing for single trial
class LEDs(object):

	def __init__(self, colors, highTime, lowTime):
		self.taskHandle = Task()
		self.taskHandle.CreateDOChan('Dev1/port0/line0:7', '', DAQmx_Val_ChanForAllLines)
		self.colors = colors
		self.on = numpy.array([0,1,1,1,1,1,1,0], dtype = uInt8)
		self.red1 = numpy.array([0, 0, 0, 0, 1, 0, 0, 0], dtype = uInt8)
		self.red2 = numpy.array([0, 1, 0, 0, 0, 0, 0, 0], dtype = uInt8)
		self.yellow1 = numpy.array([0, 0, 0, 0, 0, 0, 1, 0], dtype = uInt8)
		self.yellow2 = numpy.array([0, 0, 0, 1, 0, 0, 0, 0], dtype = uInt8)
		self.green1 = numpy.array([0, 0, 0, 0, 0, 1, 0, 0], dtype = uInt8)
		self.green2 = numpy.array([0, 0, 1, 0, 0, 0, 0, 0], dtype = uInt8)
		self.standByItv = 0.5
		self.off = numpy.array([0,0,0,0,0,0,0,0], dtype = uInt8)
		self.highTime = highTime
		self.lowTime = lowTime
		self.t = []
		self.Response = []

	def all_on(self):
		self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.on, None, None)

	def all_off(self):
		self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
	
	def standby(self, mod):
		self.taskHandle.StartTask()
		if mod == 1:
			while True:
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.red2, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.yellow2, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.green2, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
		elif mod == 0: 
			while True:
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.red1, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.yellow1, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.green1, None, None)
				yield viztask.waitTime(self.standByItv)
				self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)

	def flashing(self):
		self.taskHandle.StartTask()
		for nextColor in self.colors:
			self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, self.off, None, None)
			yield viztask.waitTime(self.lowTime)
			self.taskHandle.WriteDigitalLines(1, 1, 5.0, DAQmx_Val_GroupByChannel, nextColor, None, None)
			self.t.append(viz.tick())
			self.Response.append('')
			yield viztask.waitTime(self.highTime)

	def stop(self):
		self.taskHandle.StopTask()
	
	def clear(self):
		self.taskHandle.ClearTask()

	# Register response for the color changing task
	def recordResp(self):
		try:
			respTime = viz.tick()
			if self.Response[-1] == '':
				self.Response.pop()
				self.Response.append(respTime)
			else:
				self.Response[-1] = [self.Response[-1], respTime] 
		except:
			pass

	# Save response date in to a .csv file
	def saveAsFile( self, fileName ):
		with open(fileName, 'wb') as csvfile:
			csvwriter = csv.writer( csvfile, delimiter = ',')
			header = ['FlashNo' ,' TimeStamp' ,'Color' , 'Response']
			csvwriter.writerow(header)
			for n, timeStamp in enumerate(self.t):
				thisLine = [str(n+1) , str(timeStamp) , str(self.colors[n]).strip('[]') , str(self.Response[n]).strip('[]')]
				csvwriter.writerow(thisLine)

# Strobe flashing
def Strobes( waveform, sampleRate ):
	sampleRate = sampleRate
	periodLength = len(waveform)
	taskHandle = Task()
	
	data = numpy.zeros( (periodLength, ), dtype = numpy.float64 )
	for i in range( periodLength ):
		data[ i ] = waveform [ i ]
	taskHandle.CreateAOVoltageChan( "Dev1/ao3", "", -10.0, 10.0, DAQmx_Val_Volts, "")
	taskHandle.CfgSampClkTiming( "", sampleRate, DAQmx_Val_Rising, DAQmx_Val_ContSamps , periodLength)
	taskHandle.WriteAnalogF64( periodLength, 0, -1.0, DAQmx_Val_GroupByChannel, data, None, None)		
	return taskHandle

# The procedure for the whole experiment
def experiment():
	for trialN in range(10):
		if trialN < 9: 
			datafile = 'Trial0' + str(trialN + 1) + '.txt'
			respfile = 'RT_Trial0' + str(trialN + 1) +  time.strftime("_%d-%b-%y_%H-%M") + '.csv'
		else:
			datafile = 'Trial' + str(trialN + 1) + '.txt'
			respfile = 'RT_Trial' + str(trialN + 1) +  time.strftime("_%d-%b-%y_%H-%M") + '.csv'

		colors = []
		with open(datafile, 'rb') as csvfile:
			csvreader = csv.reader(csvfile, delimiter = ' ')
			for row in csvreader:
				colors.append(row)
		colors = numpy.asarray( colors, dtype = uInt8 ); # colors = colors[0]

		strobes = Strobes( x, 100 )
		leds = LEDs(colors, 0.05, 0.9403)
		vizact.onkeydown('.', leds.recordResp)

		sensor_Target = vizproximity.Sensor(vizproximity.RectangleArea([4, 0.1],  center=[0, real_tg_dist[(-1)**trialN]]), None)
		manager.addSensor(sensor_Target); 

		# Show where the target is and ask them to face to the target
		yield viztask.waitKeyDown('a')
		standBy = viztask.schedule(leds.standby(trialN%2))
		# Turn of the LED to get the experiment ready to start
		yield viztask.waitKeyDown('s')
		standBy.kill()
		leds.all_off()
		leds.stop()
		monitor_record_Network.send('Start!')
		strobes.StartTask()
		f = viztask.schedule(leds.flashing())
		monitor_record_Network.send('Start!')
		yield vizproximity.waitEnter(sensor_Target) # flash until they enter the target zone
		f.kill()
		# Once reach the target turn off both the LEDs and strobes
		strobes.StopTask()
		strobes.ClearTask()
		leds.all_off()
		leds.stop()
		leds.clear()
		# Save the data into a csv file
		leds.saveAsFile( respfile )
		manager.clearSensors()
	
	yield viztask.waitTime(10)
	viz.quit()
		
viztask.schedule(experiment())




