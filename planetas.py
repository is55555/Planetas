#!/usr/bin/env python
# units in meters, seconds and kilograms
# internal distance unit = Earth radius

import os, pyglet, pyglet.clock
from pyglet.gl import *
from pyglet import window, event
from math import sqrt

G_Newton = 6.674E-11


def distance_scale(metric, invert=False):
    earth_radius = 6.371E+6
    if invert:
        return metric * earth_radius
    else:
        return metric / earth_radius  # unit of distance will be the radius of the Earth


class Vec3d: # GLfloat 3D vector
    def __init__(self, *args):
        self.values = (GLfloat * len(args))(*args)

    def __getitem__(self, key):
        return self.values[key]

    def subtract(vec_a, vec_b):
        return Vec3d(vec_a[0] - vec_b[0], vec_a[1] - vec_b[1], vec_a[2] - vec_b[2])

    def add(vec_a, vec_b):
        return Vec3d(vec_a[0] + vec_b[0], vec_a[1] + vec_b[1], vec_a[2] + vec_b[2])

    def norm(vec):
        return sqrt((vec[0] * vec[0]) + (vec[1] * vec[1]) + (vec[2] * vec[2]))

    # scalar multiplying a vector
    def scalar_mult(vector, scalar):
        return Vec3d((scalar * vector[0]),
                     (scalar * vector[1]),
                     (scalar * vector[2]))

    def __str__(vec):
        return str(vec[0]) + ', ' + str(vec[1]) + ', ' + str(vec[2])

    def __repr__(vec):
        return "Vec3d(" + repr(vec[0]) + ', ' + repr(vec[1]) + ', ' + repr(vec[2]) + ")"

    def to_list(v):
        return [v[0], v[1], v[2]]

    def sexp_str(v): # print_number_array(a):
        s = '('
        for i in v.to_list():
            s += " %+1.4e " % i
        s += ')'
        return s


class Star:
    def __init__(self, label = "", mass=0.0, v_pos=Vec3d(0.0, 0.0, 0.0), v_vel=Vec3d(0.0, 0.0, 0.0),
                 colour=Vec3d(1.0, 1.0, 1.0), radius=1.0):  # v_pos = position vector v_vel = velocity vector
        self.mass = mass
        self.v_pos = v_pos
        self.v_vel = v_vel  # static against the PoV, by default
        self.colour = colour
        self.radius = radius  # default is the unit (will be set to be the radius of the earth)
        # self.acceleration_vector = vec(0, 0, 0)
        self.label = label
        self.universe = None # to be included on the side of Universe

    def setColor(self, rgb):
        self.colour = Vec3d(rgb[0], rgb[1], rgb[2])

    def setRadius(self, r):
        self.radius = r

    def draw(self):
        scaled_pos = map(distance_scale, self.v_pos)
        scaled_radius = distance_scale(self.radius)

        glTranslatef(*(scaled_pos))
        sphere = gluNewQuadric()
        glColor3f(*(self.colour))
        gluSphere(sphere, scaled_radius, 20, 20)  # (quad, radius, slices, stacks)
        #  slices and stacks are subdivisions along and across the z axis respectively.

    def acceleration(self):
        acceleration_vector = Vec3d(0.0, 0.0, 0.0)
        for star2 in self.universe.stars.values():
            if self.v_pos == star2.v_pos: continue  # do it on ID?
            diff_vector = star2.v_pos.subtract(self.v_pos)
            euclidean_dist = diff_vector.norm()

            force_of_gravity = (G_Newton * self.mass * star2.mass) / (euclidean_dist * euclidean_dist)
            gravity_acc = force_of_gravity / star2.mass  # Newton -> fundamental law of acceleration, inertia
            acceleration_vector = acceleration_vector.add(
                diff_vector.scalar_mult(gravity_acc/euclidean_dist))


        return acceleration_vector


stars = dict()
stars['Earth'] =Star(label  = 'Earth',
                     mass   = 5.9736E+24,
                     radius = 6.371E+6,
                     colour = Vec3d(0.3, 0.3, 1.0),
                     v_pos  = Vec3d(0,0,0),
                     v_vel  = Vec3d(0,0,0))
