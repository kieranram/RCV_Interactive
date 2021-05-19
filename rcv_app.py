import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

candidate_cols = ['Candidate_ID', 'Candidate_Name', 'Candidate_Party']
ballot_cols = ['Ballot_ID', 'First Choice', 'Second Choice', 'Third Choice', 'Fourth Choice', 'Fifth Choice']

candidate_form = html.Div([
                    dcc.Input(id = 'cand_name', type = 'text', placeholder = 'New Candidate Name'),
                    dcc.Input(id = 'cand_party', type = 'text', placeholder = 'New Candidate Party'),
                    html.Button('Add Candidate', id='cand-button'), 
                    html.Br()
                ], style = {'float' : 'left', 'width' : '40%'})

ballot_form = html.Div([
                dcc.Dropdown(id = 'first_choice', placeholder = 'Enter First Choice'),
                dcc.Dropdown(id = 'second_choice', placeholder = 'Enter Second Choice', disabled = True),
                dcc.Dropdown(id = 'third_choice', placeholder = 'Enter Third Choice', disabled = True),
                dcc.Dropdown(id = 'fourth_choice', placeholder = 'Enter Fourth Choice', disabled = True),
                dcc.Dropdown(id = 'fifth_choice', placeholder = 'Enter Fifth Choice', disabled = True),
                html.Button('Add Ballot', id='ballot_button'), 
                html.Br()
            ], style = {'width' : '40%'})

candidate_table = dash_table.DataTable(
                    id = 'show_cands', 
                    columns = [{'name' : i, 'id' : i} for i in candidate_cols], 
                    data = [{'Candidate_Name' : 'Example Candidate', 
                            'Candidate_Party' : 'Example Party', 
                            'Candidate_ID' : '0'}]
                    )

ballot_table = dash_table.DataTable(
                id = 'show_ballots', 
                columns = [{'name' : x, 'id' : x} for x in ballot_cols], 
                data = [{x : x for x in ballot_cols}]
            )

app.layout = html.Div(children=[
    html.H3('Create an interactive Ranked Choice Voting election!'),
    html.Br(),
    
    candidate_form,
    html.Br(), html.Br(),
    html.Div('Candidates: '),
    candidate_table, 
    html.Br(),

    ballot_form, 
    html.Br(),
    html.Div('Ballots: '),
    ballot_table, 

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
    # On initial load, or if simply white space is entered, do not accept as valid
    if (c_name is None) or (len(c_name.strip()) == 0):
        return cands
    if (c_party is None) or (len(c_party.strip()) == 0):
        return cands
    
    # If no candidates have yet been created, initialize empty candidate data frame. 
    # Otherwise load candidates into a DataFrame
    if cands is None:
        all_candidates = pd.DataFrame(columns = candidate_cols)
        new_id = 0
    else:
        all_candidates = pd.read_json(cands, orient = 'index')
        max_id = all_candidates['Candidate_ID'].max()
        new_id = max_id + 1
        
    new_cand = pd.Series({'Candidate_Name' : c_name, 'Candidate_Party' : c_party, 'Candidate_ID' : new_id})
    all_candidates = all_candidates.append(new_cand, ignore_index = True)
    return all_candidates.to_json(orient = 'index')

@app.callback(
    Output('ballots', 'data'),
    Input('ballot_button', 'n_clicks'),
    State('first_choice', 'value'),
    State('second_choice', 'value'),
    State('third_choice', 'value'), 
    State('fourth_choice', 'value'),
    State('fifth_choice', 'value'),
    State('ballots', 'data')
)
def add_ballots(n_clicks, first, second, third, fourth, fifth, ballots):
    # On initial load, ballots is None and first is None. Nothing should happen
    if (ballots is None) and (first is None):
        return None

    # If no ballots exist, initialize empty DF. Otherwise load ballots into DF
    if ballots is None:
        all_ballots = pd.DataFrame(columns = ballot_cols)
        new_id = 0
    else:
        all_ballots = pd.read_json(ballots, orient = 'index')
        max_id = all_ballots['Ballot_ID'].max()
        new_id = max_id + 1
    
    # If ballot has no first option, do not add anything to the ballots
    if first is None:
        return all_ballots.to_json(orient = 'index')
    
    # Otherwise create new ballot, add to dataframe and return
    new_ballot = pd.Series({'Ballot_ID' : new_id, 'First Choice' : first, 'Second Choice' : second, 'Third Choice' : third, 
                            'Fourth Choice' : fourth, 'Fifth Choice' : fifth})
    all_ballots = all_ballots.append(new_ballot, ignore_index = True)
    return all_ballots.to_json(orient = 'index')
    

@app.callback(
    Output('show_cands', 'data'),
    Input('candidates', 'data'), 
    State('show_cands', 'data')
)
def update_candidates(cands, tbl_cands):
    # On first load, keep defaults
    if cands is None:
        return tbl_cands

    # In all other cases, return the candidates as a list of dicts
    new_cands = pd.read_json(cands, orient = 'index').to_dict('records')
    return new_cands

@app.callback(
    Output('show_ballots', 'data'), 
    Input('ballots', 'data'), 
    State('show_ballots', 'data'), 
    State('candidates', 'data')
)
def update_ballots(ballots, tbl_ballots, cands):
    # On first load, keep defaults
    if ballots is None:
        return tbl_ballots

    candidates = pd.read_json(cands, orient = 'index')
    cand_map = candidates.set_index('Candidate_ID')['Candidate_Name']
    new_ballots = pd.read_json(ballots, orient = 'index')

    for col in ballot_cols:
        if col == 'Ballot_ID': 
            continue
        new_ballots.loc[:, col] = new_ballots[col].map(cand_map)

    return new_ballots.to_dict('records')

@app.callback(
    Output('first_choice', 'options'), 
    Output('second_choice', 'options'), 
    Output('third_choice', 'options'),
    Output('fourth_choice', 'options'), 
    Output('fifth_choice', 'options'),
    Input('candidates', 'data')
)
def update_options(cands):
    # On load, no options available
    if cands is None:
        return [[] for _ in range(5)]
    get_opts = lambda x: {'label' : x['Candidate_Name'], 'value' : x['Candidate_ID']}
    cand_df = pd.read_json(cands, orient = 'index')
    all_opts = cand_df.apply(get_opts, axis = 1).tolist()
    return [all_opts for _ in range(5)]

@app.callback(
    Output('second_choice', 'disabled'), 
    Input('first_choice', 'value')
)
def activate_second(choice):
    if choice is None:
        return True
    else:
        return False

@app.callback(
    Output('third_choice', 'disabled'),
    Input('second_choice', 'value')
)
def activate_third(choice):
    if choice is None:
        return True
    else:
        return False

@app.callback(
    Output('fourth_choice', 'disabled'),
    Input('third_choice', 'value')
)
def activate_fourth(choice):
    if choice is None:
        return True
    else:
        return False

@app.callback(
    Output('fifth_choice', 'disabled'),
    Input('fourth_choice', 'value')
)
def activate_fifth(choice):
    if choice is None:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run_server()