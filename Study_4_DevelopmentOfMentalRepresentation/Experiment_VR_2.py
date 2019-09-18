# import criticla modules
import viz, viztask, vizact, vizinfo, vizproximity, vizshape, viznet, vizinput, winsound
import time, random, os, oculus
import numpy as np
from environments import *

# Initialise window
viz.setMultiSample(8)
viz.go()
viz.mouse.setVisible(False)

# Critical constants
real_tg = 7; real_tg_dist = [0, 0, 7]; vis_tg_dist = 8.5
real_tg_r = 0.02; vis_tg_r = 0.02; vis_tg_r = 0.2 
real_tg_ht = 3; vis_tg_ht = 3
pole_ht = 3; pole_wd = 12; pole_dep = 12; pole_no = 20
groundOffset = pole_dep/2 - (real_tg/2 + vis_tg_dist - real_tg) + vis_tg_dist - real_tg
groundPos = [0, -groundOffset, vis_tg_dist+groundOffset]
polePos = [0, 0, pole_dep+1 ]
offsets = {'L': [-10,0,0], 'R': [10,0,0]}
conditions = {'F': 'flipped', 'C': 'changing', 'S': 'staying'}
tg1Color = viz.ORANGE
tg2Color = [0.18, 0.43, 1]
tg1Colors = [viz.RED, viz.GREEN, viz.YELLOW]
tg2Colors = [viz.CYAN, viz.MAGENTA, [0.65, 0.29, 0.78]]

# Set up the conditions according to the folder name
path = os.getcwd()
folder = path.split(os.path.sep)
folder = folder[-1]
folder = folder.split('_')

id = folder[0] # Subject No
sceneOrder = folder[3] # scene order: F-flipped poles, C-changing poles, S-staying poles
offsetOrder = folder[4] #displacement order: L-leftward, R-rightward
flippedTarget = folder[5] # the target that will be used in the flipped condition: BO - blue, OB - orange

# Set up Oculus Rift
hmd = oculus.Rift()

if hmd.getSensor().getDisplayMode() == oculus.DISPLAY_DESKTOP:
	viz.window.setFullscreen(True)

# set up IPD (this was done by the participant)
# set up eye height (this was done by inputting the number manually)

# Network Setup
serverName = 'srushton-PC'
VRPNhost = 'SimonR-PC'
labNetwork = viz.addNetwork(serverName)

# Set up motion tracking
vrpn = viz.add('vrpn7.dle') 
ori_marker = vrpn.addTracker('Tracker0@'+VRPNhost,9)
ori_marker.swapPos([1,2,-3])
ori_marker.swapQuat([-1,-2,3,4])
pos_marker = vrpn.addTracker('Tracker0@'+VRPNhost,4)

# Setup navigation node and link to main view
view=viz.MainView
viewLink = viz.link(ori_marker, view, mask=viz.LINK_ORI)

def UpdatePos():
	pos=pos_marker.getPosition()
	view.setPosition([pos[0],pos[1]-0.4,-pos[2]], viz.ABS_GLOBAL)
updateView=vizact.ontimer(0,UpdatePos)
		

########################################################################

info = hmd.addMessagePanel(' ', pos=(0,0,3))

info.visible(viz.OFF)

# Setup a sound
metronome=viz.addAudio('Bottle_80.mp3')
metronome.loop(viz.ON)
metronome.volume(1)

alert = viz.addAudio('alert.mp3') # inform participants to stop walking
alert.loop(viz.OFF)
alert.volume(1)

# Set up the targets
Target1 = targetCreator(vis_tg_ht, tg1Color)
Target2 = targetCreator(vis_tg_ht, tg2Color)

