
# HARDWARE SOFTWARE INTERFACE SETTINGS:
pin_config = {                                      # These control which pins on the RPi do what.
    
"leftPin": 12,
"rightPin": 33,
"yawPin": 32,
"afterSpdCmdDelay": 0,                              # This should be set to 0, in order to make the pitch and yaw cmds nonblocking.
"pulse_freq": 50                                    # Pulse frequency, in hZ. 
    
}

