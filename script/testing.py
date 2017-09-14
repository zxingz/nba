import plotly.offline as py
import plotly.graph_objs as go

trace1 = go.Area(
    r=[2, 8, 0, 6, 0, 0, 1, 0],
    t=['3pt', '2pt', 'ft', 'reb', 'blk', 'stl', 'to', 'ast'],
    name='S. Ibaka (PF) 31m-22',
    marker=dict(
        color='rgb(106,81,163)'
    )
)
trace2 = go.Area(
    r=[3, 5, 3, 6, 0, 1, 2, 6],
    t=['3pt', '2pt', 'ft', 'reb', 'blk', 'stl', 'to', 'ast'],
    name='A. Gordon (PF) 32m-22',
    marker=dict(
        color='rgb(158,154,200)'
    )
)
data = [trace1, trace2]
layout = go.Layout(
    title='Magic',
    font=dict(
        size=16
    ),
    legend=dict(
        font=dict(
            size=16
        )
    ),
    radialaxis=dict(
        ticksuffix='%'
    ),
    orientation=270
)
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='/home/vishnu/Elements/CodingEnv/data/nba/20170102/polar-area-chart.html')