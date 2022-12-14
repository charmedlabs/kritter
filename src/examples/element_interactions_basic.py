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
    checkbox = kritter.Kcheckbox(name='Checkbox', value=False)
    checklist = kritter.Kchecklist(name='Checklist', options=['First', 'Last', 'Wingdings'])
    dropdownMenu = kritter.KdropdownMenu(name='DropdownMenu', options=['Burgundy', 'Magenta', 'Teal'])
    slider = kritter.Kslider(name='Slider', format=lambda val: f"{val}%")
    slider_range = kritter.Kslider(name='Range Slider', range=True)
    dropdown = kritter.Kdropdown(name='Dropdown', options=['', 'Excalibur', 'Gramr', 'The Pen'])
    textBox = kritter.KtextBox(name='TextBox', placeholder='Placeholder!', max=150) # arbitrary max given
    text = kritter.Ktext(name='Text', value='\n'.join([
        'This is a basic Text Element.',
        'No Callback for kText']))

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

    @slider.callback()
    def func(value):
        message = f"print from slider - value = {value}"
        print(message)

    @slider_range.callback()
    def func(value):
        message = f"print from slider_range - value = {value}"
        print(message)

    @dropdown.callback()
    def func(value):
        message = f"print from dropdown - value = {value}"
        print(message)

    @textBox.callback()
    def func(value):
        message = f"print from textBox - value = {value}"
        print(message)

    # define interface layout
    kapp.layout = [checkbox, checklist, dropdownMenu, slider, dropdown, slider_range, textBox, text]
    kapp.run()  # Run Server - vizy.local:5000/


