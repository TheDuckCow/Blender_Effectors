Blender Effectors
=================

Blender 3D addon for special motion effects for groups of objects, inspired by Cinema 4D's shader effectors.

Usage
=================

- Install the addon via user preferences from file (select effector.py), enable it, and locate the tool under the 3D view toolbar (currently on all tabs)
- Take any single mesh, use the "Separate Faces" function (splits every face into a new object and re-locates the origin)
- Use "Add Effector". This will seteup drivers and constraints for each of the objects and create an armature rig with circular bone shapes.
- Go into pose mode for the added effector rig, and select the inner (solid) shape of the two concentric spheres
- transform this however you want - rotation, scale, position, and you will notice the faces of the previous mesh now react accordingly
- Select and move the outer (wireframe) shape of the two concentric spheres of the rig and move this around. This controls the falloff, and the farther away a face is from this sphere the lower the influence (scale it up or down to change the size of the field of influence

Not yet implemented
=================

Update Effector: 
This function will allow you to update constraints or parameters such as falloff style and other coming parameters.

Join Effector/Remove Effector:
This function will allow you add or remove a specific object from the set of objects controlled by the effector rig

Current Version notes
=================

This addon is not at version "1.0" yet, basic functionality has not been completely achieved. For now, to get proper results, one needs to go into edit mode of the added rig and parent the inner sphere to the outter sphere to work as intended. No falloff options exist yet.

Moo-Ack!
