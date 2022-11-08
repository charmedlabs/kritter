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


    kapp.layout = []    # define interface layout
    kapp.run()  # Run Server - vizy.local:5000/

