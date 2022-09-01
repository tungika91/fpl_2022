import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit as st
import altair as alt
from bs4 import BeautifulSoup
import requests

st.header('Fantasy Premier League 2022-2023')

current_GW = st.text_input('Enter Gameweek', 2)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    fpl_players_df = pd.read_csv(uploaded_file)
else:
    filename = f'GW_{current_GW}'
    filepath = Path(f'db/{filename}.csv')
    fpl_players_df = pd.read_csv(filepath)

fpl_players_df['xG_xA'] = fpl_players_df['xG'] + fpl_players_df['xA']

# Divide into different groups based on position
fwd_df = fpl_players_df.loc[(fpl_players_df.position == 'Forward') & (fpl_players_df.minutes > 0)]
mid_df = fpl_players_df.loc[(fpl_players_df.position == 'Midfielder') & (fpl_players_df.minutes > 0)]
def_df = fpl_players_df.loc[(fpl_players_df.position == 'Defender') & (fpl_players_df.minutes > 0)]
gk_df = fpl_players_df.loc[(fpl_players_df.position == 'Goalkeeper') & (fpl_players_df.minutes > 0)]

# FILTER CONDITIONS
def is_Fixture_easy(mid_df, avg_difficulty_score = 2.5):
    return (mid_df['Avg_Difficulty'] <= avg_difficulty_score)

def max_Cost(mid_df, max_cost = 80):
    return mid_df['now_cost'] <= max_cost

def min_playingTime(mid_df, playtime = 120):
    return mid_df['minutes'] >= playtime

# Separate each position into individual tabs
tab0, tab1, tab2, tab3, tab4 = st.tabs(['Goalkeepers', "Defenders", "Midfielders", "Forwards", "Injuries"])

with tab0:
    # GOALKEEPERS
    st.header('GOALKEEPERS ANALYSIS')
    st.subheader(f'Quick Summary')

    # Summary
    st.dataframe(gk_df[['web_name','team_short','total_points','minutes', 'saves', 'penalties_saved', 'goals_conceded', 'own_goals']])
    gk_para = ['clean_sheets', 'saves', 'minutes', 'total_points', 'penalties_saved', 'goals_conceded', 'own_goals']

    # Performance Analysis 
    st.subheader('Goalkeepers Performance Analysis')
    para_x_gk = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points', 'clean_sheets', 'saves', 'minutes', 'penalties_saved', 'goals_conceded', 'own_goals'),
        index = 0)
    para_y_gk = st.selectbox(
        'Select parameter for y-axis:',
        ('saves','clean_sheets', 'minutes', 'total_points', 'penalties_saved', 'goals_conceded', 'own_goals'),
        index = 0)

    # Plot with Altair chart - interactive
    chart_gk = alt.Chart(gk_df).mark_circle().encode(
        x = para_x_gk,
        y = para_y_gk,
        size = 'total_points',
        color = alt.value('green'),
        opacity = alt.value(0.5),
        tooltip = ['web_name', 'team']
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20
    ).interactive()

    # Plot with matplotlib - still
    #st.altair_chart(chart_gk, use_container_width=True)
    color_gk = []
    col1, col2 = st.columns(2)
    with col1:
        LOW_GK = st.number_input('Low-tier cost:',value=40)
    with col2:
        MID_GK = st.number_input('Mid-tier cost:',value=50)

    for i in range(len(gk_df)):
        if gk_df['now_cost'].iloc[i] <= LOW_GK:
            color_gk.append('#1f77b4')
        elif LOW_GK < gk_df['now_cost'].iloc[i] <= MID_GK:
            color_gk.append('#ff7f0e')
        else:
            color_gk.append('#2ca02c')
    
    fig_gk = plt.figure(figsize = (12,6), dpi=500)
    plt.scatter(gk_df[para_x_gk], gk_df[para_y_gk], c=color_gk, alpha = 0.7, s = 300)
    plt.xlabel(para_x_gk.upper())
    plt.ylabel(para_y_gk.upper())
    plt.title("Goalkeepers " + para_y_gk.upper() + ' vs ' + para_x_gk.upper())
    for i, txt in enumerate(gk_df.web_name):
        plt.annotate(txt, (gk_df[f'{para_x_gk}'].iat[i], gk_df[f'{para_y_gk}'].iat[i]))
    plt.grid(which = 'both', axis = 'both', ls = '--')
    st.pyplot(fig_gk)

    # Players with issues
    st.subheader('Goalkeepers with injuries')
    chance_gk = st.text_input('Chance of goalkeeprs playing next GW:', 75)
    st.dataframe(gk_df[['web_name', 'team_short', 'news']].loc[gk_df['chance_of_playing_this_round'] <= int(chance_gk)])

    # Potential picks for next GWs
    st.subheader('Potential Picks')
    col1_gk, col2_gk, col3_gk = st.columns(3)

    with col1_gk:
        dif_gk = st.text_input('Average difficulty for the next 4 GW:', 2.5)
    with col2_gk:
        min_minutes_gk = st.text_input('Minimum minutes played so far:', 100)
    with col3_gk:
        max_cost_gk = st.text_input('Maximum price:', 49)
    st.dataframe(gk_df[['web_name', 'team_short','minutes','now_cost', 'total_points','form','clean_sheets', 'saves', 'penalties_saved', 'goals_conceded', 'own_goals', 'Avg_Difficulty', 'Difficulty', 'Opponents']].loc[is_Fixture_easy(gk_df, float(dif_gk)) & max_Cost(gk_df, int(max_cost_gk)) & min_playingTime(gk_df, int(min_minutes_gk))].sort_values('saves', ascending=False))