def changeColor1(target=Target1):
	lastColor = random.randint(0, 2)
	i = 1
	while True:
		target.color(tg1Colors[lastColor])
		d = yield viztask.waitDraw()
		data = str(i) + ',' + str(lastColor) + ',' + str(d.time)
		sub_rt.write('\n' + data)
		tmp = [0, 1, 2]
		tmp.remove(lastColor)
		lastColor = random.choice(tmp)
		i += 1
		yield viztask.waitTime(0.75)

def changeColor2(target=Target2):
	lastColor = random.randint(0, 2)
	i = 1
	while True:
		target.color(tg2Colors[lastColor])
		d = yield viztask.waitDraw()
		data = str(i) + ',' + str(lastColor) + ',' + str(d.time)
		sub_rt.write('\n' + data)
		tmp = [0, 1, 2]
		tmp.remove(lastColor)
		lastColor = random.choice(tmp)
		i += 1
		yield viztask.waitTime(0.75)

# Record response
def reactTime():
	clicktime=viz.tick()
	sub_rt.write(','+str(clicktime))
vizact.onkeydown('.', reactTime)

# Set up proximity sensors
manager = vizproximity.Manager()
target = vizproximity.Target(view)
manager.addTarget(target)

# Set up the basic scene - ground
ground = groundCreator()
ground.setPosition([0, 0, groundPos[1]])
ground.visible(viz.OFF)
Target1.setParent(ground); 
Target2.setParent(ground); 
Target1.setPosition([0, 0, vis_tg_dist ], viz.ABS_GLOBAL)
Target2.setPosition([0, 0, real_tg - vis_tg_dist], viz.ABS_GLOBAL)

def writePolePos(name, group):
	file =  open(name + '_Poles_' +  str(viz.tick()) +'.csv', 'w')
	for p in group:
		thisPos = str(p.getPosition()).strip('[]')
		file.write(thisPos + '\n')

