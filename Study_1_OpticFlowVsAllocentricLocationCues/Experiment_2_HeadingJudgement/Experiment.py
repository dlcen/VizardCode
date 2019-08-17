import viz, viztask, vizact, vizinfo, vizproximity, vizshape, vizinput
import time, random, os
import numpy as np
from Environments import *
import Staircases as ST
import oculus

# Initialize window
viz.setMultiSample(8)
viz.go()
viz.mouse.setVisible(False)
#Disable mouse navigation
viz.mouse(viz.OFF)

# Participant information
path=os.getcwd() # Information contained in the folder title
folder=path.split('\\')
folder=folder[-1]
folder=folder.split('_')

sub_id=folder[0] # Subject No.
Sequence=folder[1] # Environment Sequence
global distance, freq, ipd, height, cloudFreq
distance=7
freq=37
cloudFreq = 5250
SPEED = 1

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

# # Apply user profile eye height to view
profile = hmd.getProfile()
if profile:
	height = profile.eyeHeight - 0.1
else:
	height = float(viz.input('Height?'))

# Set up the instruction
beforeExp = """That's the practice. 
Ready for the experiment?
"""
ReqResp = 'Left or Right?'
# GotResp = 'Next Trial'

# Set up the target
Target = vizshape.addCylinder(height = 3, radius=0.02, yAlign=vizshape.ALIGN_MIN)
Target.color(viz.ORANGE)
Target.visible(viz.OFF)

# Set up view movement
view = viz.MainView
sensor = hmd.getSensor()
link = viz.link(hmd.getSensor(), view, mask=viz.LINK_ORI)
vizact.onkeydown('r', sensor.reset)
view.eyeheight(height)
MODE = viz.SPEED
ROTATE_MODE = viz.NO_ROTATE

# Set up the cross at the centre of the visual field
def cross(eyeHeight):
	viz.startLayer(viz.LINES)  
	viz.lineWidth(2)
	viz.vertex(-0.25,0+eyeHeight,5) #Vertices are split into pairs. 
	viz.vertex(0.25,0+eyeHeight,5) 
	viz.vertex(0,-0.25+eyeHeight,5) 
	viz.vertex(0,0.25+eyeHeight,5) 
	myCross = viz.endLayer() 
	return myCross
Cross = cross(height)
Cross.visible(viz.OFF)

def AnimateView(orientation):
	offset = distance * np.tan(np.radians(orientation))
	action = vizact.goto([offset, height, distance], SPEED, MODE)
	view.runAction(action)

# Refreshing dots
def refreshing(clouds):
	index=0
  	while True: 
		clouds[index].remove()
		pos=np.random.uniform(low=-6, high=6, size=(cloudFreq/freq,3))
		pos[:,1]=pos[:,1]/2
		pos[:,2]=pos[:,2] -5
		viz.startLayer(viz.POINTS)
		viz.pointSize(2)
		for n in range(cloudFreq/freq):		
			viz.vertex(pos[n,0], pos[n,1], pos[n,2])
		single_cloud=viz.endLayer()
		single_cloud.disable(viz.CULLING)
		single_cloud.setParent(Target)
		clouds.append(single_cloud)
		index+=1
		yield viztask.waitDraw()

# Define a function to recording the head orientation during the trial
def recording(record, scene, condition, stimuli, trialNo):
	while True:
		data = str(scene) + ',' + str(condition) + ',' + str(stimuli) + ',' + str(trialNo) + ',' + str(viz.tick()) + ',' + str(view.getPosition()).strip('[]') + ',' + str(view.getEuler()).strip('[]') + '\n'
		record.write(data)
		yield viztask.waitTime(1/75)

# Set up a calibration at the beginning of each trial
manager_cali = vizproximity.Manager()
# First create a transparent ball 
eyepatch = viz.addTexQuad(parent=viz.HEAD,color = viz.CYAN, size=1)
eyepatch.setPosition([0, 0, 5], viz.ABS_PARENT)
eyepatch.alpha(0.5)
eyepatch.visible(viz.OFF)
# Set up sensor
sensor = vizproximity.Sensor(vizproximity.Box(size = [0.4, 0.4, 2]), source = Cross)
# Set up target
target_cali = vizproximity.Target(eyepatch)
# Add sensor and target
manager_cali.addSensor(sensor)
manager_cali.addTarget(target_cali)

# Set up the information panel
info = hmd.addMessagePanel('', pos=(0,0,3))
info.visible(viz.OFF)

# Set up the staircase
# Multiple staircases
exp_conditions=[
				{'label':'Very Close', 'name': 'Close', 'startVal': 5},
                {'label':'Close', 'name': 'Close', 'startVal': 5},
                {'label':'Middle', 'name': 'Middle', 'startVal': 5},
                {'label':'Far', 'name': 'Far', 'startVal': 5},
                ] 

