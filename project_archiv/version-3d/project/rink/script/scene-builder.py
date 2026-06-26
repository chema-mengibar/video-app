import bpy
import json
from math import degrees

path = bpy.path.abspath("//")


frameIdx = 0
fileName = 1
sceneName = 'scene-' + str(fileName)

data = {
    'meta':{
       'name': sceneName,
       'limits': {
            "x": 22.5,
            "z": 13.5
        },
    },
    'assets': [
    
    ]
}

# SCENE OBJECTS

# selection_names = [obj.name for obj in bpy.context.selected_objects]


selection_names = [
    {'dummy':'dummy-g-1', 'target':'player-g-1'},
    {'dummy':'dummy-g-2', 'target':'player-g-2'},
    {'dummy':'dummy-g-3', 'target':'player-g-3'},
    {'dummy':'dummy-g-4', 'target':'player-g-4'},
    {'dummy':'dummy-g-goalie', 'target':'player-g-goalie'},
    {'dummy':'dummy-h-0', 'target':'player-h-0'}, 
    {'dummy':'dummy-h-1', 'target':'player-h-1'},
    {'dummy':'dummy-h-2', 'target':'player-h-2'},
    {'dummy':'dummy-h-3', 'target':'player-h-3'},
    {'dummy':'dummy-h-goalie', 'target':'player-h-goalie'}
]

bpy.context.scene.frame_set(frameIdx)

for objItem in selection_names:
    
    obj = bpy.data.objects[objItem['dummy']]
    loc = obj.location
    
    x = round(loc.x, 2)
    y = round(loc.y, 2)
    z = round(loc.z, 2)
    
    r_x = round(degrees(obj.rotation_euler.x), 2)
    r_y = round(degrees(obj.rotation_euler.y), 2)
    r_z = round(degrees(obj.rotation_euler.z), 2)
    
    objData = {
        'name': objItem['target'],
        'loc': {
            'x': x,    
            'z': y,    
        },
        'rot': {  
            'z': r_z,    
        },
    }
    data['assets'].append(objData)



content = f"""
{json.dumps(data, indent=4)}
"""

with open(path + "/export/" + sceneName +".json",'w') as f:
    f.write(content)
    