"""
State:          Viewer Wanderer
State type:     viewer_wanderer
Description:    wander through the viewer
Author:         Dolag
Date Created:   January 26, 2024 - 14:23:49
"""

# Usage: Select the node and hit enter in the viewer.

import hou
import viewerstate.utils as su
import stateutils


class State(object):
    speed = 0.15
    speed_step = 0.05
    rotate_mouse_pos = hou.Vector2(0, 0)
    rotate = False
    MSG = "Press Ctrl + WSADEQ to move the camera\nScroll wheel to set move speed. Current speed : {}"
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer

    def displayPrompt(self):
        self.scene_viewer.setPromptMessage(State.MSG.format(self.speed))

    def onEnter(self, kwargs):
        self.displayPrompt()

    def onResume(self, kwargs):
        self.displayPrompt()

    def onKeyEvent(self, kwargs):
        ui_device = kwargs["ui_event"].device()
        #  wander
        if ui_device.isKeyDown():
            key = ui_device.keyString()
            if key in ('Ctrl+w', 'Ctrl+s', 'Ctrl+a', 'Ctrl+d', 'Ctrl+e', 'Ctrl+q'):
                viewer = stateutils.findSceneViewer()
                if viewer:
                    vp = viewer.curViewport()
                    camera = vp.defaultCamera()
                    forward = hou.Vector3(0, 0, -1)  # camera forward
                    #  forward = forward * camera.rotation()  # no, camera.rotation() rotates a vector into view space
                    forward = forward * camera.rotation().inverted()
                    forward = forward.normalized()
                    #  camera.pivot() is the transform centroid in world space
                    #  camera.translate() is the translation relative to the pivot in view space
                    #  camera.rotate() is the rotation relative to the pivot
                    #  camera.translate() * camera.rotation().inverted() is the camera position in world space
                    move_step = self.speed
                    if key == 'Ctrl+w':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [0, 0, -move_step])))
                    elif key == 'Ctrl+s':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [0, 0, move_step])))
                    elif key == 'Ctrl+a':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [-move_step / camera.orthoWidth(), 0, 0])))
                    elif key == 'Ctrl+d':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [move_step / camera.orthoWidth(), 0, 0])))
                    elif key == 'Ctrl+e':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [0, move_step / (camera.orthoWidth() / camera.aspectRatio()), 0])))
                    elif key == 'Ctrl+q':
                        camera.setTranslation(tuple(a + b for a, b in zip(camera.translation(), [0, -move_step / (camera.orthoWidth() / camera.aspectRatio()), 0])))
                    self.displayPrompt()

                return True

    # def onMouseEvent(self, kwargs):
    #     ui_device = kwargs["ui_event"].device()
    #     if ui_device.isMiddleButton():
    #         #  rotate camera
    #         viewer = stateutils.findSceneViewer()
    #         if viewer:
    #             vp = viewer.curViewport()
    #             camera = vp.defaultCamera()
    #             forward = hou.Vector3((0, 0, -1)) * camera.rotation()
    #             center = hou.Vector3(camera.pivot()) + hou.Vector3(camera.translation()) * camera.rotation().inverted()
    #             forward = center - hou.Vector3(camera.pivot())
    #             forward = forward.normalized()
    #             camera.setPivot(tuple(center))
    #             camera.setTranslation((0, 0, 0))
    #             mouse_pos = hou.Vector2(ui_device.mouseX() / vp.size()[2] - vp.size()[0],
    #                                            ui_device.mouseY() / vp.size()[3] - vp.size()[1])
    #             delta_pos = mouse_pos - self.rotate_mouse_pos
    #
    #             # 假设你已经有了一个yaw和pitch的角度（以度为单位）
    #             yaw = delta_pos[1] * 0.25  # Yaw角度
    #             pitch = delta_pos[0] * 0.25  # Pitch角度
    #
    #             # 使用hou.hmath.buildRotate函数来构造旋转矩阵
    #             rotation_matrix = hou.hmath.buildRotate((0, yaw, pitch))
    #             rotation = camera.rotation() * rotation_matrix.extractRotationMatrix3()
    #             camera.setRotation(rotation)
    #
    #             return True
    #
    #     return False

    def onMouseWheelEvent(self, kwargs):
        ui_device = kwargs["ui_event"].device()
        #  change speed
        if ui_device.mouseWheel() != 0:
            self.speed = self.speed + ui_device.mouseWheel() * self.speed_step
            self.displayPrompt()
            return True

        return False

    def onKeyTransitEvent(self, kwargs):
        ui_device = kwargs["ui_event"].device()
        if ui_device.isMiddleButton() and not self.rotate:
            viewer = stateutils.findSceneViewer()
            vp = viewer.curViewport()
            camera = vp.defaultCamera()
            #  record the init mouse pos
            self.rotate_mouse_pos = hou.Vector2(ui_device.mouseX() / vp.size()[2] - vp.size()[0],
                                               ui_device.mouseY() / vp.size()[3] - vp.size()[1])
            self.rotate = True
        elif ui_device.isMidddleButtonUp():
            self.rotate = False

        self.displayPrompt()


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "dolag::viewer_wanderer"
    state_label = "Viewer Wanderer"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)

    return template

