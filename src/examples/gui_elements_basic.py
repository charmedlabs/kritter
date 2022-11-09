'''
3 kdropdown menus, 1 kbutton, 1 ktextbox: 
- appear/disappear dropdown causes button to appear and disappear. 
- enabled/disabled causes button to be enabled/disabled.  
- spinner/no spinner causes the button to show spinner, not show spinner. 
- when the button is clicked, if ktextbox not empty, will create a new browser tab with the URL from the textbox value.
'''

# imports
import kritter
import dash_bootstrap_components as dbc

if __name__ == "__main__":

    # Create Kritter server before defining compenents
    kapp = kritter.Kritter()

    # Application Styles
    main_style = {"label_width": 12, "control_width": 12}

    # Contents/Components of Application

    # options = [dbc.DropdownMenuItem(k, id=kapp.new_id(), href="export/"+v[0], target="_blank", external_link=True) for k, v in self.export_map.items()]
    # # We don't want the export funcionality to be shared! (service=None)
    # export = kritter.KdropdownMenu(name="Export data", options=options, service=None)

    header = kritter.Ktext(
        value="Button Controls From Other Elements\n- Visibility, Enabled, Spinner Activation",
        style=main_style)

    # Button Controls
    dropdown_button_visiblity = kritter.KdropdownMenu(options=['invisible', 'visible'])
    dropdown_button_enabler = kritter.KdropdownMenu(options=['enable', 'disable', ])
    dropdown_button_spinner = kritter.KdropdownMenu(options=['no spinner', 'spinner'])
    button_spinner_flag = False
    # Textbox and Button 
    textbox = kritter.KtextBox(placeholder="Placeholder! Will not open URL")
    button_icon = kritter.Kritter.icon("external-link")
    button = kritter.Kbutton(
        name=[button_icon, 'Open URL'], 
        spinner=True,   # spinner exists
        disabled=True,  # start unable to click
        disp=False,     # start invisible
        href="https://www.google.com", 
        external_link=True, 
        target="_blank")     

    @dropdown_button_visiblity.callback()
    def func(value):
        '''shows or hides button'''
        # TODO: how to access string values? 
        #       these 'value' variables return integers 0..n
        kapp.push_mods(button.out_disp(bool(value)))

    @dropdown_button_enabler.callback()
    def func(value):
        '''enables or disables button click'''
        kapp.push_mods(button.out_disabled(bool(value)))

    @dropdown_button_spinner.callback()
    def func(value):
        '''shows or hides spinner when button is clicked'''
        # global button_spinner_flag
        # button_spinner_flag = bool(value)
        # print(f"{value} - {button_spinner_flag}")
        kapp.push_mods(button.out_spinner_disp(bool(value)))

    # @textbox.callback()
    # def func():
    #     pass

    @button.callback(textbox.state_value())
    def func(value):
        '''if the textbox not empty, will create a 
        new browser tab with the URL from the textbox value.'''
        global button_spinner_flag
        if button_spinner_flag:
            kapp.push_mods(button.out_spinner_disp(True))
        mods = [button.out_spinner_disp(False)]
        # open link
        url = f"http://vizy.local:5000/{value}"
        mods.append(button.out_url(url))
        kapp.push_mods(mods)
        
    # define interface layout
    kapp.layout = [header, dropdown_button_visiblity, dropdown_button_enabler, dropdown_button_spinner, textbox, button] #, dropdown_button_visiblity, dropdown_button_enabler, button]    
    kapp.run()  # Run Server - vizy.local:5000/
