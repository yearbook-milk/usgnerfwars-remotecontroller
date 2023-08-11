
# HARDWARE SOFTWARE INTERFACE SETTINGS:
pin_config = {                                      
    
# these control which pins do what (note that l, r and yaw pins need to be on a PWM enabled channel)
"leftPin": 18,
"rightPin": 13,
"yawPin": 12,

"revPin": 23,
"firePin": 24,

# set this to 0
"afterSpdCmdDelay": 0,     

# pulse waveform properties                     
"pulse_freq": 50,   
"min_pulse_length": 500,
"max_pulse_length": 2500,
      
# DONT TOUCH      
"pinsToSet": "leftPin rightPin yawPin",

# angle limits (for instance, if you know youll break something by turning the pitch over 45 deg, a software
# lock/safety can be enabled).
"yaw_limits": (-90, 90),
"pitch_limits": (-30, 30),



}


# If you are using this client in remote mode and not running this on the RPi, simply leave set everything to 0 and start in R mode 