# This is the code to run in the backpack laptop. 
# It generates the virtual stimuli that is presented on the Oculus HMD.

import viz
import viztask
import vizact
import vizinfo
import vizproximity
import vizshape
import time
import viznet
import vizinput
import random
import numpy as np
from Environments import * # import the virtual environments
import oculus
import os

# Initialize window
viz.setMultiSample(8)
viz.go() # Should call this early to avoid some errors
viz.mouse.setVisible(False)

# Read the information from the folder name
# The folder name contains all information including:
# 	- participant id
# 	- condition sequence
# 	- prism direction sequence
path=os.getcwd()
folder=path.split('\\')
folder=folder[-1]
folder=folder.split('_')

id=folder[0]
Sequence=folder[1]
side=folder[2]
distance=7
freq=37
ipd=62
sub_ipd=ipd/1000

# Helps reduce latency
viz.setOption('viz.glFinish',1)
#viz.vsync(0)
viz.setOption('viz.max_frame_rate',75)

# Setup Oculus Rift HMD
hmd = oculus.Rift()
if not hmd.getSensor():
	sys.exit('Oculus Rift not detected')

# Go fullscreen if HMD is in desktop display mode
if hmd.getSensor().getDisplayMode() == oculus.DISPLAY_DESKTOP:
	viz.window.setFullscreen(True)

#hmd.setTimeWarp(False)
hmd.setIPD(sub_ipd)

# Network Setup
serverName = 'srushton-PC'
VRPNhost = 'SimonR-PC'
myNetwork = viz.addNetwork(serverName)

# Set up Tracking 
vrpn = viz.add('vrpn7.dle') 
ori_marker = vrpn.addTracker('Tracker0@' + VRPNhost,9)
ori_marker.swapPos([1,2,-3])
ori_marker.swapQuat([-1,-2,3,4])
pos_marker = vrpn.addTracker('Tracker0@' + VRPNhost,4)


# Setup navigation node and link to main view
view=viz.MainView
viewLink = viz.link(ori_marker, view, mask=viz.LINK_ORI)

def UpdatePos():
	pos=pos_marker.getPosition()
	view.setPosition([pos[0],pos[1]-0.2,-pos[2]+0.2], viz.ABS_GLOBAL)
updateView=vizact.ontimer(0,UpdatePos)



########################################################################################################
# Set up Target
Target = vizshape.addCylinder(height = 3, radius=0.02) #Change the diameter of the target
Target.setPosition([0,1.5,distance], viz.ABS_GLOBAL)
Target.visible(viz.OFF)

info = hmd.addMessagePanel(' ', pos=(0,0,3))
info.visible(viz.OFF)

# Setup metronome
sound=viz.addAudio('Bottle_80.mp3')
sound.loop(viz.ON)
sound.volume(1)

sub_rt = open('VRrt_' + id + '_Seq-' + Sequence + '_Offset-' + side + '_' + time.strftime("%d-%b-%y_%H-%M") + '.csv', 'a')
		
Color = [viz.RED,viz.GREEN,viz.YELLOW]
def changeColor(node):
	lastColor=random.randint(0, 2)
	while True:
		node.color(Color[lastColor])
		d=yield viztask.waitDraw()
		data = '  ,'+ str(lastColor)+','+str(d.time)
		sub_rt.write('\n'+data)
		tmp_color=[0, 1, 2]
		tmp_color.remove(lastColor)
		lastColor=random.choice(tmp_color)
		yield viztask.waitTime(0.75)

def reactTime():
	clicktime=viz.tick()
	sub_rt.write(','+str(clicktime))
vizact.onkeydown('.', reactTime)

SPpos = ([0,0,0],[0,1.5,0],[0,1.5,distance])

# Set up proximity sensors
manager = vizproximity.Manager()

target = vizproximity.Target(view)
manager.addTarget(target)

sensor_Target = vizproximity.Sensor(vizproximity.Box([0.6, 6, 0.1]), source=Target)
manager.addSensor(sensor_Target)

# Refresh dots
def refreshing(clouds):
	index=0
  	while True: 
		clouds[index].remove()
		pos=np.random.uniform(low=-6, high=6, size=(5250/freq,3))
		pos[:,1]=pos[:,1]/4
		pos[:,2]=pos[:,2] -5
		viz.startLayer(viz.POINTS)
		viz.pointSize(2)
		for n in range(5250/freq):		
			viz.vertex(pos[n,0], pos[n,1], pos[n,2])
		single_cloud=viz.endLayer()
		single_cloud.disable(viz.CULLING)
		single_cloud.setParent(Target)
		clouds.append(single_cloud)
		index+=1
		yield viztask.waitDraw()

