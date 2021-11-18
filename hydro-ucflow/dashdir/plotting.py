# This file updates the figures. It is called by app.py

import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objects as go
from PIL import Image

import calculations as calc


def remove_mesh_points(X, Y, h1, h2, K, W, L):
    # This function is used for making flow arrows on the elevation plot.
    # This function removes mesh grid points that are outside the area we want to put arrows.
    h = calc.get_h(
        h1, h2, K, W, L, X[0]
    )  # we need h, because we don't want to plot arrows above h

    # Here we just iterate over our mesh points and see if they are outside of our desired area, and if so set them to None
    if calc.get_h_max(h1, h2, K, W, L) >= 0:
        for i in range(len(X)):
            for j in range(len(X[0])):
                if Y[i][j] > h[j]:
                    X[i][j] = None
                    Y[i][j] = None
    else:
        for i in range(len(X)):
            for j in range(len(X[0])):
                if Y[i][j] > h[j]:
                    X[i][j] = None
                    Y[i][j] = None

    return [X, Y]


def get_topography_line(x, h):
    # This is creating the topography line on the elevation plot. This is a static line at random points I chose that look okay.
    shift = np.array([50, 51, 54, 54, 51, 51, 52, 52, 49, 48])
    x_top = np.arange(0, 900, 100)
    y_top = shift

    topography_line = go.Scatter(
        x=x_top, y=y_top, mode="lines", line=dict(color="Sienna"), name="topography"
    )
    return topography_line


def initialize_elevation_plot(h1, h2, K, W, L, arrow_visibility):
    elevation_plot = go.Figure()

    elevation_plot.add_layout_image(
        # setting the background image of the plot.
        dict(
            source=Image.open("./background.png"),
            xref="x domain",
            yref="y domain",
            x=0,
            y=0,
            sizex=1,
            sizey=1,
            sizing="stretch",
            xanchor="left",
            yanchor="bottom",
            opacity=0.5,
            layer="below",
        )
    )
    elevation_plot.update_xaxes(showgrid=False, zeroline=False)
    elevation_plot.update_yaxes(showgrid=False, zeroline=False)
    # this hrect adds a white box to extend the legend area, to hide an issue with the background image
    elevation_plot.add_hrect(
        xref="paper",
        yref="paper",
        x0=1,
        x1=1.5,
        y0=-15,
        y1=100,
        line_width=0,
        fillcolor="white",
        opacity=1,
    )

    # calculating the values to plot, using the calculations file.
    x = np.linspace(0, L, 1000)
    h = calc.get_h(h1, h2, K, W, L, x)
    d = calc.get_d(h1, h2, K, W, L)

    # initialize traces using .add_trace()
    elevation_plot.add_trace(
        go.Scatter(x=x, y=h, line=dict(color="RoyalBlue"), name="h(x)")
    )  # plot h

    # plot the divide, a line from the ground to the closest intercept of h
    index = min(range(len(x)), key=lambda i: abs(x[i] - d))
    elevation_plot.add_trace(
        go.Scatter(
            x=[d, d],
            y=[0, h[index]],
            mode="lines",
            line=dict(color="Red"),
            name="divide",
        )
    )

    elevation_plot.update_layout(
        xaxis_title="x (m)", yaxis_title="Water Table Elevation (m)"
    )
    elevation_plot.update_xaxes(range=[0, L])
    elevation_plot.update_yaxes(range=[-4, 65])
    elevation_plot.layout.title = "Head Plot"

    if "visible" in arrow_visibility:  # if the checkbox for arrows is clicked
        # quiver plot
        x_quiver = np.linspace(L / 8, L - (L / 8), 8)
        y_quiver = np.linspace(0, (5 / 6) * max(h), 5)  # go to max y value
        X, Y = np.meshgrid(x_quiver, y_quiver)
        X, Y = remove_mesh_points(
            X, Y, h1, h2, K, W, L
        )  # removing mesh points outside of the area we want arrows
        u = calc.get_q(h1, h2, K, W, L, X) * 15  # the arrows are scaled by 15
        v = Y * 0
        # see https://plotly.github.io/plotly.py-docs/generated/plotly.figure_factory.create_quiver.html
        quiver_plot = ff.create_quiver(
            X,
            Y,
            u,
            v,
            arrow_scale=0.3,
            angle=np.pi / (9 * 16),
            name="Q(x)",
            line_color="Teal",
        )
        elevation_plot.add_traces(data=quiver_plot.data)

    # topography line
    elevation_plot.add_trace(get_topography_line(x, h))
    # this is a grey rectangle at the bottom of the plot to represent unpenetrable ground
    elevation_plot.add_hrect(y0=-4, y1=0, line_width=0, fillcolor="grey", opacity=1)

    elevation_plot.update_layout(margin=dict(l=100, r=150, b=50, t=50))

    # an annotation in the plot to display values for each of the parameters.
    text = (
        "<b>h1 = "
        + str(h1)
        + "m<br>h2 = "
        + str(h2)
        + "m<br>K = "
        + str(K)[:4]
        + "m/day<br>W = "
        + str(W)
        + "m/day<br>L = "
        + str(L)
        + "m</b>"
    )
    elevation_plot.add_annotation(
        xref="paper",
        yref="paper",
        x=1,
        y=0,
        text=text,
        showarrow=False,
        xshift=-10,
        yshift=10,
        align="left",
        bgcolor="lightgrey",
    )

    return elevation_plot


