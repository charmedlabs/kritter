'''
Using a regular and a range slider, 
intersect a few different colored squares 
defined using dash's html components

color ideas:
additive, subtractive primary or secondary colors
dropdown menus with color selection
'''

# imports
import kritter
import dash_html_components as html

if __name__ == "__main__":

    # Create Kritter server - server is created before components
    kapp = kritter.Kritter()    

    # Application Styles
    main_style = {"label_width": 3, "control_width": 6}
    background_style = {"label_width": 3, "control_width": 6, 'background-color': 'black'}
    box_style = {'width':'100px', 'height':'100px', } # 'background-color': 'black'}
    # Contents/Components of Application
    header = kritter.Ktext(value="Hello World!", style=main_style)
    # create boxes with primary colors..
    box_r = html.P('Testing, but to be emptied', style=main_style)
    box_g = html.P('Testing, but to be emptied', style=background_style)
    box_b = html.P('Testing, but to be emptied', style=box_style)
    display = [
        box_r,
        # box_g, # if uncommented, webpage will not load | stays on 'loading' page -- <div class="_dash-loading">Loading...</div>
        # box_b, # also stalls on loading page 
    ]
    # define controls
    overlap_slider = kritter.Kslider(name='Overlap', mxs=(0, 100, 1), format=lambda s: f'{s}%') # overlap 0% - 100%
    controls = html.Div([overlap_slider])

    # Define Callbacks for Components
    @overlap_slider.callback()
    def func(value):
        # 0 - 100 % overlap of RGB boxes
        # update relative positions of 'boxes'
        pass

    # define interface layout
    kapp.layout = [
        header, 
        display, 
        controls
    ] 

    # Run Server - vizy.local:5000/
    kapp.run()  