with tab1:
    # DEFENDER
    st.header('DEFENDER ANALYSIS')
    st.subheader(f'Quick Summary')

    # Summary
    st.dataframe(def_df[['web_name','team_short','total_points','minutes','goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals']])
    def_para = ['clean_sheets', 'influence','creativity', 'threat', 'ict_index','minutes', 'total_points', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals']

    # Performance Analysis 
    st.subheader('Defender Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points', 'influence','creativity', 'threat', 'ict_index','form','clean_sheets', 'minutes', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','influence','creativity', 'threat', 'ict_index','clean_sheets', 'form','minutes', 'total_points', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals'),
        index = 0)

    # Plot with Altair chart - interactive
    chart_def = alt.Chart(def_df).mark_circle().encode(
        x = para_x,
        y = para_y,
        size = 'total_points',
        color = alt.value('red'),
        opacity = alt.value(0.5),
        tooltip = ['web_name', 'team']
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20
    ).interactive()

    # Plot with matplotlib - still
    #st.altair_chart(chart_def, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    color_def = []
    col1, col2 = st.columns(2)
    with col1:
        LOW_DEF = st.number_input('Low-tier cost:',value=45)
    with col2:
        MID_DEF = st.number_input('Mid-tier cost:',value=65)

    for i in range(len(def_df)):
        if def_df['now_cost'].iloc[i] <= LOW_DEF:
            color_def.append('#1f77b4')
        elif LOW_DEF < def_df['now_cost'].iloc[i] <= MID_DEF:
            color_def.append('#ff7f0e')
        else:
            color_def.append('#2ca02c')
    plt.scatter(def_df[para_x], def_df[para_y], c=color_def, alpha = 0.7, s = 300)
    plt.xlabel(para_x.upper())
    plt.ylabel(para_y.upper())
    plt.title("Defenders " + para_y.upper() + ' vs ' + para_x.upper())
    for i, txt in enumerate(def_df.web_name):
        plt.annotate(txt, (def_df[f'{para_x}'].iat[i], def_df[f'{para_y}'].iat[i]))
    plt.grid(which = 'both', axis = 'both', ls = '--')
    st.pyplot(fig)

    # Players with issues
    st.subheader('Defenders with injuries')
    chance_def = st.text_input('Chance of defenders playing next GW:', 75)
    st.dataframe(def_df[['web_name', 'team_short', 'news']].loc[def_df['chance_of_playing_this_round'] <= int(chance_def)])

    # Potential picks for next GWs
    st.subheader('Potential Picks')
    col1, col2, col3 = st.columns(3)

    with col1:
        dif = st.text_input('Average difficulty for the next 4 GW:', 2.75)
    with col2:
        min_minutes = st.text_input('Minimum minutes played so far:', 120)
    with col3:
        max_cost = st.text_input('Maximum price:', 50)
    st.dataframe(def_df[['web_name', 'team_short','minutes','now_cost', 'total_points','form','xG_xA', 'xGChain', 'Avg_Difficulty', 'Difficulty', 'Opponents']].loc[is_Fixture_easy(def_df, float(dif)) & max_Cost(def_df, int(max_cost)) & min_playingTime(def_df, int(min_minutes))].sort_values('xG_xA', ascending=False))

