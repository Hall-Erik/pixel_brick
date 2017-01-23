# Pixel Brick

This is my implementation of the Pixel Brick project that can be found on Hackster.io [here](https://www.hackster.io/ravi-sawhney/pixelbrick-273664?ref=part&ref_id=13643&offset=7) which uses the 8x8 LED display on the Sense Hat to show useful information in a simple format.

## This implementation

So far, my implementation uses three quadrants of the LED array.

- Upper left quadrant shows the timeliness of the next bus at a certain stop.  Green means the bus is on time.  Blue means it is early.  Red means it is late.  Two rows means 5-10 minutes off schedule.  Four means 10+.

- Lower left quadrant shows current temperature difference (top) and high temperature difference (bottom).  Each column represents up to 5 degrees of difference. Orange means warmer, Blue means cooler.

- Lower right quadrant shows current chance of precipitation (top) and current UV index (bottom).  For precipitation, each column represents up to 25%. Blue means rain, white means snow. For UV, the column count and color changes based on severity.

This is a work in progress and subject to change.

## Requirements

You will need an API key for wunderground and UTA.

The program looks for a config.ini file in the same directory that looks like this:

```
[uta]
uta_key = xxxxxxxxxxx
stop_id = xxxxxx

[weather]
wunderground_key = xxxxxxxxxxxxxxxx
```