def trial(name, conditions, nTrials=23, feedback=False, withSimple=True):
	stairs = ST.MultiStairs(conditions=conditions, nTrials=nTrials, withSimple=withSimple)
	TrialNo = 0
	data = 'Scene, Condition, Stimuli, TrialNo, TimeStamp, Head_x, Head_y, Head_z, Head_yaw, Head_pitch, Head_roll\n'
	headfile = open('HeadData_' + str(sub_id) + '_' + str(name) + '_' + time.strftime("%d-%b-%y_%H-%M") + '.csv', 'a')
	headfile.write(data)

	for thisStimuli, thisCondition in stairs:
		TrialNo += 1
		# set the orientation
		currStim = thisStimuli

		if currStim < 0:
			oriDirection = 'Left'
			correctKey = viz.KEY_LEFT
		else:
			oriDirection = 'Right'
			correctKey = viz.KEY_RIGHT
			print thisStimuli
			
		if thisCondition['label'] == 'Very Close':
			distance = 7
			
		elif thisCondition['label'] == 'Close':
			distance = 6
			
		elif thisCondition['label'] == 'Middle':
			distance = 5
			
		elif thisCondition['label'] == 'Far':
			distance = 3
			
		else: # this is the duration for the catch trials, don't make it too short!
			distance = 3.5
			

		runningTime = 0.75
		
		# Show the cross
		eyepatch.visible(viz.ON)
		Cross.visible(viz.ON)
		yield viztask.waitTime(1.5)
		Cross.visible(viz.OFF)
		eyepatch.visible(viz.OFF)
		waittime = random.uniform(0.5, 0.75)
		yield viztask.waitTime(waittime)
		# Show the environment
		Target.setPosition([0, 0, distance], viz.ABS_GLOBAL)
		Target.visible(viz.ON)
		# Show "Start"
		waittime = random.uniform(0.25, 0.75)
		yield viztask.waitTime(waittime)
		record = viztask.schedule(recording(headfile, name, thisCondition['label'], thisStimuli, TrialNo))
		AnimateView(currStim)
		
		yield viztask.waitTime(runningTime)
		Target.visible(viz.OFF)
		iniTime = viz.tick()
		view.endAction()
		view.reset(viz.HEAD_POS)

		# get the response
		thisResp = None
		respTime = None
		
		d = yield viztask.waitKeyDown((viz.KEY_RIGHT, 'q', 'escape', viz.KEY_LEFT))
		record.kill()
		
		if thisResp is None:
			thisKey = d.key
			if thisKey == correctKey:
				thisResp = 1
				if feedback:
					info.setText('Correct. Well done!')
					info.visible(viz.ON); yield viztask.waitTime(1); info.visible(viz.OFF)
			else:
				thisResp = 0
				if feedback:
					info.setText('Not correct. Try it again.')
					info.visible(viz.ON); yield viztask.waitTime(1); info.visible(viz.OFF)
			# get the response time
			respTime = d.time - iniTime
		if currStim == 0:
			thisResp = 0

		stairs.addResponse(thisResp)
		stairs.addOtherData('Response Time', respTime)
		stairs.addOtherData('Actual Trial No', TrialNo)
		
		waittime=random.uniform(0.5, 0.75)
		yield viztask.waitTime(waittime)
	
	stairs.saveAsExcel(str(sub_id) + '_' + str(name) + '_' + time.strftime("%d-%b-%y_%H-%M"))

def practice():
	info.setText('Practice Session')
	info.visible(viz.ON)
	yield viztask.waitTime(2)
	info.visible(viz.OFF)

	practice_conditions = [{'label':'Far','startVal': 5}, {'label':'Middle','startVal': -5}, {'label':'Close','startVal': -5}, {'label':'Very Close','startVal': -5}]
	
	ground=GroundCreator()
	ground.setParent(Target)

	yield trial('Practice', practice_conditions, nTrials=1, feedback=True, withSimple=False)
	
	ground.remove()

def main():
	# Set up the instruction
	info.setText('Let the experimenter know if you are ready.')
	info.visible(viz.ON)
	yield viztask.waitKeyDown(' ')
	info.visible(viz.OFF)
	yield viztask.waitTime(1)
	yield practice()

	info.setText(beforeExp)
	info.visible(viz.ON)
	yield viztask.waitKeyDown(' ')
	info.visible(viz.OFF)

	for i in range(len(Sequence)):

		if i>0:
			info.setText('End of Block ' + str(i) + '. \nWould you like to continue?')
			info.visible(viz.ON)
			yield viztask.waitKeyDown(' ')
			
		info.setText('Block ' + str(i+1))
		info.visible(viz.ON)
		yield viztask.waitTime(2)
		info.visible(viz.OFF)
		yield viztask.waitTime(1)
		
		if Sequence[i]=='C' or Sequence[i]=='c':
			condName = 'DotCloud'
			clouds=flashingCloud(3, 12, 12, 1, cloudFreq, Target,freq)
			refresh=viztask.schedule(refreshing(clouds))
			yield trial(condName, exp_conditions)
			for c in clouds:
				c.remove()
			refresh.kill()

		elif Sequence[i]=='L' or Sequence[i]=='l':
			condName = 'Line'
			yield trial(condName, exp_conditions)

		elif Sequence[i]=='O' or Sequence[i]=='o':
			condName = 'OutlinedRoom'
			Target.alpha(0)
			door=door_line(2.5, 0.5, 2)
			door.setParent(Target)
			door.zoffset(-1)
			door.color(viz.ORANGE)
			outlineRoom=room_line(3, 12, 12, 2)
			outlineRoom.setParent(Target)
			yield trial(condName, exp_conditions)
			door.remove(); outlineRoom.remove()
			Target.alpha(1)

		elif Sequence[i]=='F' or Sequence[i]=='f':
			condName = 'EmptyRoom'
			Target.alpha(0)
			door=doorway(2.5, 0.5, 0.025)
			door.setParent(Target)
			door.zoffset(-1)
			door.color(viz.ORANGE)
			room_env=RoomCreator(12, 12, 3, 1)
			room_env.setParent(Target)
			room_env.setPosition([0,0,-11], viz.REL_PARENT)
			yield trial(condName, exp_conditions)
			room_env.remove()
			door.remove()
			Target.alpha(1)

	info.setText('Thank you!')
	info.visible(viz.ON)
	yield viztask.waitTime(2)

	viz.quit()

viztask.schedule(main)




