import pymesh
import numpy as np
import math
import datetime
import sys
import time
import os

depth = int(sys.argv[1])
start_x = int(sys.argv[2])


def mesh_trans(mesh, x, y, z):
    return pymesh.form_mesh(mesh.vertices + [[x, y, z]], mesh.faces)

def mesh_rotate(mesh, x, y, z, angle):
    rot = pymesh.Quaternion.fromAxisAngle(np.array([x, y, z]), math.pi*2*angle/360)
    return pymesh.form_mesh(np.dot(rot.to_matrix(), mesh.vertices.T).T, mesh.faces)

def menger_sponge(depth, start_x):    
    start = datetime.datetime.now()
    prev_file = None
    if start_x == 1:
        mesh_fractal = pymesh.generate_box_mesh([0,0,0], [1,1,1])    
    else:
        mesh_fractal = pymesh.load_mesh("/portal/menger_sponge_"+str(depth)+"_x"+str(start_x)+".stl")
        start_x += 3
    z = [-0.1,1.1]
    side = 1
    operation = 'difference'
    #operation = 'union'
    for d in range(1, depth+1):
        log('=== '+str(d)+' / '+str(depth)+' iteration ===')
        side /= 3
        for x in range(start_x,3**d,3):            
            for y in range(1,3**d,3):
                log('[x,y]: ['+str(x)+','+str(y)+'] / '+str(3**d))
                
                box_a = pymesh.generate_box_mesh([side*x,side*y,z[0]], [side*x+side,side*y+side,z[1]])
                
                box_b = mesh_rotate(mesh = box_a, x = 1, y = 0, z = 0, angle = 90)
                box_b = mesh_trans(mesh = box_b, x = 0, y = 1, z = 0)

                box_c = mesh_rotate(mesh = box_a, x = 0, y = 1, z = 0, angle = 90)
                box_c = mesh_trans(mesh = box_c, x = 0, y = 0, z = 1)

                mesh_fractal = pymesh.boolean(mesh_fractal, box_a, operation=operation, engine="igl")
                mesh_fractal = pymesh.boolean(mesh_fractal, box_b, operation=operation, engine="igl")
                mesh_fractal = pymesh.boolean(mesh_fractal, box_c, operation=operation, engine="igl")            
            
            filename = "/portal/menger_sponge_"+str(d)+"_x"+str(x)+".stl"
            pymesh.save_mesh(filename, mesh_fractal, ascii=False)
            if not prev_file is None:
                print('unlinking', prev_file)
                os.unlink(prev_file)
            prev_file = filename

    end = datetime.datetime.now()
    log('generation time: '+str(end - start))
    return mesh_fractal

def log(message):
    print(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), message)

# generation
mesh_fractal = menger_sponge(depth, start_x)

# save
log('saving..')
pymesh.save_mesh("/portal/menger_sponge_"+str(depth)+".stl", mesh_fractal, ascii=False)
log('job complete')