stars['Moon']  =Star(label  = 'Moon',
                     mass   = 7.3483E+22,
                     radius = 1.7371E+6,
                     colour = Vec3d(0.7,0.7,0.7),
                     v_pos  = Vec3d(0,3.633E+8,0), # perigee, nearest point (where max orbital velocity is achieved)
                     v_vel  = Vec3d(1.076E+3,0,0)) # max orbital velocity


class Universe:
    seconds_elapsed = 0.0
    timeFactor = 43800 # 43800x => 1 month scaled to 1 minute  (1 = realtime)
    #timePause = False  # initial status
    timePause = True  # initial status

    # list of stars with the data in the dictionary so we can switch which is the central star
    # on every "draw()" we centre on the star indexed by "centralStar"
    centralStar = 0 # by default the central star is the first in the list
    starList = [] # so as to have an indexed list to iterate in order

    def __init__(self):
        self.stars = stars
        self.G_Newton = G_Newton

        #print stars.keys()
        for star in stars.keys():
            self.starList.append(star)
            stars[star].universe = self

    def togglePause(self):
        if self.timePause:
            self.timePause = False
        else:
            self.timePause = True
        return self.timePause

    def no_gravity_update(self, dt):
        for star1 in self.stars.values():
            displacement = star1.v_vel.scalar_mult(dt)
            star1.v_pos = star1.v_pos.add(displacement)
        self.seconds_elapsed += dt

    def naive_update(self, dt): # recalculate positions and velocities of each star based on static data
        def velocities_update(time_interval):
            for star1 in self.stars.values():
                acceleration_vector = star1.acceleration()
                star1.v_vel = star1.v_vel.add(acceleration_vector.scalar_mult(time_interval))

        def positions_update(time_interval):
            for star1 in self.stars.values():
                displacement = star1.v_vel.scalar_mult(time_interval)
                star1.v_pos = star1.v_pos.add(displacement)
        positions_update(dt)
        velocities_update(dt)
        self.seconds_elapsed += dt

    def runge_kutta_update(self, dt): # broken at the moment - TODO
        def derivative(tuple_state, tuple_prior, dt_):
            derived = (
                tuple_state[0] + tuple_prior[3] * dt_,
                tuple_state[1] + tuple_prior[4] * dt_,
                tuple_state[2] + tuple_prior[5] * dt_,
                tuple_state[3] + tuple_prior[3],
                tuple_state[4] + tuple_prior[4],
                tuple_state[5] + tuple_prior[5],
                )
            return derived

        for star in stars.keys():
            v_acc = stars[star].acceleration()

            k1 = (stars[star].v_vel[0], stars[star].v_vel[1], stars[star].v_vel[2],
                  v_acc[0], v_acc[1], v_acc[2])
            k2 = derivative(k1, k1, dt * 0.5)
            k3 = derivative(k1, k2, dt * 0.5)
            k4 = derivative(k1, k3, dt)
            ddt = vec(0,0,0,0,0,0)
            for i in xrange(6):
                ddt[i] = 1.0 / 6.0 * (k1[i] + 2.0 * (k2[i] + k3[i]) + k4[i])
            stars[star].v_pos[0] += ddt[0] * dt
            stars[star].v_pos[1] += ddt[1] * dt
            stars[star].v_pos[2] += ddt[2] * dt
            stars[star].v_vel[0] += ddt[3] * dt
            stars[star].v_vel[1] += ddt[4] * dt
            stars[star].v_vel[2] += ddt[5] * dt
            #print k1, k2, k3, k4, ddt[0], ddt[1], ddt[2], ddt[3], ddt[4], ddt[5]
        self.seconds_elapsed += dt

    def centre_stars(self, centre):
        for star in self.stars.values():
            star.v_pos = star.v_pos.subtract(centre)

    def switch_central_star(self):
        self.centralStar += 1
        self.centralStar %= len(stars)

    def __str__(self):
        days_elapsed = self.seconds_elapsed / 86400.0
        years_elapsed = days_elapsed / 365.25
        s = "seconds: " + str(self.seconds_elapsed) + " <=> " +\
            str(days_elapsed) + " days <=> " + str(years_elapsed) + " years"

        for star1 in self.stars.values():
            s += "\n%10s %17s %s" % (star1.label, "position units", star1.v_pos.sexp_str())
            s += "\n%10s %17s %s" % (star1.label, "position meters", star1.v_pos.sexp_str())
            s += "\n%10s %17s %s" % (star1.label, "velocity", star1.v_vel.sexp_str())
            s += "\n%10s %17s %s\n" % (star1.label, "acceleration", star1.acceleration().sexp_str())
        return s


