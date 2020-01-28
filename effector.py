########
"""
GNU GENERAL PUBLIC LICENSE

Blender 3D addon with purpose to help create special motion graphics
with effector controls inspired by Cinema 4D.

Example usage:
https://www.youtube.com/watch?v=BYXmV7fObOc

Notes to self:
Create a simialr, lower poly contorl handle and
perhaps auto enable x-ray/bounding.
Long term, might become an entire panel with tools
of all types of effectors, with secitons like
convinience tools (different split faces/loose buttons)
next to the actual different effector types
e.g. transform effector (as it is)
time effector (..?) etc. Research it more.

another scripting ref:
http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Interface#A_popup_dialog

plans:
- Make checkboxes for fields to have effector affect (loc, rot, scale)
- Name the constraints consistent to effector name, e.g. effector.L.001 for easy removal
- add falloff types (and update-able in driver setting)
- custome driver equation field ('advanced' tweaking, changes drivers for all in that effector group)
- Empty vertex objects for location which AREN'T transformed, so that there is no limit to
how much the location can do (now limited to be between object and base bone)
- create list panel that shows effectors added, and with each selected can do things:
	- all more effector objects
	- select current objects (and rig)
	- change falloff/equation
	- remove selected from effector
	- remove effector (drivers & rig)
	- apply effector in position (removes rig)

Source code available on github:
https://github.com/TheDuckCow/Blender_Effectors

"""


bl_info = {
	"name": "Blender Effectors",
	"author": "Patrick W. Crawford",
	"version": (1, 0, 4),
	"blender": (2, 80, 0),
	"location": "3D window toolshelf",
	"category": "Object",
	"description": "Effector special motion graphics",
	"wiki_url": "https://github.com/TheDuckCow/Blender_Effectors"
	}


import bpy

## just in case
from bpy.props import *
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from os.path import dirname, join


BV_IS_28 = None  # global initialization
def bv28():
	"""Check if blender 2.8, for layouts, UI, and properties. """
	global BV_IS_28
	if not BV_IS_28:
		BV_IS_28 = hasattr(bpy.app, "version") and bpy.app.version >= (2, 80)
	return BV_IS_28


def createEffectorRig(bones, loc=None):
	"""Add the control armature and rig used to modify the objects in scope"""
	[bone_base,bone_control] = bones
	if loc is None:
		loc = get_cuser_location()

	bpy.ops.object.armature_add(location=loc)
	rig = bpy.context.active_object
	rig.name = "effector"

	"""
	bpy.ops.object.mode_set(mode='EDIT')
	control = rig.data.edit_bones.new('control')
	#bpy.ops.armature.bone_primitive_add() #control
	# eventually add property as additional factor

	rig.data.bones[0].name = 'base'
	rig.data.bones[0].show_wire = True
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')

	# SCENE REFRESH OR SOMETHING???
	rig.data.bones[1].name = 'control'
	control = obj.pose.bones[bones['base']]
	#rig.data.bones[1].parent = rig.data.[bones['base']] #need other path to bone data
	bpy.ops.object.mode_set(mode='OBJECT')
	rig.pose.bones[0].custom_shape = bone_base
	rig.pose.bones[1].custom_shape = bone_control

	# turn of inherent rotation for control??

	# property setup
	#bpy.ops.wm.properties_edit(data_path='object', property='Effector Scale',
	#   value='1.0', min=0, max=100, description='Falloff scale of effector')
	#scene property='Effector.001'

	"""

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.armature.select_all(action='SELECT')
	bpy.ops.armature.delete()

	arm = rig.data
	bones = {}

	bone = arm.edit_bones.new('base')
	bone.head[:] = 0.0000, 0.0000, 0.0000
	bone.tail[:] = 0.0000, 0.0000, 1.0000
	bone.roll = 0.0000
	bone.use_connect = False
	bone.show_wire = True
	bones['base'] = bone.name

	bone = arm.edit_bones.new('control')
	bone.head[:] = 0.0000, 0.0000, 0.0000
	bone.tail[:] = 0.0000, 1.0000, 0.0000
	bone.roll = 0.0000
	bone.use_connect = False
	bone.parent = arm.edit_bones[bones['base']]
	bones['control'] = bone.name

	bpy.ops.object.mode_set(mode='OBJECT')
	pbone = rig.pose.bones[bones['base']]
	#pbone.rigify_type = ''
	pbone.lock_location = (False, False, False)
	pbone.lock_rotation = (False, False, False)
	pbone.lock_rotation_w = False
	pbone.lock_scale = (False, False, False)
	pbone.rotation_mode = 'QUATERNION'
	pbone.bone.layers = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
	pbone = rig.pose.bones[bones['control']]
	#pbone.rigify_type = ''
	pbone.lock_location = (False, False, False)
	pbone.lock_rotation = (False, False, False)
	pbone.lock_rotation_w = False
	pbone.lock_scale = (False, False, False)
	pbone.rotation_mode = 'QUATERNION'
	#pbone.bone.layers = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]

	bpy.ops.object.mode_set(mode='EDIT')
	for bone in arm.edit_bones:
		bone.select = False
		bone.select_head = False
		bone.select_tail = False
	for b in bones:
		bone = arm.edit_bones[bones[b]]
		bone.select = True
		bone.select_head = True
		bone.select_tail = True
		arm.edit_bones.active = bone

	arm.layers = [(x in [0]) for x in range(32)]

	bpy.ops.object.mode_set(mode='OBJECT')
	rig.pose.bones[0].custom_shape = bone_base
	rig.pose.bones[1].custom_shape = bone_control

	return rig

