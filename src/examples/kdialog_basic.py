'''
Button causes kdialog to come up.
- some text
- a slider or other simple component
- 'close' button, which is there by default. 
'''

# imports
import kritter

slider_min, slider_max = 1, 100
slider_step = 1
slider_mean_value = lambda: int(sum([slider_min, slider_max]) // 2)
slider_start_value = slider_mean_value()

if __name__ == "__main__":

    # Create Kritter server before defining compenents
    kapp = kritter.Kritter()

    # Application Styles
    main_style = {"label_width": 3, "control_width": 6}

    ### Contents/Components of Application
    # Dialog
    # format=lambda x: f"{x}T", 
    slider = kritter.Kslider(name="Slider", value=slider_start_value, mxs=(slider_min, slider_max, slider_step), style=main_style)
    reset_button_icon = kritter.Kritter.icon("bomb")
    reset_button = kritter.Kbutton(name=[reset_button_icon, "Reset Slider"])
    dialog = kritter.Kdialog(title="Example Dialog", layout=[slider, reset_button])
    # Button to open Dialog
    button_icon = kritter.Kritter.icon("gear")
    button = kritter.Kbutton(name=[button_icon, "Open Dialog"])

    # Define Component Callbacks
    @button.callback()
    def func():
        '''display dialog when clicked'''
        mods = []
        # button.out_spinner_disp(True)
        # return dialog.out_open(True)  # works but throws error "Exception: ['_none.0'] callback(s) are part of shared callback chain, but are not shared."
        kapp.push_mods(dialog.out_open(True))

    @reset_button.callback()
    def func():
        '''sets slider value to center'''
        # TODO: slider min,max not accessible ?
        value = slider_mean_value()
        kapp.push_mods(slider.out_value(value))

    kapp.layout = [button, dialog]  # define interface layout
    kapp.run()  # Run Server - vizy.local:5000/

