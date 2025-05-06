import pandas as pd
Score=pd.read_csv('T20_Score.csv')


players=pd.read_csv('Cleaned_datasets/Players.csv')

t20team=players[['Player ID','Player Name','T20I Batting Pos','Playing Role','Batting Style','Bowling Style','Bowling Type']].merge(
    Score,on='Player ID',how='outer'
)
num_batters=8
num_openers=2
num_top_order=1
num_middle_order=2
num_keeper=1
num_allrounders=max(0,num_batters-6)
num_bowlers=11-num_batters

num_pacers=3
num_spinners=2


if(num_bowlers+num_openers+num_top_order+num_allrounders+num_middle_order+num_keeper==11):

    #Openers Selection
    openers=t20team[t20team['T20I Batting Pos']=='Openers'].sort_values('Batsmen Score',ascending=False).head(num_openers)['Player Name'].reset_index(drop=True)

    #Top Order Selection
    top_order=t20team[t20team['T20I Batting Pos']=='Top Order'].sort_values('Batsmen Score',ascending=False).head(num_top_order)['Player Name'].reset_index(drop=True)

    #Middle Order Selection
    middle_order=t20team[(t20team['T20I Batting Pos']=='Middle Order')& (~t20team['Playing Role'].str.contains('Allrounder',na=False)) & (t20team['Playing Role']!='Wicketkeeper Batter')].sort_values('Batsmen Score',ascending=False).head(num_middle_order)['Player Name'].reset_index(drop=True)

    #Keeper Selection
    Keeper=t20team[(t20team['T20I Batting Pos']=='Middle Order') & (t20team['Playing Role']=='Wicketkeeper Batter')].sort_values('Keeper Score',ascending=False).head(num_keeper)['Player Name'].reset_index(drop=True)

    #Allrounder Selection
    all_pace=t20team[((t20team['Playing Role']=='Allrounder') | (t20team['Playing Role']=='Bowling Allrounder') | (t20team['Playing Role']=='Batting Allrounder')) & (t20team['Bowling Type'].str.contains('Pacer'))].sort_values(['Allrounder Score','Batsmen Score'],ascending=False).head(num_allrounders).reset_index(drop=True)
    all_spin=t20team[((t20team['Playing Role']=='Allrounder') | (t20team['Playing Role']=='Bowling Allrounder') | (t20team['Playing Role']=='Batting Allrounder')) & (t20team['Bowling Type']=='Spin')].sort_values(['Allrounder Score','Batsmen Score'],ascending=False).head(num_allrounders).reset_index(drop=True)

    allr=all_pace.merge(all_spin,how='outer').sort_values('Allrounder Score',ascending=False)

    rem_pacers= num_pacers -sum(allr['Bowling Type'].str.contains('Pacer'))
    rem_spinners =  num_spinners - sum(allr['Bowling Type'] == 'Spin')
    print(allr,rem_pacers,rem_spinners)

    if rem_spinners<0 :
        all_spin=allr[allr['Bowling Type']=='Spin'].head(num_spinners)
        all_pace=allr[allr['Bowling Type'].str.contains('Pacer')].head((num_allrounders-num_spinners))
        rem_spinners=num_spinners - sum(all_spin['Bowling Type']=='Spin')
        rem_pacers=num_pacers - sum(all_pace['Bowling Type'].str.contains('Pacer'))

    if rem_pacers<0 :
        all_pace = allr[allr['Bowling Type'].str.contains('Pacer')].head(num_pacers)
        all_spin=allr[allr['Bowling Type']=='Spin'].head(num_allrounders-num_pacers)

    final_allr = all_pace.merge(all_spin, how='outer').sort_values('Allrounder Score', ascending=False).head(num_allrounders)
    final_allr.sort_values('Batsmen Score',ascending=False)
    allrounders = list(final_allr['Player Name'])

    rem_pacers= num_pacers -sum(final_allr['Bowling Type'].str.contains('Pacer'))
    rem_spinners =  num_spinners - sum(final_allr['Bowling Type'] == 'Spin')


    #Pacer Selection
    pacers=t20team[(t20team['Playing Role']=='Bowler') &(t20team['Bowling Type']).str.contains('Pacer') ].sort_values('Bowler Score',ascending=False).head(rem_pacers).reset_index(drop=True)

    #Spinner Selection
    spinners=t20team[(t20team['Playing Role']=='Bowler') &(t20team['Bowling Type']=='Spin')].sort_values('Bowler Score',ascending=False).head(rem_spinners).reset_index(drop=True)

    #bowlers
    bowlers=pacers.merge(spinners,how='outer').sort_values('Batsmen Score')['Player Name'].reset_index(drop=True)

    #Final t20team
    final_XI=list(openers)+list(top_order)+list(middle_order)+list(Keeper)+allrounders+list(bowlers)
    for i in range(len(final_XI)):
        print(i+1,'. ',final_XI[i],sep='')

    #Average Score by team
    df1=pd.read_excel('Cleaned_datasets/T20.xlsx',usecols=['Player ID','Avg'])
    batsmens=df1.merge(players[['Player ID','Player Name']],on='Player ID')
    batsmens.fillna(0,inplace=True)
    batting_Score = sum(batsmens[batsmens['Player Name'].isin(final_XI)]['Avg'])
    print("Average Batting Score:", batting_Score*0.6)

else:
    print("Choose only 11 Players")