def initialize_q_plot(h1, h2, K, W, L):
    q_plot = go.Figure()

    # calculating values for our parameters using the calculations file.
    x = np.linspace(0, L, 1000)
    q = calc.get_q(h1, h2, K, W, L, x)

    # initialize traces using .add_trace()
    # plot q
    q_plot.add_trace(go.Scatter(x=x, y=q, line=dict(color="MediumPurple"), name="Q(x)"))
    # plot the zero line on the graph
    q_plot.add_trace(
        go.Scatter(
            x=[x[0], x[-1]],
            y=[0, 0],
            mode="lines",
            line=dict(color="FireBrick"),
            name="zero",
        )
    )

    q_plot.update_layout(xaxis_title="x (m)", yaxis_title="Q(x) (m\u00B2/day)")
    q_plot.update_xaxes(range=[0, L])
    q_plot.update_yaxes(range=[-100, 100], zeroline=True, zerolinecolor="FireBrick")
    q_plot.layout.title = "Q Plot"

    q_plot.update_layout(margin=dict(l=100, r=150, b=50, t=50))

    return q_plot


def update_elevation_plot(h1, h2, K, W, L, arrow_visibility, elevation_plot):
    # calculating our parameters with the calculations file.
    x = np.linspace(0, L, 1000)
    h = calc.get_h(h1, h2, K, W, L, x)
    d = calc.get_d(h1, h2, K, W, L)

    # Updating specific traces using their index in plot.data
    elevation_plot.data[0].x = x
    elevation_plot.data[0].y = h  # update h trace

    if W != 0:
        elevation_plot.data[1].visible = True
        index = min(range(len(x)), key=lambda i: abs(x[i] - d))
        elevation_plot.data[1].x = [d, d]
        elevation_plot.data[1].y = [0, h[index]]  # update the divide trace
    else:
        elevation_plot.data[1].visible = False

    elevation_plot.update_xaxes(range=[0, L])
    # update the size of the image so when we change L it looks like the background doesn't move
    elevation_plot.update_layout_images(sizex=800 / L)

    # update flow arrows
    if "visible" in arrow_visibility:
        # quiver plot
        x_quiver = np.linspace(L / 8, L - (L / 8), 8)
        y_quiver = np.linspace(0, (5 / 6) * max(h), 5)  # go to max y value
        X, Y = np.meshgrid(x_quiver, y_quiver)
        X, Y = remove_mesh_points(X, Y, h1, h2, K, W, L)
        u = calc.get_q(h1, h2, K, W, L, X) * 15
        v = Y * 0
        quiver_plot = ff.create_quiver(
            X, Y, u, v, arrow_scale=0.3, angle=np.pi / (9 * 16)
        )

        elevation_plot.data[2].x = quiver_plot.data[0].x
        elevation_plot.data[2].y = quiver_plot.data[0].y
    else:
        elevation_plot.data[2].x = []
        elevation_plot.data[2].y = []

    # update topography line
    topography_plot = get_topography_line(x, h)
    elevation_plot.data[3].x = topography_plot.x
    elevation_plot.data[3].y = topography_plot.y

    # update annotation that displays parameter values on the graph
    text = (
        "<b>h1 = "
        + str(h1)
        + "m<br>h2 = "
        + str(h2)
        + "m<br>K = "
        + str(K)[:4]
        + "m/day<br>W = "
        + str(W)
        + "m/day<br>L = "
        + str(L)
        + "m</b>"
    )
    elevation_plot.update_annotations(text=text)

    return elevation_plot


def update_q_plot(h1, h2, K, W, L, q_plot):
    x = np.linspace(0, L, 1000)
    q = calc.get_q(h1, h2, K, W, L, x)

    q_plot.data[0].x = x
    q_plot.data[0].y = q

    q_plot.update_xaxes(range=[0, L])

    return q_plot
