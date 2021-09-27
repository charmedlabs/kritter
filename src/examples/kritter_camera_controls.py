from threading import Thread
import kritter
from dash_devices.dependencies import Output
import dash_bootstrap_components as dbc
import dash_html_components as html

# Frame grabbing thread
def grab(video, stream, run):
    while run():
        # Get frame
        frame = stream.frame()
        # Send frame
        video.push_frame(frame)


if __name__ == "__main__":
    # Create and start camera.
    camera = kritter.Camera(hflip=True, vflip=True)
    stream = camera.stream()

    # Create Kritter server.
    kapp = kritter.Kritter()
    style = {"label_width": 3, "control_width": 6}
     # Create video component.
    video = kritter.Kvideo(width=camera.resolution[0], height=camera.resolution[1])
    hist_enable = kritter.Kcheckbox(name='Histogram', value=False, style=style)
    mode = kritter.Kdropdown(name='Camera mode', options=camera.getmodes(), value=camera.mode, style=style)
    brightness = kritter.Kslider(name="Brightness", value=camera.brightness, mxs=(0, 100, 1), format=lambda val: '{}%'.format(val), style=style)
    framerate = kritter.Kslider(name="Framerate", value=camera.framerate, mxs=(camera.min_framerate, camera.max_framerate, 1), format=lambda val : '{} fps'.format(val), style=style)
    autoshutter = kritter.Kcheckbox(name='Auto-shutter', value=camera.autoshutter, style=style)
    shutter = kritter.Kslider(name="Shutter-speed", value=camera.shutter_speed, mxs=(.0001, 1/camera.framerate, .0001), format=lambda val: '{:.4f} s'.format(val), style=style)
    shutter_cont = dbc.Collapse(shutter, id=kapp.new_id(), is_open=not camera.autoshutter, style=style)
    awb = kritter.Kcheckbox(name='Auto-white-balance', value=camera.awb, style=style)
    red_gain = kritter.Kslider(name="Red gain", value=camera.awb_red, mxs=(0.05, 2.0, 0.01), style=style)
    blue_gain = kritter.Kslider(name="Blue gain", value=camera.awb_red, mxs=(0.05, 2.0, 0.01), style=style)
    awb_gains = dbc.Collapse([red_gain, blue_gain], id=kapp.new_id(), is_open=not camera.awb)            

    @hist_enable.callback()
    def func(value):
        return video.out_hist_enable(value)

    @brightness.callback()
    def func(value):
        camera.brightness = value

    @framerate.callback()
    def func(value):
        camera.framerate = value
        return shutter.out_value(camera.shutter_speed) + shutter.out_max(1/camera.framerate)

    @mode.callback()
    def func(value):
        camera.mode = value
        return video.out_width(camera.resolution[0]) + video.out_height(camera.resolution[1]) + framerate.out_value(camera.framerate) + framerate.out_min(camera.min_framerate) + framerate.out_max(camera.max_framerate)

    @autoshutter.callback()
    def func(value):
        camera.autoshutter = value
        return Output(shutter_cont.id, 'is_open', not value)

    @shutter.callback()
    def func(value):
        camera.shutter_speed = value    

    @awb.callback()
    def func(value):
        camera.awb = value
        return Output(awb_gains.id, 'is_open', not value)

    @red_gain.callback()
    def func(value):
        camera.awb_red = value

    @blue_gain.callback()
    def func(value):
        camera.awb_blue = value

    controls = html.Div([hist_enable, mode, brightness, framerate, autoshutter,shutter_cont, awb, awb_gains])

    # Add video component and controls to layout.
    kapp.layout = [video, controls]

    # Run camera grab thread.
    run_grab = True
    grab_thread = Thread(target=grab, args=(video, stream, lambda: run_grab))
    grab_thread.start()

    # Run Kritter server, which blocks.
    kapp.run()
    run_grab = False