# Experiment Set up
def trialSetting_Exp(block_no, node):
	info.setText("Hurrah!! Please wait for the experimenter.")
	for m in range(4):
		
		yield viztask.waitNetwork(serverName)
		sub_rt.write('\nBlock ' + str(block_no) + ' Trial '+ str(m+1))
		node.color(viz.ORANGE); Target.visible(viz.ON)
		myNetwork.send('Ready')
		yield viztask.waitNetwork(serverName)
		sound.play()
		myNetwork.send('Block ' + str(block_no) + ' Trial ' + str(m+1))
		colorChange=viztask.schedule(changeColor(node))
				
		yield vizproximity.waitEnter(sensor_Target)
		Target.visible(viz.OFF)
		sound.stop()
		colorChange.kill()
		myNetwork.send('Reach Target!')
			
		ori = (1+(-1)**m)*90
		Target.setPosition(SPpos[(-1)**m], mode = viz.ABS_PARENT)
		Target.setEuler([ori,0,0],mode=viz.REL_LOCAL)
		
		if m < 3:
			info.visible(viz.ON)
			yield viztask.waitTime(3)
			info.visible(viz.OFF)
		else:
			sub_rt.write('\nend of block'+ str(block_no))
			info.setText('End of Block ' + str(block_no))
			info.visible(viz.ON)
			yield viztask.waitTime(3)
			info.visible(viz.OFF)

def Practice(block_no, node):
	ground=GroundCreator()
	ground.setParent(Target)
	ground.setPosition([0,-1.5,-1], viz.REL_PARENT)
	yield viztask.waitNetwork(serverName)
	info.setText('Block ' + str(block_no))
	info.visible(viz.ON)
	yield viztask.waitTime(2)
	info.visible(viz.OFF)
	yield trialSetting_Exp(block_no, node)
	ground.remove()

def experiment(side):
	yield viztask.waitNetwork(serverName)
	
	yield Practice(1, Target)
	
	for i in range(len(Sequence)):
		block=(i+1)*2

		if side=='LR':
			if i==0 or i==2:
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)
			else:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
		else:
			if i==0 or i==2:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
			else:    
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)

		if Sequence[i]=='C' or Sequence[i]=='c':
			clouds=flashingCloud(3, 12, 12, 1, 5250, Target,freq)
			refresh=viztask.schedule(refreshing(clouds))
			yield viztask.waitNetwork(serverName)
			info.setText('Block ' + str(block))
			info.visible(viz.ON)
			yield viztask.waitTime(2)
			info.visible(viz.OFF)
			yield trialSetting_Exp(block, Target)
			for c in clouds:
				c.remove()
			refresh.kill()

		elif Sequence[i]=='L' or Sequence[i]=='l':
			yield viztask.waitNetwork(serverName)
			info.setText('Block ' + str(block))
			info.visible(viz.ON)
			yield viztask.waitTime(2)
			info.visible(viz.OFF)
			yield trialSetting_Exp(block, Target)

		elif Sequence[i]=='O' or Sequence[i]=='o':
			Target.alpha(0)
			door=door_line(2.5, 0.5, 2)
			door.setParent(Target)
			door.setPosition([0,-1.5,0], viz.REL_PARENT)
			door.zoffset(-1)
			outlineRoom=room_line(3, 12, 12, 2)
			outlineRoom.setParent(Target)
			outlineRoom.setPosition([0,-1.5,0], viz.REL_PARENT)
			yield viztask.waitNetwork(serverName)
			info.setText('Block ' + str(block))
			info.visible(viz.ON)
			yield viztask.waitTime(2)
			info.visible(viz.OFF)
			yield trialSetting_Exp(block, door)
			door.remove(); outlineRoom.remove()
			Target.alpha(1)

		elif Sequence[i]=='F' or Sequence[i]=='f':
			Target.alpha(0)
			door=doorway(2.5, 0.5, 0.025)
			door.setParent(Target)
			door.setPosition([0,-1.5,0], viz.REL_PARENT)
			door.zoffset(-1)
			room_env=RoomCreator(12, 12, 3, 1)
			room_env.setParent(Target)
			room_env.setPosition([0,-1.5,-11], viz.REL_PARENT)
			yield viztask.waitNetwork(serverName)
			info.setText('Block ' + str(block))
			info.visible(viz.ON)
			yield viztask.waitTime(2)
			info.visible(viz.OFF)
			yield trialSetting_Exp(block, door)
			room_env.remove()
			door.remove()
			Target.alpha(1)
			
		viewLink.reset(viz.RESET_OPERATORS)
		
		yield Practice(block+1, Target)

	info.setText('End of the Experiment.')
	info.visible(viz.ON)
	yield viztask.waitTime(90)
	viz.quit()

viztask.schedule(experiment(side))
