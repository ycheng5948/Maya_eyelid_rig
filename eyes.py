from maya import cmds

# after the 2 initial CRVs are created from GEO
CRVs = ['lid_top_CRV', 'lid_bot_CRV']
cmds.delete("lid_top_CRV", ch=True)
cmds.delete("lid_bot_CRV", ch=True)

for i in CRVs:
    cmds.duplicate(i, n=i.replace('_CRV', '_blk_CRV'))
    cmds.duplicate(i, n=i.replace('_CRV', '_drv_CRV'))
    cmds.duplicate(i, n=i.replace('_CRV', '_drv_low_CRV'))
cmds.duplicate('lid_top_CRV', n='lid_bld_CRV')

# set up bld_CRV
cmds.blendShape('lid_bot_CRV','lid_bld_CRV', n='lid_bld_temp_BS')
cmds.blendShape('lid_bld_temp_BS', edit=True, w=[0, 0.5])
cmds.delete("lid_bld_CRV", ch=True)

# rebuilding the drv_low_CRVs
cmds.rebuildCurve('lid_top_drv_low_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.01)
cmds.rebuildCurve('lid_bot_drv_low_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.01)
cmds.delete("lid_top_drv_low_CRV", ch=True)
cmds.delete("lid_bot_drv_low_CRV", ch=True)

# setting up blend shapes
cmds.blendShape('lid_top_drv_CRV', 'lid_bot_drv_CRV', 'lid_bld_CRV', n='lid_bld_BS')
cmds.blendShape('lid_top_drv_CRV', 'lid_bld_CRV', 'lid_top_blk_CRV', n='lid_top_blk_BS')
cmds.blendShape('lid_bld_CRV', 'lid_bot_drv_CRV', 'lid_bot_blk_CRV', n='lid_bot_blk_BS')

# manual
# setting up all needed wire deform
###################################################################
# create and name CTRLs and orient the GRP correctly
#creating ball ctrl
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='A')
cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), n='B')
cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), n='C')
crvGrp = cmds.group(em=True, name='ball_CRV')
crvShape = ['AShape', 'BShape', 'CShape']
cmds.parent(crvShape, crvGrp, s=1,r=1)
cmds.delete('A', 'B', 'C')
crvGrp = cmds.group(em=True, name='ball_GRP')
cmds.parent('ball_CRV', 'ball_GRP')

# get CVs' world space information to move the CTRLs to
top_CTRLs_name = ['in', 'top_in', 'top', 'top_out', 'out']
bot_CTRLs_name = ['bot_in', 'bot', 'bot_out']

top_CVs = ['lid_top_drv_low_CRV.cv[0]', 'lid_top_drv_low_CRV.cv[2]', 'lid_top_drv_low_CRV.cv[3]', 'lid_top_drv_low_CRV.cv[4]', 'lid_top_drv_low_CRV.cv[6]']
bot_CVs = ['lid_bot_drv_low_CRV.cv[2]', 'lid_bot_drv_low_CRV.cv[3]', 'lid_bot_drv_low_CRV.cv[4]']

# get CV positions
def get_cv_positions(cvs):
    return [cmds.xform(cv, q=1, t=1, ws=1) for cv in cvs]

top_positions = get_cv_positions(top_CVs)
bot_positions = get_cv_positions(bot_CVs)

# determine if first CV is outer or inner
is_outer = abs(top_positions[0][0]) > abs(top_positions[-1][0])

# reverse control order if outer edge is first
if is_outer:
    top_CTRLs_name.reverse()
    bot_CTRLs_name.reverse()

# duplicate and move the controls
def create_controls(ctrl_names, positions, suffix=""):
    for name, pos in zip(ctrl_names, positions):
        grp = cmds.duplicate('ball_GRP', name='lid_{0}_GRP{1}'.format(name, suffix), rc=1)[0]
        ctrl = cmds.rename(cmds.listRelatives(grp, c=1)[0], 'lid_{0}_CTRL'.format(name))
        cmds.move(*pos, grp)

create_controls(top_CTRLs_name, top_positions)
create_controls(bot_CTRLs_name, bot_positions)

# clean up
cmds.delete('ball_GRP')

# creating joints based on CTRLs' names to bind the curves
CTRLs = cmds.ls('lid_*_CTRL')
for i in CTRLs:
    jnt = cmds.createNode("joint", n=i.replace("_CTRL", "_JNT"))
    cmds.parentConstraint(i, jnt, mo=False)