# --------------------------------------------------

if __name__ == '__main__':
    universe = Universe()

    win = window.Window(width=800, height=600)
    # glClearColor(0.0, 0.0, 0.0, 0.0)

    def resetRasterPosition():
        glLoadIdentity()
        glTranslatef(0, 0, -100)

    glPushMatrix()

    def draw():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        universe.centre_stars(centre=stars[universe.starList[universe.centralStar]].v_pos)

        for star in stars.values():
            resetRasterPosition()
            star.draw()


    def iteration(dt):
        ##win.dispatch_events()
        draw()

        # win.flip()
        # dt=clock.tick() * timeFactor
        dt *= universe.timeFactor
        #print "dt:", dt

        if dt > 1E+6:    dt = 1E+6 # limits
        if dt < 1E-6: dt = 1E-6
        if not universe.timePause:
            #universe.no_gravity_update(dt)
            universe.naive_update(dt)
            #universe.runge_kutta_update(dt)


    @win.event
    def resize(width, height):
        ##glPushMatrix()
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1.0  * width / height, 0.1, 1000.0)
        #gluPerspective(fovy,aspect,zNear,zFar)

        #		gluLookAt (0.0, 0.0, 0.0, # position of eye
        #			0.0, 0.0, -1.0, # at, where pointing at
        ##			0.0, 0.0, 0.0, # at, where pointing at
        #			0.0, 1.0, 0.0) # up vector of the camera
        #
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        print "resized"

    win.on_resize = resize


    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == window.key.UP:
            pass
        elif symbol == window.key.DOWN:
            pass
        elif symbol == window.key.LEFT:
            pass
        elif symbol == window.key.RIGHT:
            pass
        elif symbol == window.key.Q:
            pyglet.app.exit()
        elif symbol == window.key.T and not (modifiers & window.key.MOD_SHIFT):
            universe.timeFactor *= 2.0
            print 'time scale *2, now', universe.timeFactor
        elif symbol == window.key.T:
            universe.timeFactor /= 2.0
            print 'time scale /2, now', universe.timeFactor
        elif symbol == window.key.SPACE:
            if universe.togglePause():
                print "PAUSED"
            else:
                print 'RESUMED'
        elif symbol == window.key.S and not (modifiers & window.key.MOD_SHIFT):
            for star in stars.keys():
                stars[star].v_vel = Vec3d(0.0, 0.0, 0.0)
            print 'stopping all velocities to (0,0,0)'
        elif symbol == window.key.M and not (modifiers & window.key.MOD_SHIFT):
            for star in stars.keys():
                stars[star].mass *= 1.1  # 10% increase
                print stars[star].label, "increased its mass a 10%, now it has mass=", stars[star].mass
        elif symbol == window.key.M:
            for star in stars.keys():
                stars[star].mass /= 1.1  # 10% decrease
                print stars[star].label, "decreased its mass a 10%, now it has mass=", stars[star].mass
        elif symbol == window.key.C and not (modifiers & window.key.MOD_SHIFT):
            universe.switch_central_star()
            print '\nrecentring stars on ', universe.starList[universe.centralStar]

        print universe
        draw()


    pyglet.clock.schedule(iteration)
    ###	print "fps:  %d" % clock.get_fps()

    pyglet.app.run()
