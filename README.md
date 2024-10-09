# Rob's Wall Clock

This [CircuitPython](https://circuitpython.org/) project drives my wall clock.

[![Youtube Link to Demo of Clock](http://img.youtube.com/vi/jQzFhzzR2q8/0.jpg)](http://www.youtube.com/watch?v=jQzFhzzR2q8 "Video Title")

As a background it uses a variant of [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway's_Game_of_Life) that [includes colors](https://life.tedivm.com/). Time is set using the internet as a starting point to set the internal real time clock, with occasional syncs to the internet for accuracy and timezone/dst adjustments.
