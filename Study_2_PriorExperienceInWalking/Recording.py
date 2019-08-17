import viz, viztask, vizact, vizproximity, winsound, vizshape, vizinput, time

real_tg_dist = (0, 6.5, 0.5)

viz.go()

view=viz.MainView
view.setPosition([0,10,3.5]); view.setEuler(45,90,0)
subject_no=vizinput.input('Subject_no: ')

serverName = 'srushton-PC'
labNetwork = viz.addNetwork(serverName)

# Setup VRPN
vrpn = viz.add('vrpn7.dle')
head = vrpn.addTracker('Tracker0@localhost', 9)
body = vrpn.addTracker('Tracker0@localhost', 10)
tracker = vrpn.addTracker('Tracker0@localhost', 4)
head.swapPos([1,2,-3])
head.swapQuat([-1, -2, 3, 4])
body.swapPos([1,2,-3])
body.swapQuat([-1, -2, 3, 4])

ground=viz.add('ground.osgb')
target_1=vizshape.addCylinder(height=3, radius=0.02); target_1.color(viz.RED); target_1.setPosition([0, 0, 0])
target_2=vizshape.addCylinder(height=3, radius=0.02); target_2.color(viz.RED); target_2.setPosition([0, 0, 7])
head_rep=vizshape.addBox([0.2,0.2,0.2]); head_rep.color(viz.PURPLE)
body_rep=vizshape.addBox([0.2,0.2,0.2]); body_rep.color(viz.YELLOW_ORANGE)
headlink=viz.link(head, head_rep)
bodylink=viz.link(body, body_rep)

manager = vizproximity.Manager()

target = vizproximity.Target(headlink)
manager.addTarget(target)

def writing(trialNo):
	record = open('PBpath_P' + subject_no + '_Trial_' + str(trialNo) + time.strftime('_%Y-%m-%d_%H-%M-%S') + '.csv', 'a')     #time.strftime('-%Y-%m-%d_%H-%M-%S')
	FrameNo=1 
	data= 'FrameNo, TimeStamp, Head_x, Head_y, Head_z, Head_yaw, Head_pitch, Head_roll, Body_x, Body_y, Body_z, Body_yaw, Body_pitch, Body_roll, Head2_x, Head2_y, Head2_z'
	record.write(data + '\n')
	
	while True:
		data=[]
		data=str(FrameNo) + ',' + str(viz.tick()) + ','+str(head.getPosition()).strip('[]')+','+str(head.getEuler()).strip('[]')+','+str(body.getPosition()).strip('[]')+','+str(body.getEuler()).strip('[]')+','+str(tracker.getPosition()).strip('[]')
		FrameNo+=1
		record.write(data + '\n')
		yield viztask.waitTime(1/120)

def experiment():
    for trial in range(10):
        sensor_Target = vizproximity.Sensor(vizproximity.RectangleArea([4, 0.1],  center=[0, real_tg_dist[(-1)**trial]]), None)
        manager.addSensor(sensor_Target)

        yield viztask.waitNetwork(serverName)
        record=viztask.schedule(writing(trial)); 
        yield viztask.waitTime(0.5)
       
        yield vizproximity.waitEnter(sensor_Target)
        winsound.Beep(800,1000) # Make a sound to notify the participant that he/she has reached the target.
        record.kill()
        manager.clearSensors()
        
viztask.schedule(experiment())
        