def createBoneShapes():
	"""Sets bone shape for control armature"""
	if (bpy.data.objects.get("effectorBone1") is None) or (bpy.data.objects.get("effectorBone2") is None):
		bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=8, enter_editmode=True)
		bpy.ops.mesh.delete(type='ONLY_FACE')
		bpy.ops.object.editmode_toggle()
		effectorBone1 = bpy.context.active_object
		effectorBone1.name = "effectorBone1"
		if bv28():
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, enter_editmode=False, radius=0.5/2)
		else:
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, enter_editmode=False, size=0.5)
		effectorBone2 = bpy.context.active_object
		effectorBone2.name = "effectorBone2"

		#move to last layer and hide
		if bv28():
			obj_unlink_remove(effectorBone1, False)
			obj_unlink_remove(effectorBone2, False)
			print("Improve placement of items to be render-hidden")
		else:
			[False] * 19 + [True]
			effectorBone1.hide = True
			effectorBone2.hide = True
			effectorBone1.hide_render = True
			effectorBone2.hide_render = True

	return [bpy.data.objects["effectorBone1"],bpy.data.objects["effectorBone2"]]


def addEffectorObj(objList, rig):
	# store previous selections/active etc
	prevActive = bpy.context.object

	#default expression, change later with different falloff etc
	default_expression = "1/(.000001+objDist)*scale"

	#empty list versus obj list?
	emptyList = []

	# explicit state set
	bpy.ops.object.mode_set(mode='OBJECT')

	# iterate over all objects passed in
	for obj in objList:
		if obj.type=="EMPTY":
			continue
		##############################################
		# Add the empty intermediate object/parent
		if bv28():
			bpy.ops.object.empty_add(
				type='PLAIN_AXES', align='WORLD', location=obj.location)
		else:
			bpy.ops.object.empty_add(
				type='PLAIN_AXES', view_align=False, location=obj.location)
		empty = bpy.context.active_object
		empty.name = "effr.empty"
		select_set(obj, True)
		preParent = obj.parent
		bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
		if bv28():
			bpy.context.object.empty_display_size = 0.1
		else:
			bpy.context.object.empty_draw_size = 0.1
		if (preParent):
			bpy.ops.object.select_all(action='DESELECT')

			# need to keep transform!
			select_set(preParent, True)
			select_set(empty, True)
			set_active_object(bpy.context, preParent)
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
			#empty.parent = preParent

		set_active_object(bpy.context, obj)
		preConts = len(obj.constraints)  # starting number of constraints

		###############################################
		# LOCATION
		bpy.ops.object.constraint_add(type='COPY_LOCATION')
		obj.constraints[preConts].use_offset = True
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL'
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"

		driverLoc = obj.constraints[preConts].driver_add("influence").driver
		driverLoc.type = 'SCRIPTED'

		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varL_dist = driverLoc.variables.new()
		varL_dist.type = 'LOC_DIFF'
		varL_dist.name = "objDist"
		varL_dist.targets[0].id = rig
		varL_dist.targets[0].bone_target = 'base'
		varL_dist.targets[1].id = empty

		varL_scale = driverLoc.variables.new()
		varL_scale.type = 'TRANSFORMS'
		varL_scale.name = 'scale'
		varL_scale.targets[0].id = rig
		varL_scale.targets[0].transform_type = 'SCALE_Z'
		varL_scale.targets[0].bone_target = 'base'

		driverLoc.expression = default_expression

		###############################################
		# ROTATION
		bpy.ops.object.constraint_add(type='COPY_ROTATION')
		preConts+=1
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL'
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"

		driverRot = obj.constraints[preConts].driver_add("influence").driver
		driverRot.type = 'SCRIPTED'

		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varR_dist = driverRot.variables.new()
		varR_dist.type = 'LOC_DIFF'
		varR_dist.name = "objDist"
		varR_dist.targets[0].id = rig
		varR_dist.targets[0].bone_target = 'base'
		varR_dist.targets[1].id = obj

		varR_scale = driverRot.variables.new()
		varR_scale.type = 'TRANSFORMS'
		varR_scale.name = 'scale'
		varR_scale.targets[0].id = rig
		varR_scale.targets[0].transform_type = 'SCALE_Z'
		varR_scale.targets[0].bone_target = 'base'

		driverRot.expression = default_expression

		###############################################
		# SCALE
		bpy.ops.object.constraint_add(type='COPY_SCALE')
		preConts+=1
		obj.constraints[preConts].target_space = 'LOCAL'
		obj.constraints[preConts].owner_space = 'LOCAL'
		obj.constraints[preConts].target = rig
		obj.constraints[preConts].subtarget = "control"

		driverScale = obj.constraints[preConts].driver_add("influence").driver
		driverScale.type = 'SCRIPTED'

		# var for objDist two targets, 1st is "base" second is "distanceRef"
		varS_dist = driverScale.variables.new()
		varS_dist.type = 'LOC_DIFF'
		varS_dist.name = "objDist"
		varS_dist.targets[0].id = rig
		varS_dist.targets[0].bone_target = 'base'
		varS_dist.targets[1].id = obj

		varS_scale = driverScale.variables.new()
		varS_scale.type = 'TRANSFORMS'
		varS_scale.name = 'scale'
		varS_scale.targets[0].id = rig
		varS_scale.targets[0].transform_type = 'SCALE_Z'
		varS_scale.targets[0].bone_target = 'base'

		driverScale.expression = default_expression