# skinning the newly made jnts to drv_lowCRV
top_JNTs = ['lid_in_JNT', 'lid_out_JNT', 'lid_top_JNT', 'lid_top_in_JNT', 'lid_top_out_JNT']
bot_JNTs = ['lid_out_JNT', 'lid_in_JNT', 'lid_bot_out_JNT', 'lid_bot_in_JNT', 'lid_bot_JNT']
cmds.skinCluster(top_JNTs, 'lid_top_drv_low_CRV', dr=4)
cmds.skinCluster(bot_JNTs, 'lid_bot_drv_low_CRV', dr=4)

# creating groups to tidy up the outline
ctrls = cmds.ls('lid_*_GRP')
cmds.group(em=True, name='lid_CTRL_GRP')
cmds.parent(ctrls, 'lid_CTRL_GRP')

joints = cmds.ls('lid_*_JNT')
cmds.group(em=True, name='lid_JNT_GRP')
cmds.parent(joints, 'lid_JNT_GRP')

###################################################################
# after all BS and wire deform created on the CRVs #manual
# also after CTRLs and created and GRPs oriented accordingly # manual
# and after the joints from previous step binded to the drv_low_CRV #auto

# setting up settings locator
cmds.spaceLocator(n='L_eye_settings_LOC')
settings_shape = 'L_eye_settings_LOCShape'
cmds.addAttr(settings_shape, at='float', ln='blink_height', min=-1, max=1, dv=0, k=True)
cmds.addAttr(settings_shape, at='float', ln='blink_top', min=0, max=1, dv=0, k=True)
cmds.addAttr(settings_shape, at='float', ln='blink_bottom', min=0, max=1, dv=0, k=True)

# hide locked and unused attributes of the locator shape
cmds.setAttr('L_eye_settings_LOCShape.lpx', channelBox=0, keyable=0)
cmds.setAttr('L_eye_settings_LOCShape.lpy', channelBox=0, keyable=0)
cmds.setAttr('L_eye_settings_LOCShape.lpz', channelBox=0, keyable=0)
cmds.setAttr('L_eye_settings_LOCShape.lsx', channelBox=0, keyable=0)
cmds.setAttr('L_eye_settings_LOCShape.lsy', channelBox=0, keyable=0)
cmds.setAttr('L_eye_settings_LOCShape.lsz', channelBox=0, keyable=0)

# parenting LOC to ctrls and hide
ctrls = cmds.ls('L_lid_*_CTRL')
for x in ctrls:
    cmds.parent(settings_shape, x, r=True, s=True, add=True)

cmds.hide('L_eye_settings_LOCShape')

# create reverse node
L_eye_rvr = cmds.createNode('reverse', n='L_eye_RVR')

# connecting locator attr to BS
cmds.connectAttr('{0}.blink_top'.format('L_eye_settings_LOCShape'), '{0}.L_lid_bld_CRV'.format('L_lid_top_blk_BS'))
cmds.connectAttr('{0}.blink_top'.format('L_eye_settings_LOCShape'), '{0}.inputX'.format('L_eye_RVR'))
cmds.connectAttr('{0}.outputX'.format('L_eye_RVR'), '{0}.L_lid_top_drv_CRV'.format('L_lid_top_blk_BS'))

cmds.connectAttr('{0}.blink_bottom'.format('L_eye_settings_LOCShape'), '{0}.L_lid_bld_CRV'.format('L_lid_bot_blk_BS'))
cmds.connectAttr('{0}.blink_bottom'.format('L_eye_settings_LOCShape'), '{0}.inputY'.format('L_eye_RVR'))
cmds.connectAttr('{0}.outputY'.format('L_eye_RVR'), '{0}.L_lid_bot_drv_CRV'.format('L_lid_bot_blk_BS'))

# create nodes for blink height
L_lid_top_RMPV = cmds.createNode('remapValue', n='L_lid_top_RMPV')
L_lid_bot_RMPV = cmds.createNode('remapValue', n='L_lid_bot_RMPV')
cmds.setAttr('{0}.inputMin'.format(L_lid_top_RMPV), -1)
cmds.setAttr('{0}.inputMin'.format(L_lid_bot_RMPV), -1)
cmds.setAttr('{0}.inputMax'.format(L_lid_top_RMPV), 1)
cmds.setAttr('{0}.inputMax'.format(L_lid_bot_RMPV), 1)

