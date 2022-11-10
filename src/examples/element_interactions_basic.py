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
    checkbox = kritter.Kcheckbox(value="Is this box checked?")
    checklist = kritter.Kchecklist(options=['First', 'Last', 'Wingdings'])
    dropdownMenu = kritter.KdropdownMenu(options=['Burgundy', 'Magenta', 'Teal'])
    dropdown = kritter.Kdropdown()
    slider = kritter.Kslider()
    textBox = kritter.KtextBox()
    text = kritter.Ktext(placeholder='No callback available, but type here!')  # no callback to be defined

    # Define Callbacks
    @checkbox.callback()
    def func(value):
        message = f"print from checkbox - value = {value}"
        print(message)

    @checklist.callback()
    def func(value):
        message = f"print from checklist - value = {value}"
        print(message)

    @dropdownMenu.callback()
    def func(value):
        message = f"print from dropdownMenu - value = {value}"
        print(message)

    @dropdown.callback()
    def func(value):
        message = f"print from dropdown - value = {value}"
        print(message)

    @slider.callback()
    def func(value):
        message = f"print from slider - value = {value}"
        print(message)

    @textBox.callback()
    def func(value):
        message = '\n'.join([
            "print from textBox",
            f"- value = {value}",
            "- testing - abcdefghijklmnopqrstuvwxyz"])    # TODO: j,x,z did not appear in my console
        print(message)

    # define interface layout
    kapp.layout = [checkbox, checklist, dropdownMenu, dropdown, slider, textBox, text]
    kapp.run()  # Run Server - vizy.local:5000/