with tab2:
    # MIDFIELDERS
    st.header('MIDFIELDER ANALYSIS')
    st.subheader(f'Quick Summary')

    # Summary
    st.dataframe(mid_df[['web_name','team_short','total_points','minutes', 'form','assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup']])
    mid_para = ['minutes','form', 'influence','creativity', 'threat', 'ict_index','total_points', 'assists', 'goals_scored','xG', 'xA','xG_xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals']

    # Performance Analysis 
    st.subheader('Midfielder Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points','xG_xA','influence','creativity', 'threat', 'ict_index','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','total_points','influence','creativity', 'threat', 'ict_index','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals'),
        index = 0)

    # Plot with Altair chart - interactive
    chart_mid = alt.Chart(mid_df).mark_circle().encode(
        x = para_x,
        y = para_y,
        size = 'total_points',
        color = alt.value('blue'),
        opacity = alt.value(0.5),
        tooltip = ['web_name', 'team']
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20
    ).interactive()

    # Plot with matplotlib - still
    #st.altair_chart(chart_mid, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    color_mid = []
    col1, col2 = st.columns(2)
    with col1:
        LOW_MID = st.number_input('Low-tier cost:',value=60)
    with col2:
        MID_MID = st.number_input('Mid-tier cost:',value=85)

    for i in range(len(mid_df)):
        if mid_df['now_cost'].iloc[i] <= LOW_MID:
            color_mid.append('#1f77b4')
        elif LOW_MID < mid_df['now_cost'].iloc[i] <= MID_MID:
            color_mid.append('#ff7f0e')
        else:
            color_mid.append('#2ca02c')
    plt.scatter(mid_df[para_x], mid_df[para_y], c=color_mid, alpha = 0.7, s = 300)
    plt.xlabel(para_x.upper())
    plt.ylabel(para_y.upper())
    plt.title("Midfielders " + para_y.upper() + ' vs ' + para_x.upper())
    for i, txt in enumerate(mid_df.web_name):
        plt.annotate(txt, (mid_df[f'{para_x}'].iat[i],mid_df[f'{para_y}'].iat[i]))
    plt.grid(which = 'both', axis = 'both', ls = '--')
    st.pyplot(fig)

    # Players with issues
    st.subheader('Midfielders with injuries')
    chance_mid = st.text_input('Chance of midfielders playing next GW:', 50)
    st.dataframe(mid_df[['web_name', 'team_short', 'news']].loc[mid_df['chance_of_playing_this_round'] <= int(chance_mid)])

    # Potential picks for next GWs
    st.subheader('Potential Picks')
    col1, col2, col3 = st.columns(3)

    with col1:
        dif = st.text_input('Average difficulty for the next 4 GW:', 2.6)
    with col2:
        min_minutes = st.text_input('Minimum minutes played so far:', 150)
    with col3:
        max_cost = st.text_input('Maximum price:', 90)
    st.dataframe(mid_df[['web_name', 'team_short','minutes','now_cost', 'total_points','form','xG_xA', 'xGChain', 'Avg_Difficulty', 'Difficulty', 'Opponents']].loc[is_Fixture_easy(mid_df, float(dif)) & max_Cost(mid_df, int(max_cost)) & min_playingTime(mid_df, int(min_minutes))].sort_values('xG_xA', ascending=False))

with tab3:
    # FORWARD
    st.header('FORWARDS ANALYSIS')
    st.subheader(f'Quick Summary')

    # Summary
    st.dataframe(fwd_df[['web_name','team_short','total_points','minutes', 'form','assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup']])
    fwd_para = ['minutes','form', 'influence','creativity', 'threat', 'ict_index','total_points', 'assists', 'goals_scored','xG', 'xA','xG_xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup']

    # Performance Analysis 
    st.subheader('Forwards Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points','xG_xA','influence','creativity', 'threat', 'ict_index','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','total_points','influence','creativity', 'threat', 'ict_index','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup'),
        index = 0)

    # Plot with Altair chart - interactive
    chart_fwd = alt.Chart(fwd_df).mark_circle().encode(
        x = para_x,
        y = para_y,
        size = 'total_points',
        color = alt.value('blue'),
        opacity = alt.value(0.5),
        tooltip = ['web_name', 'team']
    ).configure_axis(
        labelFontSize=15,
        titleFontSize=20
    ).interactive()

    # Plot with matplotlib - still
    #st.altair_chart(chart_fwd, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    color_fw = []
    col1, col2 = st.columns(2)
    with col1:
        LOW_FW = st.number_input('Low-tier cost:',value=65)
    with col2:
        MID_FW = st.number_input('Mid-tier cost:',value=90)

    for i in range(len(fwd_df)):
        if fwd_df['now_cost'].iloc[i] <= LOW_FW:
            color_fw.append('#1f77b4')
        elif LOW_FW < fwd_df['now_cost'].iloc[i] <= MID_FW:
            color_fw.append('#ff7f0e')
        else:
            color_fw.append('#2ca02c')
    plt.scatter(fwd_df[para_x], fwd_df[para_y], c=color_fw, alpha = 0.7, s = 300)
    plt.xlabel(para_x.upper())
    plt.ylabel(para_y.upper())
    plt.title("Forwards " + para_y.upper() + ' vs ' + para_x.upper())
    for i, txt in enumerate(fwd_df.web_name):
        plt.annotate(txt, (fwd_df[f'{para_x}'].iat[i],fwd_df[f'{para_y}'].iat[i]))
    plt.grid(which = 'both', axis = 'both', ls = '--')
    st.pyplot(fig)

    # Players with issues
    st.subheader('Forwards with injuries')
    chance_fwd = st.text_input('Chance of forwards playing next GW:', 75)
    st.dataframe(fwd_df[['web_name', 'team_short', 'news']].loc[fwd_df['chance_of_playing_this_round'] <= int(chance_fwd)])

    # Potential picks for next GWs
    st.subheader('Potential Picks')
    col1, col2, col3 = st.columns(3)

    with col1:
        dif = st.text_input('Average difficulty for the next 4 GW:', 2.7)
    with col2:
        min_minutes = st.text_input('Minimum minutes played so far:', 160)
    with col3:
        max_cost = st.text_input('Maximum price:', 120)
    st.dataframe(fwd_df[['web_name', 'team_short','minutes','now_cost', 'total_points','form','xG_xA', 'xGChain', 'Avg_Difficulty', 'Difficulty', 'Opponents']].loc[is_Fixture_easy(fwd_df, float(dif)) & max_Cost(fwd_df, int(max_cost)) & min_playingTime(fwd_df, int(min_minutes))].sort_values('xG_xA', ascending=False))

