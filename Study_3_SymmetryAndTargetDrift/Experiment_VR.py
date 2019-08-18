import viz, viztask, vizact, vizinfo, vizproximity, vizshape, viznet, vizinput
import time, random
import numpy as np
from Environments import *
import os
import oculus

# Initialize window
viz.setMultiSample(8)
viz.go() # It's position is very important
viz.mouse.setVisible(False)

# Critical Values
ipd=70
p_height = 1.80
real_tg = 7; real_tg_dist = [0, 0, 7]; vis_tg_dist_near = 8.5; vis_tg_dist_far = 85
real_tg_r = 0.02; vis_tg_r = 0.02; vis_tg_r_far = 0.2 
real_tg_ht = 3; vis_tg_ht_near = 3; vis_tg_ht_far = (real_tg_ht - p_height) * vis_tg_dist_far/real_tg
room_ht = 3; room_wd = 12; room_dep = 12

path=os.getcwd()
folder=path.split('\\')
folder=folder[-1]
folder=folder.split('_')

# Read condition information from the folder name
id=folder[0]
Exp_Sequence=folder[4]
Room_Sequence = folder[5]
Room_OffsetOrder = folder[6]
Distance_Sequence = folder[7]
Distance_OffsetOrder = folder[8]

sub_ipd=ipd/1000

# Setup Oculus Rift HMD
hmd = oculus.Rift() #renderMode=oculus.RENDER_CLIENT)

if hmd.getSensor().getDisplayMode() == oculus.DISPLAY_DESKTOP:
	viz.window.setFullscreen(True)

hmd.setIPD(sub_ipd)

# Network Setup
VRPNserver = 'SimonR-PC'
serverName = 'srushton-PC'
myNetwork = viz.addNetwork(serverName)

# Set up Tracking 
vrpn = viz.add('vrpn7.dle') 
ori_marker = vrpn.addTracker('Tracker0@' + VRPNserver,9)
ori_marker.swapPos([1,2,-3])
ori_marker.swapQuat([-1,-2,3,4])
pos_marker = vrpn.addTracker('Tracker0@' + VRPNserver,4)

# Setup navigation node and link to main view
view=viz.MainView
viewLink = viz.link(ori_marker, view, mask=viz.LINK_ORI)

def UpdatePos():
	pos=pos_marker.getPosition()
	view.setPosition([pos[0],pos[1]-0.2,-pos[2]], viz.ABS_GLOBAL)
updateView=vizact.ontimer(0,UpdatePos)


########################################################################################################

info = hmd.addMessagePanel(' ', pos=(0,0,3))

info.visible(viz.OFF)

# Setup a sound
sound=viz.addAudio('Bottle_80.mp3') # The metronome.
sound.loop(viz.ON)
sound.volume(1)

alert = viz.addAudio('alert.mp3') # An alert to notify the participant to stop.
alert.loop(viz.OFF)
alert.volume(1)

# Set up a file to record the response to the changes of target LED colour
sub_rt = open('VRrt_' + id + '_' + Exp_Sequence + '_' + Room_Sequence + '_' + Room_OffsetOrder + '_' + Distance_Sequence + '_' + Distance_OffsetOrder + '_' + time.strftime("%d-%b-%y_%H-%M") + '.csv', 'a')
		
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

manager = vizproximity.Manager()

target = vizproximity.Target(view)
manager.addTarget(target)

# Experiment Set up
def trials(block_no, vis_dist, isDisks=False):
	info.setText("Hurrah!! Please wait for the experimenter.")
	for m in range(4):
		vis_pos = [0, real_tg - vis_dist, vis_dist]
		sensor_Target = vizproximity.Sensor(vizproximity.RectangleArea([6, 0.1],  center=[0, real_tg_dist[(-1)**(m+1)]]), None)
		manager.addSensor(sensor_Target)

		if isDisks:
			disks.remove()
			global disks
			disks = diskCreator(vis_tg)
			disks.setPosition([0, 0, -vis_dist])

		yield viztask.waitNetwork(serverName)
		sub_rt.write('\nBlock ' + str(block_no) + ' Trial '+ str(m+1))
		vis_tg.color(viz.ORANGE)
		vis_tg.visible(viz.ON)
		myNetwork.send('Ready')
		yield viztask.waitNetwork(serverName)
		sound.play()
		myNetwork.send('Block ' + str(block_no) + ' Trial ' + str(m+1))
		colorChange=viztask.schedule(changeColor(vis_tg))
				
		yield vizproximity.waitEnter(sensor_Target)
		alert.play()
		print str(block_no) + ' ' + str(m+1) + ' ' + str(view.getPosition()) + ' ' + str(vis_tg.getPosition())
		vis_tg.visible(viz.OFF)
		sound.stop()
		colorChange.kill()
		myNetwork.send('Reach Target!')
			
		ori = (1+(-1)**m)*90;
		vistg_p = vis_tg.getPosition()
		vis_tg.setPosition(vistg_p[0], vistg_p[1], vis_pos[(-1)**m], mode = viz.ABS_PARENT)
		vis_tg.setEuler([ori,0,0],mode=viz.REL_LOCAL)
		
		manager.clearSensors()
		
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
			if isDisks:
				disks.remove()

