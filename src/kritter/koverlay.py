#
# This file is part of Kritter 
#
# All Kritter source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Kritter source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

from dash_devices.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from functools import wraps

OVERLAY_WIDTH_HEIGHT = 10000

class Koverlay:
    def __init__(self, underlay, kapp, service):
        self.underlay_style = underlay.style
        self.service = service
        self.kapp = kapp
        self.id = self.kapp.new_id("overlay")
        self.shapes = []
        self.annotations = []
        self.graphs = []
        self.figure = dict(
            layout=dict(
                showlegend=False,
                hovermode='closest',
                xpad=0,
                ypad=0,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, b=0, t=0, r=0),  
                xaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[0, OVERLAY_WIDTH_HEIGHT-1]),
                yaxis=dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[0, OVERLAY_WIDTH_HEIGHT-1])
            )
        )
        self.overlay = dcc.Graph(id=self.id, figure=self.figure, config={'displayModeBar': False}, style=self.style())
        self.div = html.Div(self.overlay, id=self.id+'-od')
        self.layout = html.Div([underlay, self.div], style={"position": "relative"})

    def style(self):
        style = {"position": "absolute", "top": "0px", "left": "0px"}
        style.update(self.underlay_style)
        return style

    def update_resolution(self, width, height):
        self.width = width
        self.figure['layout']['xaxis'] = dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[0, self.width-1])
        self.height = height
        self.figure['layout']['yaxis'] = dict(zeroline=False, showticklabels=False, fixedrange=True, showgrid=False, range=[self.height-1, 0])
        return self.out_draw()

    def callback_draw(self, state=()):
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, "relayoutData")], state, self.service)
            def _func(*args):
                try:
                    return func(args[0]['shapes'][-1], *args[1:])
                except KeyError:
                    pass
        return wrap_func

    def callback_hover(self, state=(), unhover=True):
        self.overlay.clear_on_unhover = unhover
        def wrap_func(func):
            @wraps(func)
            @self.kapp.callback(None,
                [Input(self.id, "hoverData")], state, self.service)
            def _func(*args):
                return func(*args)
        return wrap_func

    def draw_circle(self, x_center, y_center, radius, fillcolor="gray", line=None, editable=False, id=None):
        circle = dict(type="circle", xref="x", yref="y", x0=x_center-radius, x1=x_center+radius, y0=y_center-radius, y1=y_center+radius, fillcolor=fillcolor, editable=editable, id=id)
        if line:
            circle['line'] = line
        self.shapes.append(circle)

    def draw_line(self, x0, y0, x1, y1, line={}, editable=False, id=None):
        line__ = dict(color="gray", width=2)
        line__.update(line)
        line_ = dict(type="line", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1, line=line__, editable=editable, id=id)
        self.shapes.append(line_)
    
    def draw_rect(self, x0, y0, x1, y1, fillcolor="gray", line=None, editable=False, id=None):
        rect = dict(type="rect", xref="x", yref="y", x0=x0, y0=y0, x1=x1, y1=y1, fillcolor=fillcolor, editable=editable, id=id)
        if line:
            rect['line'] = line
        self.shapes.append(rect)
   
    def draw_shape(self, points, fillcolor="gray", line=None, editable=False, id=None):
        try:
            for i, p in enumerate(points):
                if i==0:
                    path = "M "
                else:
                    path += " L "
                path += f"{p[0]} {p[1]}"
            path += " Z"
        except:
            raise RuntimeError(f"draw_shape() points in wrong format -- need to be [(x0, y0), (x1, y1), ...]. You passed: {points}")

        shape = dict(type="path", xref="x", yref="y", path=path, fillcolor=fillcolor, editable=editable, id=id)
        if line:
            shape['line'] = line
        self.shapes.append(shape)
    
    def draw_text(self, x0, y0, text, font={}, fillcolor="white", padding=2, xanchor="center", yanchor="center", id=None):
        font_ = dict(family="sans serif", size=16, color="gray")
        font_.update(font)
        text_ = dict(text=text, x=x0, y=y0, xref="x", yref="y", font=font, showarrow=False, borderwidth=0, borderpad=padding, bgcolor=fillcolor, xanchor=xanchor, yanchor=yanchor, id=id)
        self.annotations.append(text_)

    # rect, line, circle, openpath, closedpath
    def draw_user(self, shape, fillcolor="gray", line=None):
        if not shape:
            self.figure['layout']['dragmode'] = None
        else: 
            self.figure['layout']['dragmode'] = f"draw{shape}" 
        self.figure['layout']['newshape'] = dict(line=line, fillcolor=fillcolor)

    def draw_clear(self, id=None):
        self.draw_clear_shapes(id)
        self.draw_clear_annotations(id)
        self.draw_clear_graphs(id)
    
    def draw_clear_shapes(self, id=None):
        if id is None:
            self.shapes = []
        else:
            self.shapes = [s for s in self.shapes if s['id']!=id]
   
    def draw_clear_annotations(self, id=None):
        if id is None:
            self.annotations = []
        else:
            self.annotations = [s for s in self.annotations if s['id']!=id]
    
    def draw_clear_graphs(self, id=None):
        if id is None:
            self.graphs = []
        else:
            self.graphs = [g for g in self.graphs if g.uid!=id]
    
    def draw_graph(self, graph, id=None):
        graph.uid = id
        self.graphs.append(graph)

    def out_style(self, underlay_style):
        self.underlay_style = underlay_style
        return [Output(self.id, "style", self.style())]

    def out_draw(self):
        self.figure['layout']['shapes'] = self.shapes
        self.figure['layout']['annotations'] = self.annotations
        self.figure['data'] = self.graphs        
        return [Output(self.id, "figure", self.figure)]  

    def out_disp(self, disp):
        if disp:
            return [Output(self.div.id, "style", {"display": "block"})]
        else:
            return [Output(self.div.id, "style", {"display": "none"})]
