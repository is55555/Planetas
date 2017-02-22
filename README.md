# Planetas

This is a little toy I made in June 2009 to try Pyglet. In the end the verdict was that Pyglet is actually not really fit for much more than toys.

Still, this thing is cute for ~330 lines of code and it can be quite instructive.

I used real numbers for the whole system to check it made sense. I used the variable timeFactor = 43800 (in the class "Universe") to speed up things (otherwise a revolution would actually take about 27 days, not much fun). That factor makes 1 minute of realtime equivalent to 30 days. So a revolution takes just under a minute.

The code is short and sweet and it shouldn't take too long to make sense of the whole thing and modify it to one's tastes.

Some caveats include the perspective view, which has plenty of distortion but I couldn't figure out at the time how to set it better. If you increase the radius of the stars you'll appreciate this. This also means the actual orbit is also distorted, but not extremely so.

I included two update procedures. A naive one simply updating the velocities and positions at every tick, and another one using Runge-Kutta, which should be more accurate but it seems to be broken right now, creating a very lopsided orbit.

Running it with the naive procedure things more or less make sense. The revolution time roughly matches 27 days. Well, for starters there's no Sun and it wouldn't 100% match real orbits in any case.

Looking back, some choices seem questionable which is why I didn't care too much about improving it. I'd say using 3D is a bit pointless since including orbit tracks or navigating in 3D in a practical way would complicate the thing way too much for the little toy it is. That would be interesting as a larger project maybe. If I didn't do this to try Pyglet, I'd have used Pygame.

### Keys:

(caps mean SHIFT key + letter)

	t	time factor X2
	T	time factor /2
	SPACE	toggle PAUSE/RESUME
	s	stop all stars (causes them to crash against each other, although there is no collision detection yet)
	m	increase mass of all planets by 10%
	M	decrease mass of all planets by 10%
	c	centre Universe's point of view on the next star (rotates through)

	ESC	close program



# Earth and Moon:

    apogee              4.055E+8 m  (5 E+8 m <=> 0.5 million kilometres)
    perigee             3.633E+8 m
    semimajor axis      3.844E+8 m
    Revolution period (days)    27.3217 days ~= 2.3606 E+6 s
    Mean orbital velocity       1.023 E+3 m/s
    Max. orbital velocity       1.076 E+3 m/s
    Min. orbital velocity       9.64  E+2 m/s

I haven't included the Sun because I'd need a more sophisticated camera system to make it practical. The proportions are such that the moon would be essentially invisible with a fixed cam, among other things.


# Sun - Earth:
(see http://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html)

    mean distance to Earth in meters : 1.496E+11
    Sun radius ~= 109 × Earth's radius
    Sun volumetric mean r = 696 000 000 m = 6.96E+8 m

    Mean orbital velocity      29.78 km/s	= 2.978E+4 m/s
    Max. orbital velocity      30.29 km/s
    Min. orbital velocity      29.29 km/s
    orbital v. aprox 30 times that of Moon/Earth
# Licence
MIT.

