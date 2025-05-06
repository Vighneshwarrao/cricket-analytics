import pandas as pd
Score=pd.read_csv('ODI_Score.csv')


players=pd.read_csv('Cleaned_datasets/Players.csv')

oditeam=players[['Player ID','Player Name','ODI Batting Pos','Playing Role','Batting Style','Bowling Style','Bowling Type']].merge(
    Score,on='Player ID',how='outer'
)
num_batters=8
num_openers=2
num_top_order=1
num_middle_order=1
num_keeper=1
num_allrounders=max(0,num_batters-5)
num_bowlers=11-num_batters

num_pacers=4
num_spinners=2


if(num_bowlers+num_openers+num_top_order+num_allrounders+num_middle_order+num_keeper==11):

    #Openers Selection
    openers=oditeam[oditeam['ODI Batting Pos']=='Openers'].sort_values('Batsmen Score',ascending=False).head(num_openers)['Player Name'].reset_index(drop=True)

    #Top Order Selection
    top_order=oditeam[oditeam['ODI Batting Pos']=='Top Order'].sort_values('Batsmen Score',ascending=False).head(num_top_order)['Player Name'].reset_index(drop=True)

    #Middle Order Selection
    middle_order=oditeam[(oditeam['ODI Batting Pos']=='Middle Order') & (oditeam['Playing Role']!='Wicketkeeper Batter')].sort_values('Batsmen Score',ascending=False).head(num_middle_order)['Player Name'].reset_index(drop=True)

    #Keeper Selection
    Keeper=oditeam[(oditeam['ODI Batting Pos']=='Middle Order') & (oditeam['Playing Role']=='Wicketkeeper Batter')].sort_values('Keeper Score',ascending=False).head(num_keeper)['Player Name'].reset_index(drop=True)

    #Allrounder Selection
    all_pace=oditeam[((oditeam['Playing Role']=='Allrounder') | (oditeam['Playing Role']=='Bowling Allrounder') | (oditeam['Playing Role']=='Batting Allrounder')) & (oditeam['Bowling Type'].str.contains('Pacer'))].sort_values(['Allrounder Score','Batsmen Score'],ascending=False).head(num_allrounders).reset_index(drop=True)
    all_spin=oditeam[((oditeam['Playing Role']=='Allrounder') | (oditeam['Playing Role']=='Bowling Allrounder') | (oditeam['Playing Role']=='Batting Allrounder')) & (oditeam['Bowling Type']=='Spin')].sort_values(['Allrounder Score','Batsmen Score'],ascending=False).head(num_allrounders).reset_index(drop=True)

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
    pacers=oditeam[(oditeam['Playing Role']=='Bowler') &(oditeam['Bowling Type']).str.contains('Pacer') ].sort_values('Bowler Score',ascending=False).head(rem_pacers).reset_index(drop=True)

    #Spinner Selection
    spinners=oditeam[(oditeam['Playing Role']=='Bowler') &(oditeam['Bowling Type']=='Spin')].sort_values('Bowler Score',ascending=False).head(rem_spinners).reset_index(drop=True)

    #bowlers
    bowlers=pacers.merge(spinners,how='outer').sort_values('Batsmen Score')['Player Name'].reset_index(drop=True)

    #Final oditeam
    final_XI=list(openers)+list(top_order)+list(middle_order)+list(Keeper)+allrounders+list(bowlers)
    for i in range(len(final_XI)):
        print(i+1,'. ',final_XI[i],sep='')

    #Average Score by team
    df1=pd.read_excel('Cleaned_datasets/ODI.xlsx',usecols=['Player ID','Avg'])
    batsmens=df1.merge(players[['Player ID','Player Name']],on='Player ID')
    batsmens.fillna(0,inplace=True)
    batting_Score = sum(batsmens[batsmens['Player Name'].isin(final_XI)]['Avg'])
    print("Average Batting Score:", batting_Score)

else:
    print("Choose only 11 Players")