########################################################################################
#   Above for precursor functions
#   Below for the class functions
########################################################################################


class BE_OT_add_effector(bpy.types.Operator):
	"""Create the effector object and setup"""
	bl_idname = "object.add_effector"
	bl_label = "Add Effector"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		objList = bpy.context.selected_objects
		[effectorBone1,effectorBone2] = createBoneShapes()
		rig = createEffectorRig([effectorBone1,effectorBone2])
		addEffectorObj(objList, rig)
		set_active_object(context, rig)
		return {'FINISHED'}


class BE_OT_update_effector(bpy.types.Operator):
	bl_idname = "object.update_effector"
	bl_label = "Update Effector"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		print("Update Effector: NOT CREATED YET!")
		return {'FINISHED'}


class BE_OT_select_empties(bpy.types.Operator):
	bl_idname = "object.select_empties"
	bl_label = "Select Effector Empties"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		if context.mode != 'OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_by_type(type='EMPTY')
		return {'FINISHED'}


class BE_OT_separate_faces(bpy.types.Operator):
	"""Separate all faces into new meshes"""
	bl_idname = "object.separate_faces"
	bl_label = "Separate Faces to Objects"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		# make sure it's currently in object mode for sanity
		bpy.ops.object.mode_set(mode='OBJECT')

		for obj in bpy.context.selected_objects:
			set_active_object(context, obj)
			if obj.type != "MESH":
				continue
			#set scale to 1
			try:
				bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
			except:
				print("couldn't transform")
			#mark all edges sharp
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.mark_sharp()
			bpy.ops.object.mode_set(mode='OBJECT')
			#apply modifier to split faces
			bpy.ops.object.modifier_add(type='EDGE_SPLIT')
			obj.modifiers[-1].split_angle = 0
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier=obj.modifiers[-1].name)
			#clear sharp
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.mark_sharp(clear=True)
			bpy.ops.object.mode_set(mode='OBJECT')
			#separate to meshes
			bpy.ops.mesh.separate(type="LOOSE")
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

		return {'FINISHED'}


