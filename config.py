
# HARDWARE SOFTWARE INTERFACE SETTINGS:
pin_config = {                                      # These control which pins on the RPi do what.
    
"leftPin": 18,
"rightPin": 13,
"yawPin": 12,
"afterSpdCmdDelay": 0,                              # This should be set to 0, in order to make the pitch and yaw cmds nonblocking.
"pulse_freq": 50,                                    # Pulse frequency, in hZ. 
"pinsToSet": "leftPin rightPin yawPin"

}


# If you are using this client in remote mode and not running this on the RPi, simply leave this as default and start in R mode 