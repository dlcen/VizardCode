import viz
import viztask
import vizshape
import viznet
import vizinfo
import time

#viz.window.setFullscreenMonitor(2)
viz.go()
view=viz.MainView
view.setPosition([0,10,3.5]); view.setEuler(45,90,0)

myNetwork = viz.addNetwork('Simon-Dell')
VRPNhost = 'SimonR-PC'

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

ground=viz.add('ground.osgb')
target_1=vizshape.addCylinder(height=3, radius=0.02); target_1.color(viz.RED); target_1.setPosition([0, 0, 0])
target_2=vizshape.addCylinder(height=3, radius=0.02); target_2.color(viz.RED); target_2.setPosition([0, 0, 7])
body_rep=vizshape.addBox([0.2,0.2,0.2]); body_rep.color(viz.YELLOW_ORANGE)
headlink=viz.link(head, view)
bodylink=viz.link(body, body_rep)


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


def keyInstruc(key):
	if key == 's' or key == 'S':
		myNetwork.send(message='start')
		
viz.callback(viz.KEYDOWN_EVENT, keyInstruc)