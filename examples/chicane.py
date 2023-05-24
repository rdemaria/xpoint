import numpy as np
import matplotlib.pyplot as plt

import xpoint as xp


start = xp.Point()
d1start = start.dup.moveby(dx=2)
d1mid = d1start.dup.arcby(angle=-45, dx=1.5, axis="z")
d1mid_b = d1mid.dup.moveby(dy=-0.1)
d1end = d1mid.dup.arcby(angle=-45, dx=1.5, axis="z")
d2start = d1end.dup.moveby(dx=2)
d2mid = d2start.dup.arcby(angle=45, dx=1.5, axis="z")
d2end = d2mid.dup.arcby(angle=45, dx=1.5, axis="z")


def plot_arc(p, angle, dx, steps=100, ax=None, ls="-", color="c"):
    pp = p.dup
    xy = np.zeros((steps+1, 2))
    xy[0] = pp.location[:2]
    for i in range(steps):
        print(angle / steps, dx / steps)
        pp.arcby(angle=angle / steps, dx=dx / steps, axis="z")
        xy[i + 1] = pp.location[:2]
        print(pp, xy[i + 1])
    if ax is None:
        ax = plt.gca()
    ax.plot(xy[:, 0], xy[:, 1], ls=ls, color=color)


def plot_line(p1, p2, ax=None, ls="-", color="k"):
    if ax is None:
        ax = plt.gca()
    xx = np.array([p1.location[0], p2.location[0]])
    yy = np.array([p1.location[1], p2.location[1]])
    ax.plot(xx, yy, ls=ls, color=color)


def plot_point(
    p,
    dd=.4,
    ax=None,
    ls="-",
    marker="o",
    color="krb",
):
    if ax is None:
        ax = plt.gca()
    ax.arrow(
        p.location[0], p.location[1], dd * p.dx[0], dd * p.dx[1], color=color[1]
    )
    ax.arrow(
        p.location[0], p.location[1], dd * p.dy[0], dd * p.dy[1], color=color[2]
    )
    ax.plot([p.location[0]], [p.location[1]], marker=marker, color=color[0])


plt.clf()
ax = plt.gca()
ax.set_aspect("equal")
# ax.set_xlim(-1, 10)
# ax.set_ylim(-5, 5)
ax.grid(True)
ax.set_xlabel("x")
ax.set_ylabel("y")

plot_point(start)
plot_point(d1start)
plot_point(d1mid)
plot_point(d1mid_b)
plot_point(d1end)
plot_point(d2start)
plot_point(d2mid)
plot_point(d2end)
plot_line(start, d1start)
plot_arc(d1start, angle=-90., dx=3, steps=20)
plot_line(d1end, d2start)

plot_arc(d2start, angle=90., dx=3, steps=20)