class BE_PT_effectors(bpy.types.Panel):
	"""Effector Tools"""

	bl_label = "Effector Tools"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS' if not bv28() else 'UI'
	bl_category = "Tools" if not bv28() else 'Tool'

	def draw(self, context):
		view = context.space_data
		scene = context.scene
		layout = self.layout

		split = layout.split()
		col = split.column(align=True)
		col.operator("object.separate_faces", text="Separate Faces")
		col.operator("object.add_effector", text="Add Effector")
		# col.operator("wm.mouse_position", text="Update Effector alt")
		col.operator("object.select_empties", text="Select Empties")

		if not bv28() and view.show_relationship_lines:
			layout.label(text="")
			layout.label(text="Disable Recommended:")
			col.prop(view, "show_relationship_lines")


########################################################################################
#   Registration / cross support
########################################################################################


def make_annotations(cls):
	"""Add annotation attribute to class fields to avoid Blender 2.8 warnings"""
	if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
		return cls
	bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
	if bl_props:
		if '__annotations__' not in cls.__dict__:
			setattr(cls, '__annotations__', {})
		annotations = cls.__dict__['__annotations__']
		for k, v in bl_props.items():
			annotations[k] = v
			delattr(cls, k)
	return cls


def set_active_object(context, obj):
	"""Get the active object in a 2.7 and 2.8 compatible way"""
	if hasattr(context, "view_layer"):
		context.view_layer.objects.active = obj # the 2.8 way
	else:
		context.scene.objects.active = obj # the 2.7 way


def select_get(obj):
	"""Multi version compatibility for getting object selection"""
	if hasattr(obj, "select_get"):
		return obj.select_get()
	else:
		return obj.select


def select_set(obj, state):
	"""Multi version compatibility for setting object selection"""
	if hasattr(obj, "select_set"):
		obj.select_set(state)
	else:
		obj.select = state


def get_cuser_location(context=None):
	"""Returns the location vector of the 3D cursor"""
	if not context:
		context = bpy.context
	if hasattr(context.scene, "cursor_location"):
		return context.scene.cursor_location
	elif hasattr(context.scene, "cursor") and hasattr(context.scene.cursor, "location"):
		return context.scene.cursor.location  # later 2.8 builds
	elif hasattr(context.space_data, "cursor_location"):
		return context.space_data.cursor_location
	elif hasattr(context.space_data, "cursor") and hasattr(context.space_data.cursor, "location"):
		return context.space_data.cursor.location
	print("WARNING! Unable to get cursor location, using (0,0,0)")
	return (0, 0, 0)


def obj_unlink_remove(obj, remove, context=None):
	"""Unlink an object from the scene, and remove from data if specified"""
	if not context:
		context = bpy.context
	if hasattr(context.scene.objects, "unlink"):  # 2.7
		context.scene.objects.unlink(obj)
	elif hasattr(context.scene, "collection"):  # 2.8
		try:
			context.scene.collection.objects.unlink(obj)
		except RuntimeError:
			pass # if not in master collection
		colls = list(obj.users_collection)
		for coll in colls:
			coll.objects.unlink(obj)
	if remove is True:
		obj.user_clear()
		bpy.data.objects.remove(obj)


classes = (
	BE_OT_add_effector,
	BE_OT_update_effector,
	BE_PT_effectors,
	BE_OT_separate_faces,
	BE_OT_select_empties
)


def register():
	for cls in classes:
		make_annotations(cls)
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()
