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
import dash_html_components as html

if __name__ == "__main__":

    # Create Kritter server before defining compenents
    kapp = kritter.Kritter()

    # Application Styles
    main_style = {"label_width": 12, "control_width": 12}

    # Contents/Components of Application
    header = kritter.Ktext(
        value="Button Controls From Other Elements\n- Visibility, Enabled, Spinner Activation",
        style=main_style)
    # Button Controls
    dropdown_button_visiblity = kritter.KdropdownMenu(name='Visibility', options=['invisible', 'visible'])
    dropdown_button_enabler = kritter.KdropdownMenu(name='Enable', options=['enable', 'disable', ])
    dropdown_button_spinner = kritter.KdropdownMenu(name='Spinner', options=['no spinner', 'spinner'])
    button_spinner_flag = False
    # Textbox and Link-Button 
    textbox = kritter.KtextBox(placeholder="Placeholder! Will not open URL")
    button_icon = kritter.Kritter.icon("external-link")
    link_button = kritter.Kbutton(
        name=[button_icon, 'Open URL'], 
        spinner=True,   # spinner exists
        disp=True,     # start visible
        disabled=False,  # start with clicking enabled
        href="", 
        external_link=True, 
        target="_blank")     

    @dropdown_button_visiblity.callback()
    def func(value):
        '''shows or hides button'''
        # TODO: how to access string values? 
        #       these 'value' variables return integers 0..n
        kapp.push_mods(link_button.out_disp(bool(value)))

    @dropdown_button_enabler.callback()
    def func(value):
        '''enables or disables button click'''
        kapp.push_mods(link_button.out_disabled(bool(value)))

    @dropdown_button_spinner.callback()
    def func(value):
        '''shows or hides spinner when button is clicked'''
        # global button_spinner_flag
        # button_spinner_flag = bool(value)
        # print(f"{value} - {button_spinner_flag}")
        # TODO : properly active/deactivate spinner output
        kapp.push_mods(link_button.out_spinner_disp(bool(value)))

    @link_button.callback(textbox.state_value())
    def func(value):
        '''if the textbox not empty, will create a 
        new browser tab with the URL from the textbox value.'''
        global button_spinner_flag
        if button_spinner_flag:
            kapp.push_mods(link_button.out_spinner_disp(True))
        mods = []
        mods += link_button.out_spinner_disp(False)
        url = f"{value}"
        mods += link_button.out_url(url) # open URL in another tab
        kapp.push_mods(mods)
        
    # define interface layout
    control_buttons = html.Div([dropdown_button_visiblity, dropdown_button_enabler, dropdown_button_spinner, ])
    kapp.layout = [header, control_buttons, textbox, link_button] 
    kapp.run()  # Run Server - vizy.local:5000/
