import viz
import vizshape
import vizmat
import numpy as np 

def doorway(height, width, radius):
	doorway=viz.addGroup()

	cylinder1 = vizshape.addCylinder(height=height+radius*2-0.01, radius=radius)
	cylinder2 = vizshape.addCylinder(height=height+radius*2-0.01, radius=radius)
	cylinder3 = vizshape.addCylinder(height=width, radius=radius, axis=vizshape.AXIS_X)
	cylinder4 = vizshape.addCylinder(height=width, radius=radius, axis=vizshape.AXIS_X)

	cylinder1.setParent(doorway)
	cylinder2.setParent(doorway)
	cylinder3.setParent(doorway)
	cylinder4.setParent(doorway)
	
	cylinder1.setPosition([-width/2, height/2, 0], mode=viz.REL_PARENT)
	cylinder2.setPosition([width/2, height/2, 0], mode=viz.REL_PARENT)
	cylinder3.setPosition([0,height,0], mode=viz.REL_PARENT)
	cylinder4.setPosition([0,0,0],mode=viz.REL_PARENT)

	return doorway

def flashingCloud(height, width, depth, offset, number, node, frequence):
	positions=np.random.uniform(low=-width/2, high=width/2, size=(number,3))
	positions[:,1]=positions[:,1]/(width/height) + height/2
	positions[:,2]=positions[:,2]-(depth/2-offset)

	clouds=[]

	for j in range(frequence):
		viz.startLayer(viz.POINTS)
		viz.pointSize(2)#Set the size of the points.
		bin=number/frequence
		for i in range(bin):		
			viz.vertex(positions[j*bin+i,0], positions[j*bin+i,1], positions[j*bin+i,2])
		single_cloud=viz.endLayer()
		clouds.append(single_cloud)
		clouds[-1].setParent(node)

	return clouds

def room_line(high, wide, dep, pixel):
	room=viz.addGroup()

	pos=np.array([[[wide/2, 0, 0], [wide/2, high, 0]],
		 	 [[-wide/2, 0, 0], [-wide/2, high, 0]],
		 	 [[wide/2, 0, 0], [-wide/2, 0, 0]],
		 	 [[wide/2, high,0], [-wide/2, high, 0]],

		 	 [[wide/2, 0, -dep], [wide/2, high, -dep]],
		 	 [[-wide/2, 0, -dep], [-wide/2, high, -dep]],
		 	 [[wide/2, 0, -dep], [-wide/2, 0, -dep]],
		 	 [[wide/2, high, -dep], [-wide/2, high, -dep]],

		 	 [[wide/2, 0, 0], [wide/2, 0, -dep]],
		 	 [[wide/2, high, 0], [wide/2, high, -dep]],
		 	 [[-wide/2, 0, 0], [-wide/2, 0, -dep]],
		 	 [[-wide/2, high, 0], [-wide/2, high, -dep]]])


	for i in range(12):
		viz.startLayer(viz.LINES)
		viz.lineWidth(pixel)
		viz.vertexColor(1,0,0)
		viz.vertex(pos[i,0,:].tolist())
		viz.vertex(pos[i,1,:].tolist())
		outline=viz.endLayer()
		outline.setParent(room)

	return room

