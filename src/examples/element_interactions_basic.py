'''
Elements - kcheckbox, kchecklist, kdropdownmenu, kdropdown, kslider, ktextbox, ktext.  

Each element, except ktext, gets a callback that prints to console. 
message = 'print from 'element name'

dropdown and checklist elements have a list of bogus options 
- 3 or 4 colors for example
'''

# imports
import kritter

if __name__ == "__main__":

    # Create Kritter server before defining compenents
    kapp = kritter.Kritter()

    # Application Styles
    main_style = {"label_width": 3, "control_width": 6}

    # Contents/Components of Application
    checkbox = kritter.Kcheckbox()
    checklist = kritter.Kchecklist()
    dropdownMenu = kritter.KdropdownMenu()
    dropdown = kritter.Kdropdown()
    slider = kritter.Kslider()
    textBox = kritter.KtextBox()
    text = kritter.Ktext()  # no callback to be defined

    # Define Callbacks
    @checkbox.callback()
    def func():
        message = "print from checkbox"
        print(message)

    @checklist.callback()
    def func():
        message = "print from checklist"
        print(message)

    @dropdownMenu.callback()
    def func():
        message = "print from dropdownMenu"
        print(message)

    @dropdown.callback()
    def func():
        message = "print from dropdown"
        print(message)

    @slider.callback()
    def func():
        message = "print from slider"
        print(message)

    @textBox.callback()
    def func():
        message = "print from textBox"
        print(message)

    # define interface layout
    kapp.layout = [checkbox, checklist, dropdownMenu, dropdown, slider, textBox, text]
    kapp.run()  # Run Server - vizy.local:5000/