cmds.setAttr('{0}.outputMax'.format(L_lid_top_RMPV), 1)
cmds.setAttr('{0}.outputMax'.format(L_lid_bot_RMPV), 0)
cmds.setAttr('{0}.outputMin'.format(L_lid_top_RMPV), 0)
cmds.setAttr('{0}.outputMin'.format(L_lid_bot_RMPV), 1)

cmds.connectAttr('{0}.blink_height'.format('L_eye_settings_LOCShape'), '{0}.inputValue'.format('L_lid_top_RMPV'))
cmds.connectAttr('{0}.blink_height'.format('L_eye_settings_LOCShape'), '{0}.inputValue'.format('L_lid_bot_RMPV'))
cmds.connectAttr('{0}.outValue'.format('L_lid_top_RMPV'), '{0}.L_lid_top_drv_CRV'.format('L_lid_bld_BS'))
cmds.connectAttr('{0}.outValue'.format('L_lid_bot_RMPV'), '{0}.L_lid_bot_drv_CRV'.format('L_lid_bld_BS'))

###################################################################

#eyelids tweakers ctrl setting
curves = ["L_lid_top_CRV", "L_lid_bot_CRV"]

# creating lid_JNT from eye_aim_JNT
cmds.duplicate('L_eye_aim_JNT', po=1, name='L_lid_JNT')

# create up_obj_locator
L_eye_up_obj_LOC = cmds.spaceLocator(n='L_eye_up_obj_LOC')
cmds.delete(cmds.parentConstraint('L_lid_JNT', L_eye_up_obj_LOC, mo=0))
cmds.move(5, 'L_eye_up_obj_LOC', y=True, relative=1)
cmds.hide('L_eye_up_obj_LOC')

# creating twk CTRLs
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='ring_CRV')
cmds.group(em=True, name='ring_GRP')
cmds.parent('ring_CRV', 'ring_GRP')

for crv in curves:
    cvs = cmds.ls("{0}.cv[*]".format(crv), fl=True)

    controls = []
    groups = []

    for i, cv in enumerate(cvs):
        jnt = cmds.createNode("joint", n=crv.replace("_CRV", "_JNT").replace("L_", "L_{0}_".format(str(i).zfill(2))))
        jnt_tip = cmds.createNode("joint", n=jnt.replace("_lid", "_lid_tip"))
        cmds.parent(jnt_tip, jnt)

        cmds.parent(jnt, "L_lid_JNT")

        cmds.setAttr("{0}.t".format(jnt), 0, 0, 0)

        grp, ctrl = cmds.duplicate("ring_GRP", n=jnt.replace("_JNT", "_GRP"), rc=True)
        ctrl = cmds.rename(ctrl, jnt.replace("_JNT", "_CTRL"))


        pci = cmds.createNode("pointOnCurveInfo", n=jnt.replace("_JNT", "_PCI"))
        crv_shape = cmds.listRelatives(crv, s=True) [0]
        cmds.connectAttr("{0}.worldSpace".format(crv_shape), "{0}.inputCurve".format(pci))
        cmds.connectAttr("{0}.position".format(pci), "{0}.translate".format(grp))
        cmds.setAttr("{0}.parameter".format(pci), i)

        cmds.aimConstraint(ctrl, jnt, mo=False, aimVector=[0, 0, 1], upVector=[0, 1, 0],
                           worldUpType="object", worldUpObject="L_eye_up_obj_LOC")
        
        cmds.xform(jnt_tip, ws=True, t=cmds.xform(cv, ws=True, q=True, t=True))

        if groups:
            cmds.aimConstraint(groups[-1], grp, mo=False, aimVector=[1, 0, 0], upVector=[0, 1, 0],
                               worldUpType="object", worldUpObject="L_eye_up_obj_LOC")
        controls.append(ctrl)
        groups.append(grp)

    for ctrl in controls:
        cmds.parent("L_eye_settings_LOCShape", ctrl, add=True, s=True)

# delete the ring_GRP
cmds.delete('ring_GRP')

###################################################################
# setting up lid_mst_CTRL and eye_mst_CTRL #manual
###################################################################
