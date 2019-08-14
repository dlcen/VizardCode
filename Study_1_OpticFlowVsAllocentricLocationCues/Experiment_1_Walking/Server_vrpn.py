# This code is to control the experimental workflow and record position and orientation data

import viz
import viztask
import vizshape
import viznet
import vizinfo
import time

#viz.window.setFullscreenMonitor(2)
viz.go()
view=viz.MainView

# Set up the position of the camera for a better view of the monitoring (see below)
view.setPosition([0,10,3.5]); view.setEuler(45,90,0) 

# Add other computers to the local network
myNetwork = viz.addNetwork('Simon-Dell') # the backpack laptop
VRPNhost = 'SimonR-PC' # the PC that sends out the VRPN signal

info  = vizinfo.InfoPanel('monitoring', align=viz.ALIGN_CENTER, icon=False)

# Setup VRPN
vrpn = viz.add('vrpn7.dle')
head = vrpn.addTracker('Tracker0@'+VRPNhost, 9)
body = vrpn.addTracker('Tracker0@'+VRPNhost, 10)
tracker = vrpn.addTracker('Tracker0@'+VRPNhost, 4)
head.swapPos([1,2,-3])
head.swapQuat([-1, -2, 3, 4])
body.swapPos([1,2,-3])
body.swapQuat([-1, -2, 3, 4])
# tracker.swapPos([1,2,-3])

# For monitoring purposes, create a scene 
# - two cylinders respectively representing the two locations of the target
# - two objects respectively representing the head and body (shoulder)
ground=viz.add('ground.osgb')
target_1=vizshape.addCylinder(height=3, radius=0.02); target_1.color(viz.RED); target_1.setPosition([0, 0, 0])
target_2=vizshape.addCylinder(height=3, radius=0.02); target_2.color(viz.RED); target_2.setPosition([0, 0, 7])
body_rep=vizshape.addBox([0.2,0.2,0.2]); body_rep.color(viz.YELLOW_ORANGE)
headlink=viz.link(head, view)
bodylink=viz.link(body, body_rep)

# Define the function to record the location and rotation data
def writing(trialNo):
	record = open('VRpath_' + trialNo + time.strftime('_%Y-%m-%d_%H-%M-%S') + '.csv', 'a')   
	data= 'FrameNo, TimeStamp, Head_x, Head_y, Head_z, Head_yaw, Head_pitch, Head_roll, Body_x, Body_y, Body_z, Body_yaw, Body_pitch, Body_roll, Head2_x, Head2_y, Head2_z'
	record.write(data + '\n')
	FrameNo=1 

	while True:
		data=[]
		data=str(FrameNo) + ',' + str(viz.tick()) + ','+str(head.getPosition()).strip('[]')+','+str(head.getEuler()).strip('[]')+','+str(body.getPosition()).strip('[]')+','+str(body.getEuler()).strip('[]')+','+str(tracker.getPosition()).strip('[]')
		FrameNo+=1
		record.write(data + '\n')
		yield viztask.waitTime(1/120)

# Listen the local network for signals of starting and ending recording
def onNetwork(e):
	msg=str(e.data)
	info.setText(msg)
	if msg[2]=='B':
		global recording
		print msg
		recording=viztask.schedule(writing(msg[2:-3].replace(' ', '_',3)))
	elif msg[2]=='R':
		try: 
			recording.kill()
		except NameError:
			pass
		
viz.callback(viz.NETWORK_EVENT, onNetwork)

# Define the key on keyboard (S) to start the trial
def keyInstruc(key):
	if key == 's' or key == 'S':
		myNetwork.send(message='start')
		
viz.callback(viz.KEYDOWN_EVENT, keyInstruc)