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
    main_style = {"label_width": 3, "control_width": 6}

    # Contents/Components of Application

    # options = [dbc.DropdownMenuItem(k, id=kapp.new_id(), href="export/"+v[0], target="_blank", external_link=True) for k, v in self.export_map.items()]
    # # We don't want the export funcionality to be shared! (service=None)
    # export = kritter.KdropdownMenu(name="Export data", options=options, service=None)

    dropdown_button_visiblity = kritter.Kdropdown(options=['visible', 'invisible'])
    dropdown_button_enabler = kritter.Kdropdown(options=['enable', 'disable'])
    dropdown_button_spinner = kritter.Kdropdown(options=['spinner', 'no spinner'])
    dropdown_menu_main = kritter.KdropdownMenu(
        options=[dropdown_button_visiblity, dropdown_button_enabler, dropdown_button_spinner]
    )
    textbox = kritter.KtextBox(placeholder="Type Here!")
    button_icon = kritter.Kritter.icon("window")
    button = kritter.Kbutton()

    @dropdown_button_visiblity
    def func():
        '''shows or hides button'''
        pass

    @dropdown_button_enabler
    def func():
        '''enables or disables button click'''
        pass

    @dropdown_button_spinner
    def func():
        '''shows or hides spinner when button is clicked'''
        pass

    @button.callback()
    def func():
        '''when clicked, opens a new url tab 
        with contents of textbox as the url.
        Does not open a new tab if textbox is blank'''
        pass

    # define interface layout
    kapp.layout = [dropdown_menu_main, dropdown_button_visiblity, dropdown_button_enabler, button]    
    kapp.run()  # Run Server - vizy.local:5000/