def Baseline(block_no):
	global vis_tg
	vis_tg = TargetCreator(vis_tg_ht_near, vis_tg_r)
	vis_tg.setPosition([0, 0, vis_tg_dist_near])
	vis_tg.visible(viz.OFF)
	ground=GroundCreator(vis_tg)

	yield viztask.waitNetwork(serverName)
	info.setText('Block ' + str(block_no))
	info.visible(viz.ON)
	yield viztask.waitTime(2)
	info.visible(viz.OFF)
	yield trials(block_no, vis_tg_dist_near)
	ground.remove()
	vis_tg.remove()

def Direction_Exp(offset): #offset = 1 or 3

	for i in range(len(Room_Sequence)):
		block=(i+offset)*2

		if Room_OffsetOrder =='LR':
			if i%2==0:
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)
			else:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
		else:
			if i%2==0:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
			else:    
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)

		global vis_tg
		vis_tg = TargetCreator(vis_tg_ht_near, vis_tg_r)
		vis_tg.setPosition([0, 0, vis_tg_dist_near])
		vis_tg.visible(viz.OFF)
		room_env=room(room_ht, room_wd, room_dep)
		room_env.setParent(vis_tg)

		if Room_Sequence[i]=='C' or Room_Sequence[i]=='c':
			room_direction = [45, 0, 0]
			
		elif Room_Sequence[i]=='M' or Room_Sequence[i]=='m':
			room_direction = [22.5, 0, 0]

		elif Room_Sequence[i]=='F' or Room_Sequence[i]=='f':
			room_direction = [0, 0, 0]

		room_env.setEuler(room_direction, viz.ABS_PARENT)
		room_env.setPosition(0, 0, - 0.5*room_wd/np.cos(np.radians(room_direction[0])), viz.REL_PARENT)
			
		yield viztask.waitNetwork(serverName)
		info.setText('Block ' + str(block))
		info.visible(viz.ON)
		yield viztask.waitTime(2)
		info.visible(viz.OFF)
		yield trials(block, vis_tg_dist_near)

		room_env.remove()
		vis_tg.remove()

		viewLink.reset(viz.RESET_OPERATORS)

		yield Baseline(block+1)


def Distance_Exp(offset): #offset = 1 or 4

	for i in range(len(Distance_Sequence)):
		block=(i+offset)*2

		if Distance_OffsetOrder =='LR':
			if i%2==0:
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)
			else:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
		else:
			if i%2==0:
				viewLink.preEuler([10,0,0], target=viz.LINK_ORI_OP)
			else:    
				viewLink.preEuler([-10,0,0], target=viz.LINK_ORI_OP)

		global vis_tg
		if Distance_Sequence[i] == 'F' or Distance_Sequence[i] == 'f':
			vis_tg = TargetCreator(vis_tg_ht_far, vis_tg_r_far)
			vis_tg_dist = vis_tg_dist_far
		else:
			vis_tg = TargetCreator(vis_tg_ht_near, vis_tg_r)
			vis_tg_dist = vis_tg_dist_near

		vis_tg.visible(viz.OFF)
		vis_tg.setPosition([0, 0, vis_tg_dist])

		global ground
		ground = GroundCreator(vis_tg)

		global disks
		disks = diskCreator(vis_tg)
		disks.setPosition([0, 0, -vis_tg_dist])

		yield viztask.waitNetwork(serverName)
		info.setText('Block ' + str(block))
		info.visible(viz.ON)
		yield viztask.waitTime(2)
		info.visible(viz.OFF)
		yield trials(block, vis_tg_dist, isDisks=True)

		ground.remove()
		if disks in globals():
			disks.remove()
		vis_tg.remove()

		viewLink.reset(viz.RESET_OPERATORS)

		yield Baseline(block+1)


def experiment():
	yield viztask.waitNetwork(serverName)
	
	yield Baseline(1)
	
	if Exp_Sequence == 'RP':
		yield Direction_Exp(1)
		yield Distance_Exp(4)
	else:
		yield Distance_Exp(1)
		yield Direction_Exp(3)

	info.setText('End of the Experiment.')
	info.visible(viz.ON)
	yield viztask.waitTime(60)
	viz.quit()

viztask.schedule(experiment())
