# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                            [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    searchable=True),                                

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=min_payload, max=max_payload, step=100,
                                    marks={int(i): str(i) for i in range(int(min_payload), int(max_payload)+1, 100)},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def get_pie_chart(selected_site):    
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['class'] == 1)]
        site_counts = filtered_df['Launch Site'].value_counts().reset_index()
        site_counts.columns = ['site', 'count'] 
        print(site_counts)  
        fig = px.pie(site_counts, values='count', names='site',
                    title='Total Successful Launches by Site')
        
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class_label', 'count']      
        print(class_counts)  
        fig = px.pie(class_counts, values='count', names='class_label',
                    title=f'Success vs Failure for site {selected_site}')

        fig.show()

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    print(filtered_df)

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Outcome Correlation',
        hover_data=['Launch Site', 'Payload Mass (kg)', 'class']
    )

    fig.update_layout(
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Launch Outcome (0 = Failure, 1 = Success)'
    )
  
    #fig.show()

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

