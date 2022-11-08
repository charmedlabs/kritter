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
    text = kritter.Ktext()

    # Define Callbacks
    checkbox.callback()
    def func():
        pass

    checklist.callback()
    def func():
        pass

    dropdownMenu.callback()
    def func():
        pass

    dropdown.callback()
    def func():
        pass

    slider.callback()
    def func():
        pass

    textBox.callback()
    def func():
        pass


    kapp.layout = []    # define interface layout
    kapp.run()  # Run Server - vizy.local:5000/

