'''
Hello world with a button.
“hello world” at top of page
press button, prints counter and message to console
kapp.layout = [“hello world”, button]
'''

import kritter

if __name__ == "__main__":
    kapp = kritter.Kritter()    # Create Kritter server
    style = {"label_width": 3, "control_width": 6}  # general style for page

    button = kritter.Kbutton()
        
    kapp.layout = ["hello world", button]