# Basic procedure Set up
def trials(block_no, isPoles='None', trialNo=10, trialtype = 'Offset', continued = False):
	info.setText("Hurrah!! Please wait for the experimenter.")

	if isPoles in ['flipped', 'staying']:
		poles, polelist = poleCreator(ground, pole_wd, pole_dep, pole_ht, pole_no)
		writePolePos(isPoles, polelist)

	for m in range(trialNo):
		# Set up the response recording file
		global sub_rt

		if continued:
			sub_rt = open('VRrt_' + str(id) + '_Block_' + str(block_no) + '_Trial_' + str(m+9) + '_' + time.strftime("%d-%b-%y_%H-%M") + '.csv', 'a')
		else:
			sub_rt = open('VRrt_' + str(id) + '_Block_' + str(block_no) + '_Trial_' + str(m+1) + '_' + time.strftime("%d-%b-%y_%H-%M") + '.csv', 'a')

		data = 'frameNo,Color,TimeStamp,Response'
		sub_rt.write('\n' + data)

		# Set up the real target sensor area
		sensor_Target = vizproximity.Sensor(vizproximity.RectangleArea([6, 0.1],  center=[0, real_tg_dist[(-1)**(m+1)]]), None)
		manager.addSensor(sensor_Target)
		# Set up poles if they change between trials
		if isPoles == 'changing':
			poles, polelist = poleCreator(ground, pole_wd, pole_dep, pole_ht, pole_no)
			writePolePos(isPoles, polelist)
		elif isPoles == 'flipped':
			poles.setEuler([(90*(1-(-1)**m)), 0, 0], mode = viz.ABS_PARENT)
			poles.setPosition([0, 0, polePos[(-1)**(m)]], mode=viz.ABS_PARENT)

		# Stand by
		yield viztask.waitNetwork(serverName)
		
		# choose target depending on walking direction
		if isPoles == 'flipped':
			if flippedTarget == 'BO':
				if m % 2 == 0:
					Target2.alpha(0)
					Target1.color(tg2Color)
				else:
					Target1.alpha(0)
					Target2.color(tg2Color)
			else:
				if m % 2 == 0:
					Target2.alpha(0)
					Target1.color(tg1Color)
				else:
					Target1.alpha(0)
					Target2.color(tg1Color)
			viz.window.screenCapture('flipped_Image_' + str(m) + '.jpg')
		else:
			if m % 2 == 0:
				Target2.alpha(0)
				Target1.color(tg1Color)
			else:
				Target1.alpha(0)
				Target2.color(tg2Color)
			viz.window.screenCapture(isPoles + '_Image_' + str(m) + '.jpg')
		
		ground.visible(viz.ON)

		labNetwork.send('Ready')
		# Start walking
		yield viztask.waitNetwork(serverName)
		metronome.play()
		
		if isPoles == 'flipped':
			if flippedTarget == 'BO':
				if m % 2 == 0:
					colorChange = viztask.schedule(changeColor2(Target1))
				else:
					colorChange = viztask.schedule(changeColor2())
			else:
				if m % 2 == 0:
					colorChange = viztask.schedule(changeColor1())
				else:
					colorChange = viztask.schedule(changeColor1(Target2))
		else:
			if m % 2 == 0:
				colorChange = viztask.schedule(changeColor1())
			else:
				colorChange = viztask.schedule(changeColor2())

		labNetwork.send('Block' + str(block_no) + ' Trial ' + str(m))

		yield viztask.waitTime(0.25)

		# reach the target
		yield vizproximity.waitEnter(sensor_Target)
		alert.play()
		metronome.stop()
		viz.clearcolor(viz.BLACK)
		ground.visible(viz.OFF)
		colorChange.kill()
		labNetwork.send('Reach Target!')

		manager.clearSensors()
		print Target1.getPosition(viz.ABS_GLOBAL)
		print Target2.getPosition(viz.ABS_GLOBAL)
		# Set up the information for participants at the end of trial
		if m < trialNo-1:
			info.visible(viz.ON)
			yield viztask.waitTime(3)
			info.visible(viz.OFF)
			if isPoles == 'changing':
				poles.remove()
		else:
			# finish writing the response
			info.setText('End of Block ' + str(block_no))
			info.visible(viz.ON)
			yield viztask.waitTime(3)
			info.visible(viz.OFF)
			if isPoles != 'None':
				poles.remove()

		# reset the targets
		if m % 2 == 0:
			Target2.alpha(1)
		else:
			Target1.alpha(1)

# Set up baseline conditions
def baseline(block_no, trialNo = 6):
	yield viztask.waitNetwork(serverName)
	info.setText('Block ' + str(block_no))
	info.visible(viz.ON)
	yield viztask.waitTime(2)
	info.visible(viz.OFF)

	yield trials(block_no, 'None', trialNo, 'baseline')

# Set up testing conditions
def testing():
	for i in range(1, 6, 2):
		block_no = i + 1
		currCondition = sceneOrder[block_no/2 - 1]
		currOffset = offsetOrder[block_no/2 - 1]

		# start the first part of the block - first 8 trials without offset
		yield viztask.waitNetwork(serverName)
		info.setText('Block' + str(block_no))
		info.visible(viz.ON)
		yield viztask.waitTime(2)
		info.visible(viz.OFF)
		yield trials(block_no, conditions[currCondition], 8, 'baseline')

		# start the second part of the block - last 2 trials with offset

		viewLink.preEuler(offsets[currOffset], target = viz.LINK_ORI_OP)

		yield trials(block_no, conditions[currCondition], 2, True)

		# remove offset
		viewLink.reset(viz.RESET_OPERATORS)

		yield baseline(block_no + 1)

# Set up the whole procedure
def experiment():
	yield viztask.waitNetwork(serverName)
	# the first baseline
	yield baseline(1)

	# following offset and baseline conditions
	yield testing()
	# finish the experiment
	info.setText('End of the Experiment.')
	info.visible(viz.ON)
	yield viztask.waitTime(45)
	viz.quit()

viztask.schedule(experiment())	