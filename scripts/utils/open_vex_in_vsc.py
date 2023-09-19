def openVexInVSC(vex_str):
    if not isinstance(vex_str, str):
        return

    # escape quotes
    vex_str = vex_str.replace("\"", "`\"")
    # print(vex_str)

    # to avoid blocking houdini, we have to use threading
    def __tmp_vex_vsc_func():
        import subprocess
        # @TODO support Linux and OSX?
        subprocess.call(["powershell", "-WindowStyle", "hidden", "-Command", r'''"{0}" | code -
                                exit'''.format(vex_str)], shell=False)


    import threading
    t = threading.Thread(target=__tmp_vex_vsc_func)
    t.start()

 