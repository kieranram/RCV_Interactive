import pandas as pd

def promote(data, keeps):
    data = data.query('Candidate == @keeps')
    data.loc[:, 'Rank'] = data.groupby('Ballot_ID').rank()
    
    return data

def remove_lowest(data):
    # Get everybody who got first place votes, figure out what the lowest number attained was. 
    # Multiple people could've gotten that number, so we have to remove all of them. 
    first_counts = data.query('Rank == 1').groupby('Candidate')['Rank'].count()
    
    lowest_count = first_counts.min()
    
    drops = first_counts[first_counts == lowest_count].index.tolist()
    
    keeps = data.query('Candidate != @drops')['Candidate'].unique().tolist()
    
    data = promote(data, keeps)
    
    return data

def iterate_series(data):
    # need to move removed ballots to a special unallocated ballot number
    rounds = data.copy()
    
    r = 1
    rounds.loc[:, 'Round'] = r
    # Can safely remove all candidates who got no 1st place votes. 
    # They can only get a subset of new slots, so will never exceed one already ahead of them
    # Can elimiante anyone not in the top n candidates
    got_first = data.query('Rank == 1')['Candidate'].unique().tolist()
    
    data = promote(data, got_first)
    
    while len(data['Candidate'].unique()) > 1:
        r += 1
        data = remove_lowest(data)
        this_round = data.copy()
        this_round.loc[:, 'Round'] = r
        rounds = rounds.append(this_round)
        
    #df that will say how many votes each person had by round
    #will also show vote share by round
    vote_shares = rounds.query('Rank == 1').groupby(['Candidate', 'Round'], as_index = False)['Ballot_ID'].count().sort_values('Ballot_ID')
    vote_shares = vote_shares.rename(columns = {'Ballot_ID' : 'n_ballots'})
    vote_shares.loc[:, 'Percent'] = vote_shares['n_ballots']/vote_shares['Round'].map(vote_shares.groupby('Round')['n_ballots'].sum())
    
    return rounds, vote_shares

def make_rounds(rcv, shares):
    
    by_round = shares.sort_values(['Round', 'n_ballots'], ascending = [True, False]).reset_index(drop = True)
    
    get_cr = lambda x: f'Candidate : {x["Candidate"]}\nRound : {x["Round"]}'
    by_round['CR'] = by_round.apply(get_cr, axis = 1)
    by_round.loc[:, 'Order'] = by_round.index

    progression = rcv.query('Rank == 1').pivot(index = 'Ballot_ID', columns = 'Round', values = 'Candidate')
    
    n_rounds = progression.columns.max() 

    all_rounds = pd.DataFrame(columns = ['Number', 'Start', 'End', 'Start_Round', 'End_Round'])

    for i in range(1, n_rounds):
        transitions = progression[[i, i+ 1]]

        current_round = transitions.groupby([i, i + 1]).apply(len)
        current_round.name = 'Number'
        current_round.index.names = ['Start', 'End']
        current_round = current_round.reset_index()

        current_round.loc[:, 'Start_Round'] = i
        current_round.loc[:, 'End_Round'] = i + 1
        all_rounds = all_rounds.append(current_round)

    all_rounds = all_rounds.reset_index(drop = True)
    
    all_rounds.loc[:, 'Start_Ind'] = all_rounds.merge(by_round, left_on = ['Start', 'Start_Round'], 
                                                  right_on = ['Candidate', 'Round'], how = 'left')['Order']
    all_rounds.loc[:, 'End_Ind'] = all_rounds.merge(by_round, left_on = ['End', 'End_Round'], 
                                                  right_on = ['Candidate', 'Round'], how = 'left')['Order']
    
    all_rounds.to_csv('all_rounds.csv')
    by_round.to_csv('by_round.csv')
    return all_rounds, by_round