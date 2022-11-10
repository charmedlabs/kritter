'''
Hello World with a button.
“hello world” at top of page
press button, prints counter and message to console
kapp.layout = [“hello world”, button]
'''

# imports
import kritter

counter = 0

if __name__ == "__main__":

    # Create Kritter server - server is created before components
    kapp = kritter.Kritter()    

    # Application Styles
    main_style = {"label_width": 3, "control_width": 6}

    # Contents/Components of Application
    header = kritter.Ktext(value="Hello World!", style=main_style)
    display = kritter.Ktext(value="", style=main_style)   # empty text box until button action
    # Incrementor Button
    button_icon = kritter.Kritter.icon("save")
    button = kritter.Kbutton(name=[button_icon, "Incrementor"])

    # Define Callbacks for Components
    @button.callback()
    def func():
        global counter  # accessing global variable
        counter += 1    # increment counter before display
        message = f"You have said Hello! ({counter}) number of times"
        mods = display.out_value(message)   # update contents of 'display' compenent
        kapp.push_mods(mods)                # apply updates to app

    kapp.layout = [header, display, button] # define interface layout
    kapp.run()  # Run Server - vizy.local:5000/
