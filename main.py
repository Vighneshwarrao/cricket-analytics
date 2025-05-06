from fastapi import FastAPI,Query
import pandas as pd

app=FastAPI()

Test_Score=pd.read_csv('Test_Scores.csv')


ODI_Scores=pd.read_csv('ODI_Score.csv')

T20_Score=pd.read_csv('T20_Score.csv')


players=pd.read_csv('Cleaned_datasets/Players.csv')

testteam=players[['Player ID','Player Name','Test Batting Pos','Playing Role','Batting Style','Bowling Style','Bowling Type']].merge(
    Test_Score,on='Player ID',how='outer'
)


def select_test_team(num_batters,num_pacers,num_spinners):
    num_openers = 2
    num_top_order = 1
    num_middle_order = 2
    num_keeper = 1
    num_allrounders = max(0, num_batters - 6)
    num_bowlers = 11 - num_batters

    if (num_bowlers + num_openers + num_top_order + num_allrounders + num_middle_order + num_keeper == 11):

        # Openers Selection
        openers = \
        testteam[testteam['Test Batting Pos'] == 'Openers'].sort_values('Batsmen Score', ascending=False).head(num_openers)[
            'Player Name'].reset_index(drop=True)

        # Top Order Selection
        top_order = \
        testteam[testteam['Test Batting Pos'] == 'Top Order'].sort_values('Batsmen Score', ascending=False).head(num_top_order)[
            'Player Name'].reset_index(drop=True)

        # Middle Order Selection
        middle_order = \
        testteam[testteam['Test Batting Pos'] == 'Middle Order'].sort_values('Batsmen Score', ascending=False).head(
            num_middle_order)['Player Name'].reset_index(drop=True)

        # Keeper Selection
        Keeper = testteam[
            (testteam['Test Batting Pos'] == 'Middle Order') & (testteam['Playing Role'] == 'Wicketkeeper Batter')].sort_values(
            'Keeper Score', ascending=False).head(num_keeper)['Player Name'].reset_index(drop=True)

        # Allrounder Selection
        all_pace = testteam[((testteam['Playing Role'] == 'Allrounder') | (testteam['Playing Role'] == 'Bowling Allrounder') | (
                    testteam['Playing Role'] == 'Batting Allrounder')) & (
                            testteam['Bowling Type'].str.contains('Pacer'))].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)
        all_spin = testteam[((testteam['Playing Role'] == 'Allrounder') | (testteam['Playing Role'] == 'Bowling Allrounder') | (
                    testteam['Playing Role'] == 'Batting Allrounder')) & (testteam['Bowling Type'] == 'Spin')].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)

        allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False)

        rem_pacers = num_pacers - sum(allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(allr['Bowling Type'] == 'Spin')
        print(allr)

        if rem_spinners < 0:
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_spinners)
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head((num_allrounders - num_spinners))
            rem_spinners = num_spinners - sum(all_spin['Bowling Type'] == 'Spin')
            rem_pacers = num_pacers - sum(all_pace['Bowling Type'].str.contains('Pacer'))

        if rem_pacers < 0:
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head(num_pacers)
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_allrounders - num_pacers)

        final_allr = all_pace.merge(all_spin, how='outer').sort_values([ 'Batsmen Score','Allrounder Score'],ascending=False).head(
            num_allrounders)
        final_allr.sort_values('Batsmen Score', ascending=False)
        allrounders = list(final_allr['Player Name'])
        print(allrounders)

        rem_pacers = num_pacers - sum(final_allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(final_allr['Bowling Type'] == 'Spin')

        # Pacer Selection
        pacers = testteam[(testteam['Playing Role'] == 'Bowler') & (testteam['Bowling Type']).str.contains('Pacer')].sort_values(
            'Bowler Score', ascending=False).head(rem_pacers).reset_index(drop=True)

        # Spinner Selection
        spinners = testteam[(testteam['Playing Role'] == 'Bowler') & (testteam['Bowling Type'] == 'Spin')].sort_values(
            'Bowler Score', ascending=False).head(rem_spinners).reset_index(drop=True)

        # bowlers
        bowlers = pacers.merge(spinners, how='outer').sort_values('Batsmen Score')['Player Name'].reset_index(drop=True)

        # Final Team
        final_xi = list(openers) + list(top_order) + list(middle_order) + list(Keeper) + allrounders + list(bowlers)
        return final_xi

@app.get('/test_team')
def test_team(
        bat: int = Query(8, ge=6, le=11),
        pace : int=Query(3,ge=2,le=5),
        spin : int = Query(2,ge=2,le=5)
):
    final_xi = select_test_team(bat,pace,spin)
    df1=pd.read_excel('Cleaned_datasets/Test.xlsx',usecols=['Player ID','Avg'])
    batsmens=df1.merge(players[['Player ID','Player Name']],on='Player ID')
    batsmens.fillna(0,inplace=True)
    batting_Score = sum(batsmens[batsmens['Player Name'].isin(final_xi)]['Avg'])
    return {'team':final_xi,'Avg Score':batting_Score}

oditeam=players[['Player ID','Player Name','ODI Batting Pos','Playing Role','Batting Style','Bowling Style','Bowling Type']].merge(
    ODI_Scores,on='Player ID',how='outer')

def select_odi_team(num_batters,num_pacers,num_spinners): #8 3 2
    num_openers = 2
    num_top_order = 1
    num_middle_order = 1
    num_keeper = 1
    num_allrounders = max(0, num_batters - 5)
    num_bowlers = 11 - num_batters


    if (num_bowlers + num_openers + num_top_order + num_allrounders + num_middle_order + num_keeper == 11):

        # Openers Selection
        openers = oditeam[oditeam['ODI Batting Pos'] == 'Openers'].sort_values('Batsmen Score', ascending=False).head(
            num_openers)['Player Name'].reset_index(drop=True)

        # Top Order Selection
        top_order = \
        oditeam[oditeam['ODI Batting Pos'] == 'Top Order'].sort_values('Batsmen Score', ascending=False).head(
            num_top_order)['Player Name'].reset_index(drop=True)

        # Middle Order Selection
        middle_order = oditeam[(oditeam['ODI Batting Pos'] == 'Middle Order') & (
                    oditeam['Playing Role'] != 'Wicketkeeper Batter')].sort_values('Batsmen Score',
                                                                                   ascending=False).head(
            num_middle_order)['Player Name'].reset_index(drop=True)

        # Keeper Selection
        Keeper = oditeam[(oditeam['ODI Batting Pos'] == 'Middle Order') & (
                    oditeam['Playing Role'] == 'Wicketkeeper Batter')].sort_values('Keeper Score',
                                                                                   ascending=False).head(num_keeper)[
            'Player Name'].reset_index(drop=True)

        # Allrounder Selection
        all_pace = oditeam[((oditeam['Playing Role'] == 'Allrounder') | (
                    oditeam['Playing Role'] == 'Bowling Allrounder') | (
                                        oditeam['Playing Role'] == 'Batting Allrounder')) & (
                               oditeam['Bowling Type'].str.contains('Pacer'))].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)
        all_spin = oditeam[((oditeam['Playing Role'] == 'Allrounder') | (
                    oditeam['Playing Role'] == 'Bowling Allrounder') | (
                                        oditeam['Playing Role'] == 'Batting Allrounder')) & (
                                       oditeam['Bowling Type'] == 'Spin')].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)

        allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False)

        rem_pacers = num_pacers - sum(allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(allr['Bowling Type'] == 'Spin')
        print(allr, rem_pacers, rem_spinners)

        if rem_spinners < 0:
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_spinners)
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head((num_allrounders - num_spinners))
            rem_spinners = num_spinners - sum(all_spin['Bowling Type'] == 'Spin')
            rem_pacers = num_pacers - sum(all_pace['Bowling Type'].str.contains('Pacer'))

        if rem_pacers < 0:
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head(num_pacers)
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_allrounders - num_pacers)

        final_allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False).head(
            num_allrounders)
        final_allr.sort_values('Batsmen Score', ascending=False)
        allrounders = list(final_allr['Player Name'])

        rem_pacers = num_pacers - sum(final_allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(final_allr['Bowling Type'] == 'Spin')

        # Pacer Selection
        pacers = oditeam[
            (oditeam['Playing Role'] == 'Bowler') & (oditeam['Bowling Type']).str.contains('Pacer')].sort_values(
            'Bowler Score', ascending=False).head(rem_pacers).reset_index(drop=True)

        # Spinner Selection
        spinners = oditeam[(oditeam['Playing Role'] == 'Bowler') & (oditeam['Bowling Type'] == 'Spin')].sort_values(
            'Bowler Score', ascending=False).head(rem_spinners).reset_index(drop=True)

        # bowlers
        bowlers = pacers.merge(spinners, how='outer').sort_values('Batsmen Score')['Player Name'].reset_index(drop=True)

        # Final oditeam
        final_XI = list(openers) + list(top_order) + list(middle_order) + list(Keeper) + allrounders + list(bowlers)
        return final_XI
@app.get('/odi_team')
def odi_team(bat: int = Query(7, ge=6, le=11),
        pace : int=Query(4,ge=1,le=5),
        spin : int = Query(2,ge=1,le=5)):
    final_xi = select_odi_team(bat,pace,spin)
    df1=pd.read_excel('Cleaned_datasets/ODI.xlsx',usecols=['Player ID','Avg'])
    batsmens=df1.merge(players[['Player ID','Player Name']],on='Player ID')
    batsmens.fillna(0,inplace=True)
    batting_Score = sum(batsmens[batsmens['Player Name'].isin(final_xi)]['Avg'])
    return {'team':final_xi,'Avg Score':batting_Score}

t20team=players[['Player ID','Player Name','T20I Batting Pos','Playing Role','Batting Style','Bowling Style','Bowling Type']].merge(
    T20_Score,on='Player ID',how='outer'
)

def select_t20_team(num_batters,num_pacers,num_spinners):
    num_openers = 2
    num_top_order = 1
    num_middle_order = 2
    num_keeper = 1
    num_allrounders = max(0, num_batters - 6)
    num_bowlers = 11 - num_batters


    if (num_bowlers + num_openers + num_top_order + num_allrounders + num_middle_order + num_keeper == 11):

        # Openers Selection
        openers = t20team[t20team['T20I Batting Pos'] == 'Openers'].sort_values('Batsmen Score', ascending=False).head(
            num_openers)['Player Name'].reset_index(drop=True)

        # Top Order Selection
        top_order = \
        t20team[t20team['T20I Batting Pos'] == 'Top Order'].sort_values('Batsmen Score', ascending=False).head(
            num_top_order)['Player Name'].reset_index(drop=True)

        # Middle Order Selection
        middle_order = t20team[(t20team['T20I Batting Pos'] == 'Middle Order') & (
            ~t20team['Playing Role'].str.contains('Allrounder', na=False)) & (
                                           t20team['Playing Role'] != 'Wicketkeeper Batter')].sort_values(
            'Batsmen Score', ascending=False).head(num_middle_order)['Player Name'].reset_index(drop=True)

        # Keeper Selection
        Keeper = t20team[(t20team['T20I Batting Pos'] == 'Middle Order') & (
                    t20team['Playing Role'] == 'Wicketkeeper Batter')].sort_values('Keeper Score',
                                                                                   ascending=False).head(num_keeper)[
            'Player Name'].reset_index(drop=True)

        # Allrounder Selection
        all_pace = t20team[((t20team['Playing Role'] == 'Allrounder') | (
                    t20team['Playing Role'] == 'Bowling Allrounder') | (
                                        t20team['Playing Role'] == 'Batting Allrounder')) & (
                               t20team['Bowling Type'].str.contains('Pacer'))].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)
        all_spin = t20team[((t20team['Playing Role'] == 'Allrounder') | (
                    t20team['Playing Role'] == 'Bowling Allrounder') | (
                                        t20team['Playing Role'] == 'Batting Allrounder')) & (
                                       t20team['Bowling Type'] == 'Spin')].sort_values(
            ['Allrounder Score', 'Batsmen Score'], ascending=False).head(num_allrounders).reset_index(drop=True)

        allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False)

        rem_pacers = num_pacers - sum(allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(allr['Bowling Type'] == 'Spin')
        print(allr, rem_pacers, rem_spinners)

        if rem_spinners < 0:
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_spinners)
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head((num_allrounders - num_spinners))
            rem_spinners = num_spinners - sum(all_spin['Bowling Type'] == 'Spin')
            rem_pacers = num_pacers - sum(all_pace['Bowling Type'].str.contains('Pacer'))

        if rem_pacers < 0:
            all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head(num_pacers)
            all_spin = allr[allr['Bowling Type'] == 'Spin'].head(num_allrounders - num_pacers)

        final_allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False).head(
            num_allrounders)
        final_allr.sort_values('Batsmen Score', ascending=False)
        allrounders = list(final_allr['Player Name'])

        rem_pacers = num_pacers - sum(final_allr['Bowling Type'].str.contains('Pacer'))
        rem_spinners = num_spinners - sum(final_allr['Bowling Type'] == 'Spin')

        # Pacer Selection
        pacers = t20team[
            (t20team['Playing Role'] == 'Bowler') & (t20team['Bowling Type']).str.contains('Pacer')].sort_values(
            'Bowler Score', ascending=False).head(rem_pacers).reset_index(drop=True)

        # Spinner Selection
        spinners = t20team[(t20team['Playing Role'] == 'Bowler') & (t20team['Bowling Type'] == 'Spin')].sort_values(
            'Bowler Score', ascending=False).head(rem_spinners).reset_index(drop=True)

        # bowlers
        bowlers = pacers.merge(spinners, how='outer').sort_values('Batsmen Score')['Player Name'].reset_index(drop=True)

        # Final t20team
        final_XI = list(openers) + list(top_order) + list(middle_order) + list(Keeper) + allrounders + list(bowlers)
        print(final_XI)
        return final_XI

@app.get('/t20_team')
def t20_team(bat: int = Query(8, ge=6, le=11),
        pace : int=Query(3,ge=1,le=5),
        spin : int = Query(2,ge=1,le=5)):
    final_XI=select_t20_team(bat,pace,spin)
    df1 = pd.read_excel('Cleaned_datasets/T20.xlsx', usecols=['Player ID', 'Avg'])
    batsmens = df1.merge(players[['Player ID', 'Player Name']], on='Player ID')
    batsmens.fillna(0, inplace=True)
    batting_Score = sum(batsmens[batsmens['Player Name'].isin(final_XI)]['Avg'])
    return {'team': final_XI, 'Avg Score': batting_Score*0.6}