def RoomCreator(length, width, height,offset):
	Room=viz.addGroup(); room=[]
	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(width/2, 0, -offset)
	viz.texCoord(1,0) 
	viz.vertex(width/2, 0, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(width/2, height, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(width/2, height, -offset)
	Wall_01 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(width/2, 0, (length-offset))
	viz.texCoord(1,0) 
	viz.vertex(0.25, 0, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(0.25, height, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(width/2, height, (length-offset))
	Wall_02_1 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(0.25, 2.5, (length-offset))
	viz.texCoord(1,0) 
	viz.vertex(-0.25, 2.5, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(-0.25, height, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(0.25, height, (length-offset))
	Wall_02_2 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(-0.25, 0, (length-offset))
	viz.texCoord(1,0) 
	viz.vertex(-width/2, 0, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(-width/2, height, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(-0.25, height, (length-offset))
	Wall_02_3 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(-width/2, 0, (length-offset))
	viz.texCoord(1,0) 
	viz.vertex(-width/2, 0, -offset)
	viz.texCoord(1,1) 
	viz.vertex(-width/2, height, -offset)
	viz.texCoord(0,1)  
	viz.vertex(-width/2, height, (length-offset))
	Wall_03 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(-width/2, 0, -offset)
	viz.texCoord(1,0) 
	viz.vertex(width/2, 0, -offset)
	viz.texCoord(1,1) 
	viz.vertex(width/2, height, -offset)
	viz.texCoord(0,1)  
	viz.vertex(-width/2, height, -offset)
	Wall_04 = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(width/2, 0, -offset)
	viz.texCoord(1,0) 
	viz.vertex(width/2, 0, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(-width/2, 0, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(-width/2, 0, -offset)
	Floor = viz.endLayer()

	viz.startLayer(viz.QUADS)
	viz.texCoord(0,0) 
	viz.vertex(width/2, height, -offset)
	viz.texCoord(1,0) 
	viz.vertex(width/2, height, (length-offset))
	viz.texCoord(1,1) 
	viz.vertex(-width/2, height, (length-offset))
	viz.texCoord(0,1)  
	viz.vertex(-width/2, height, -offset)
	Ceiling = viz.endLayer()

	WallScale_small = [1,.25,1]
	WallScale_large = [1,.25,1]
	WallScale_w2l = [.5,.25,1]
	AreaScale = [1,1,1]

	matrix_s = vizmat.Transform()
	matrix_s.setScale(WallScale_small)

	matrix_l = vizmat.Transform()
	matrix_l.setScale(WallScale_large)

	matrix_w2l = vizmat.Transform()
	matrix_w2l.setScale(WallScale_w2l)

	matrix_w2s = vizmat.Transform()
	matrix_w2s.setScale([0.04,0.04,1])
	
	matrix_area = vizmat.Transform()
	matrix_area.setScale(AreaScale)

	Wall_01.texmat(matrix_s)
	Wall_02_1.texmat(matrix_w2l) 
	Wall_02_2.texmat(matrix_w2s) 
	Wall_02_3.texmat(matrix_w2l)
	Wall_03.texmat(matrix_s)
	Wall_04.texmat(matrix_l)

	Floor.texmat(matrix_area)
	Ceiling.texmat(matrix_area)

	wallTex = viz.addTexture('wallTex.jpg')
	wallTex.wrap(viz.WRAP_T,viz.REPEAT)
	wallTex.wrap(viz.WRAP_S,viz.REPEAT)
	
	wallTex_darker = viz.addTexture('wallTex_Dark.jpg')
	wallTex_darker.wrap(viz.WRAP_T, viz.REPEAT)
	wallTex_darker.wrap(viz.WRAP_S, viz.REPEAT)
	
	wallTex_bright = viz.addTexture('wallTex_Brightened.jpg')
	wallTex_bright.wrap(viz.WRAP_T, viz.REPEAT)
	wallTex_bright.wrap(viz.WRAP_S, viz.REPEAT)
	
	room.append(Wall_01); room.append(Wall_02_1); room.append(Wall_02_2); room.append(Wall_02_3)
	room.append(Wall_03); room.append(Wall_04)
	room.append(Floor); room.append(Ceiling)

	
	room[0].texture(wallTex)
	room[4].texture(wallTex)
	room[5].texture(wallTex)
	
	room[1].texture(wallTex_bright)
	room[2].texture(wallTex_bright)
	room[3].texture(wallTex_bright)
	
	room[6].texture(wallTex_darker)
	room[7].texture(wallTex_darker)
	
	for i in range(8):
		room[i].setParent(Room)
	
	return Room		

def door_line(high, wide, pixel):
	door=viz.addGroup()

	pos=np.array([[-wide/2, 0, 0], [wide/2, 0, 0],[wide/2, high, 0],[-wide/2, high, 0]])

	
	viz.startLayer(viz.LINE_LOOP)
	viz.lineWidth(pixel)
	for i in range(4):
		viz.vertex(pos[i,:].tolist())

	line=viz.endLayer()
	line.setParent(door)

	return door

def GroundCreator():
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

	return Floor
