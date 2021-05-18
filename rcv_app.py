import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df_cols = ['Candidate_Name', 'Candidate_Party', 'Candidate_ID']
app.layout = html.Div(children=[
    html.H3('Create an interactive Ranked Choice Voting election!'),
    html.Br(),

    html.Div('Candidates: '),
    dash_table.DataTable(
        id = 'show_cands', 
        columns = [{'name' : i, 'id' : i} for i in df_cols], 
        data = [{'Candidate_Name' : 'Example Candidate', 
                'Candidate_Party' : 'Example Party', 
                'Candidate_ID' : '0'}]
    ), 
    
    html.Div([
        dcc.Input(id = 'cand_name', type = 'text', placeholder = 'New Candidate Name'),
        html.Br(),
        dcc.Input(id = 'cand_party', type = 'text', placeholder = 'New Candidate Party'),
        html.Br(),
        html.Button('Add Candidate', id='cand-button'), 
        html.Br()
    ]), 
    html.Br(), 

    html.Div('Ballots: '),
    dash_table.DataTable(
        id = 'show_ballots', 
        columns = [{'name' : i, 'id' : i} for i in range(1, 6)], 
        data = [{1 : 'First Choice', 
                 2 : 'Second Choice', 
                 3 : 'Third Choice', 
                 4 : 'Fourth Choice', 
                 5 : 'Fifth Choice'}]
    ), 
    
    html.Div([
        dcc.Dropdown(id = 'new_first', placeholder = 'Enter First Choice'),
        html.Br(),
        dcc.Dropdown(id = 'new_second', placeholder = 'Enter Second Choice'),
        html.Br(),
        dcc.Dropdown(id = 'new_third', placeholder = 'Enter Third Choice'),
        html.Br(),
        dcc.Dropdown(id = 'new_fourth', placeholder = 'Enter Fourth Choice'),
        html.Br(),
        dcc.Dropdown(id = 'new_fifth', placeholder = 'Enter Fifth Choice'),
        html.Br(),
        html.Button('Add Ballot', id='ballot_button'), 
        html.Br()
    ]), 
    html.Br(),

    dcc.Store(id = 'candidates'), 
    dcc.Store(id = 'ballots')
])

@app.callback(
    Output('candidates', 'data'),
    Input('cand-button', 'n_clicks'),
    State('cand_name', 'value'),
    State('cand_party', 'value'), 
    State('candidates', 'data')
)
def add_cand(n_clicks, c_name, c_party, cands):
    if (c_name is None) or (len(c_name.strip()) == 0):
        return cands
    if (c_party is None) or (len(c_party.strip()) == 0):
        return cands
    
    if cands is None:
        all_candidates = pd.DataFrame(columns = df_cols)
        new_id = 0
    else:
        all_candidates = pd.read_json(cands, orient = 'index')
        max_id = all_candidates['Candidate_ID'].max()
        new_id = max_id + 1
        
    new_cand = pd.Series({'Candidate_Name' : c_name, 'Candidate_Party' : c_party, 'Candidate_ID' : new_id})
    return all_candidates.append(new_cand, ignore_index = True).to_json(orient = 'index')

@app.callback(
    Output('show_cands', 'data'),
    Input('candidates', 'data'), 
    State('show_cands', 'data')
)
def update_candidates(cands, tbl_cands):
    if cands is None:
        return tbl_cands

    new_cands = pd.read_json(cands, orient = 'index').to_dict('records')
    return new_cands

if __name__ == '__main__':
    app.run_server()