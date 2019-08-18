import viz
import vizshape
import vizmat
import vizfx
import vizproximity
import numpy as np
import math

def room(high, wide, dep):
	room=viz.addGroup()
	wall_positions=(([wide/2, 0, dep/2], [wide/2, 0, (-dep/2)], [wide/2, high, (-dep/2)], [wide/2, high, dep/2]),
							([wide/2, 0, (-dep/2)], [-wide/2, 0, (-dep/2)], [-wide/2, high, (-dep/2)], [wide/2, high, (-dep/2)]),
							([-wide/2,0, (-dep/2)], [-wide/2, 0, dep/2], [-wide/2, high, dep/2], [-wide/2, high, (-dep/2)]),
							([-wide/2,0, dep/2], [wide/2, 0, dep/2], [wide/2, high, dep/2], [-wide/2, high, dep/2]),
							([wide/2, high, dep/2], [wide/2, high, (-dep/2)], [-wide/2, high, (-dep/2)], [-wide/2, high, dep/2]),
							([100, 0, -100], [100, 0, 100], [-100, 0, 100], [-100, 0, -100]))
	coord=([0,0], [1,0], [1,1], [0,1])

	WallScale_small = [1,.25,1]
	WallScale_large = [1,.25,1]
	AreaScale = [1,1,1]
	AreaScale_f = [16, 16 ,1]

	matrix_s = vizmat.Transform()
	matrix_s.setScale(WallScale_small)

	matrix_l = vizmat.Transform()
	matrix_l.setScale(WallScale_large)

	matrix_area_f = vizmat.Transform()
	matrix_area_f.setScale(AreaScale_f)
	
	matrix_area = vizmat.Transform()
	matrix_area.setScale(AreaScale)

	wallTex = viz.addTexture('wallTex.jpg')
	wallTex.wrap(viz.WRAP_T,viz.REPEAT)
	wallTex.wrap(viz.WRAP_S,viz.REPEAT)
	
	wallTex_darker = viz.addTexture('wallTex_Dark.jpg')
	wallTex_darker.wrap(viz.WRAP_T, viz.REPEAT)
	wallTex_darker.wrap(viz.WRAP_S, viz.REPEAT)
	
	wallTex_bright = viz.addTexture('wallTex_Brightened.jpg')
	wallTex_bright.wrap(viz.WRAP_T, viz.REPEAT)
	wallTex_bright.wrap(viz.WRAP_S, viz.REPEAT)

	for i in range(6):
		viz.startLayer(viz.QUADS)
		for j in range(4):
			viz.texCoord(coord[j])
			viz.vertex(wall_positions[i][j])
		wall=viz.endLayer()

		if i<4:
			if i%2:
				wall.texmat(matrix_s)
			else:
				wall.texmat(matrix_l)

			if i==3:
				wall.texture(wallTex_bright)
			else:
				wall.texture(wallTex)

		else:
			if i==5:
				wall.texmat(matrix_area_f)
			else:
				wall.texmat(matrix_area)

			wall.texture(wallTex_darker)

		wall.setParent(room)

	return room

def GroundCreator(node):
	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(100, 0, -100)
	viz.texCoord(1,0) 
	viz.vertex(100, 0, 100)
	viz.texCoord(1,1) 
	viz.vertex(-100, 0, 100)
	viz.texCoord(0,1)  
	viz.vertex(-100, 0, -100)
	Floor = viz.endLayer()

	AreaScale_f = [16, 16 ,1]

	matrix_area_f = vizmat.Transform()
	matrix_area_f.setScale(AreaScale_f)
	
	Floor.texmat(matrix_area_f)

	wallTex = viz.addTexture('wallTex.jpg')
	wallTex.wrap(viz.WRAP_T,viz.REPEAT)
	wallTex.wrap(viz.WRAP_S,viz.REPEAT)

	Floor.texture(wallTex)
	Floor.setParent(node)
	return Floor

def diskCreator(node):
	disks = viz.addGroup()

	#Generate random values for position and orientation
	disk_rad=0.5; space_width=80; disk_number=np.int_( np.floor(0.2*(space_width*space_width)/(4*disk_rad))); al_valu = 0.55; segment_no = 36
	
	viz.startLayer(viz.POLYGON)
	viz.pointSize(1)
	for i in range(segment_no):
		pt_z = disk_rad * math.cos(2*math.pi*i/segment_no)
		pt_x = disk_rad * math.sin(2*math.pi*i/segment_no)
		viz.vertex([pt_x, 0, pt_z])
	disk = viz.endLayer()

	a = np.arange(2*disk_rad, space_width-2*disk_rad, 4*disk_rad)
	x = np.repeat(a, len(a)) - space_width/2 
	z = np.tile(a, len(a)) - disk_rad
	pool = np.vstack((x, z))
	pool = np.transpose(pool)
	ind = np.random.choice(len(pool), disk_number, replace=False)
	noise = np.random.uniform(-disk_rad, disk_rad, (disk_number, 2))
	positions = pool[ind,:] + noise
	
	#disk=vizfx.addChild('disk.osgb')

	for i in range(disk_number):
		#Load a disk
		if i < disk_number/5:
			d = disk.copy(); d.color(0, 0, 0.5); d.alpha(al_valu) #Blue
		elif disk_number/5 <= i < 2*disk_number/5:
			d = disk.copy(); d.color(0.55, 0, 0); d.alpha(al_valu) #Red
		elif 2*disk_number/5 <= i < 3*disk_number/5:
			d = disk.copy(); d.color(1, 0.84, 0); d.alpha(al_valu) #Yellow
		elif 3*disk_number/5 <= i <4*disk_number/5:
			d = disk.copy(); d.color(0, 0.5, 0); d.alpha(al_valu) #Green
		elif 4*disk_number/5 <= i < disk_number:
			d = disk.copy(); d.color(0.5, 0, 0.5); d.alpha(al_valu) #Purple

		#Set position, orientation, and state
		d.setPosition([positions[i, 0],0,positions[i, 1]])
		d.zoffset(-1)
		d.setParent(disks)

	disk.remove()

	disks.setParent(node)
	return disks

def TargetCreator(high, rad):
	global Target
	Target = vizshape.addCylinder(height = high, radius=rad, yAlign=vizshape.ALIGN_MIN) #Change the diameter of the target
	return Target