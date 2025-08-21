import stateutils
import hou


def enableSOPState(state_label):
    # We want to launch a SOP state, so we need to make sure the
    # viewer is at the SOP level first
    viewer = stateutils.findSceneViewer()
    network = viewer.pwd()
    if network.childTypeCategory() != hou.sopNodeTypeCategory() and network.childTypeCategory() != hou.objNodeTypeCategory():
        raise hou.Error("You must select an object to use this tool")

    # Set the viewer's current state to my state
    viewer.setCurrentState(state_label)