with tab4:
    url = 'https://www.premierinjuries.com/injury-table.php' 
    html = requests.get(url).text

    soup = BeautifulSoup(html)
    table = soup.select('table tbody')
    
    # SCRAPE INJURY COUNT AND TEAM NAME
    for index, element in enumerate(table):
        # Get injury count
        injury_count = []
        counts = element.select('th div div.table-actions div.injury-count2.injury-count-yes span')
        for count in counts:
            injury_count.append(int(count.text))

        # Get team name
        team_list = []
        teams = element.select('th div div.injury-team')
        for i,team in enumerate(teams):
          for j in range(injury_count[i]):
            team_list.append(team.text)

    # SCRAPE STATUS
    for index, element in enumerate(table):
        temp = []
        statuses = element.select('tr td')
        for status in statuses:
          #print(status.text)
          if 'Status' in status.text:
            temp.append(status.text.strip("'Status'"))

    i = 0 # keep track of item in temp
    j = 0 # keep track of count in injury_count

    status_list = []
    while i < len(temp):
      if temp[i] == temp[0]:
        i+=1
      else:
        for n in range(injury_count[j]):
          if temp[i+n] == 'Ruled O':
            status_list.append('Ruled Out')
          else:
            status_list.append(temp[i+n])
        j+=1
        i+=n+1

    # body > div.elementor.elementor-995 > section.elementor-section.elementor-top-section.elementor-element.elementor-element-0de1ea7.elementor-section-full_width.elementor-section-height-default.elementor-section-height-default > div > div.elementor-column.elementor-col-33.elementor-top-column.elementor-element.elementor-element-84bc06d.pi-column-darkglass > div > div.elementor-element.elementor-element-389f88c.elementor-widget.elementor-widget-shortcode > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(1) > div
    # SCRAPE PLAYER NAME
    for index, element in enumerate(table):
        temp = []
        names = element.select('tr td')
        for name in names:
          #print(name.text)
          if 'Player' in name.text:
            temp.append(name.text.strip('Player'))
    name_list = []
    for item in temp:
      if item != '':
        name_list.append(item)

    # body > div.elementor.elementor-995 > section.elementor-section.elementor-top-section.elementor-element.elementor-element-0de1ea7.elementor-section-full_width.elementor-section-height-default.elementor-section-height-default > div > div.elementor-column.elementor-col-33.elementor-top-column.elementor-element.elementor-element-84bc06d.pi-column-darkglass > div > div.elementor-element.elementor-element-389f88c.elementor-widget.elementor-widget-shortcode > div > div > div > table > tbody > tr:nth-child(3) > td:nth-child(1) > div
    # SCRAPE POTENTIAL RETURN
    for index, element in enumerate(table):
        temp = []
        dates = element.select('tr td')
        for date in dates:
          #print(name.text)
          if 'Potential Return' in date.text:
            temp.append(date.text.strip('Potential Return'))

    return_list = []
    for item in temp:
      if item != '':
        if item == 'No Return D':
          return_list.append('No Return Date')
        else:
          return_list.append(item)


    # CREATE DATAFRAME AS SUMMARY
    count = [i for i in range(sum(injury_count))]
    injury_df = pd.DataFrame({'Team': team_list, 
                              'Player': name_list,
                              'Status': status_list,
                              'Potential Return': return_list
                              }, index = count)
    
    team = st.selectbox('Select team:',set(team_list),index = 0)
    st.subheader('List of injuries')
    st.dataframe(injury_df.loc(injury_df['Team'] == team))
