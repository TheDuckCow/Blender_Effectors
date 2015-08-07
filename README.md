Blender Effectors
=================

Blender 3D addon for special motion effects for groups of objects, inspired by Cinema 4D's shader effectors.

[**Demo video**](https://www.youtube.com/watch?v=Wtb5R6wck2g)

[![Alt text for your video](http://img.youtube.com/vi/Wtb5R6wck2g/0.jpg)](https://www.youtube.com/watch?v=Wtb5R6wck2g)


Usage
=================
**NOTE: This addon uses drivers to function. Make sure python scripts are set to auto-run** *(user preferences > file > Auto execution)*

- Install the addon via user preferences from file (select effector.py), enable it, and locate the tool under the 3D view toolbar (only visible under the TOOLS tab)
- ENABLE AUTO-RUN, this script uses drivers which need auto-run enabled to function. preferences > file > check "Auto Run Python Scripts"
- Take any single mesh, use the "Separate Faces" function (splits every face into a new object and re-locates the origin); alternatively just select a collection of meshes, they need not be only faces. Consider applying scale and rotation via control-a at this point if you want the current setup to be the "rest" position when the effector is added.
- Press "Add Effector" with the above ojbects selected. This will seteup drivers and constraints for each of the objects and create an armature rig with circular bone shapes.
- Go into pose mode for the added effector rig, and select the inner (solid) shape of the two concentric spheres
- transform this however you want - rotation, scale, position, and you will notice the faces of the previous mesh now react accordingly
- Select and move the outer (wireframe) shape of the two concentric spheres of the rig and move this around. This controls the falloff, and the farther away a face is from this sphere the lower the influence (scale it up or down to change the size of the field of influence).

**Examples of other possible results**
https://www.facebook.com/photo.php?v=756842547715651
https://www.facebook.com/video.php?v=736784593054780


To be implemented eventually
=================

Update Effector: 
This function will allow you to update constraints or parameters such as falloff style and other coming parameters.

Isolation Effectors:
When adding an effector, should have the option to choose between effecting some/all of location, rotation, and scale, as well as which axis.

Effector control panel:
This panel will list the number of added effectors in the scene. With any of these effectors selected, further options for contorlling that effector and all its objects are possible, including:
- Selecting all objects affected by that effector
- Adding/removing objects affected by effector
- Changing the influence factors (loc, rot, scale) for the effector.
- Changing the falloff mode/parameters
- Advanced (i.e. direct) control of the driver equation

Additional effector types:
- Transform Effector (Current implementation)
- Texture Effector (Transform based on nearest pixel value of a UV mapped plane)
- In-line Effector (Same as transform, but transforms made in a line to/from the control armature as opposed to from rest position)

Additional desirable changes and additions:
- Influence vetex group: So that transforms only affect a specific group of vertices (using hooks?)
- Local/global options, for different effects (e.g. if you just wanted to scale on z-axis around control, but source objects are at different orientations)


Current Version notes
=================

The "Update Effector" does nothing at this current time. For current functionality demostration, see the following video:
https://www.facebook.com/video.php?v=736784593054780

Currently, it *does* work to have multiple effectors on the same object without any issue. There is however an issue with location-changing effectors with feedback looping (driver moves object, but then driver is based on object position). Will be fixed in the future with empties as intermediate objects or equivalent setup.

Select empties is just a re-statement of the select all object by type function, later it will recognize empties related to the selected effector group.


Moo-Ack!
