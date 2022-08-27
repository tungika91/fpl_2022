import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit as st
import altair as alt

st.header('Fantasy Premier League 2022-2023')

current_GW = st.text_input('Enter Gameweek', 2)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    fpl_players_df = pd.read_csv(uploaded_file)
else:
    filename = f'GW_{current_GW}'
    filepath = Path(f'/Users/tungngo/WaveBoost Dropbox/Tung Ngo/Learning/Python3/FPL 2022-2023/db/{filename}.csv')
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
tab0, tab1, tab2, tab3 = st.tabs(['Goalkeepers', "Defenders", "Midfielders", "Forwards"])

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
    st.altair_chart(chart_gk, use_container_width=True)
    fig_gk = plt.figure(figsize = (12,6), dpi=500)
    plt.scatter(gk_df[para_x_gk], gk_df[para_y_gk], s = 200, alpha = 0.5)
    for i, txt in enumerate(gk_df.web_name):
        plt.annotate(txt, (gk_df[f'{para_x_gk}'].iat[i], gk_df[f'{para_y_gk}'].iat[i]), fontsize = 12)
    plt.grid(linestyle = '--')
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.xlabel(para_x_gk, fontsize = 15)
    plt.ylabel(para_y_gk, fontsize = 15)
    st.pyplot(fig_gk)

    # Players with issues
    st.subheader('Goalkeepers with issues')
    chance_gk = st.text_input('Chance of goalkeeprs playing next GW:', 75)
    st.dataframe(gk_df[['web_name', 'team_short', 'news']].loc[gk_df['chance_of_playing_next_round'] <= int(chance_gk)])

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
    def_para = ['clean_sheets', 'minutes', 'total_points', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals']

    # Performance Analysis 
    st.subheader('Defender Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points', 'clean_sheets', 'minutes', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'xG_xA','shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','clean_sheets', 'minutes', 'total_points', 'goals_conceded', 'clean_sheets', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'xGChain', 'xGBuildup', 'Goals_Assists', 'own_goals'),
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
    st.altair_chart(chart_def, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    plt.scatter(def_df[para_x], def_df[para_y], s = 200, alpha = 0.5)
    for i, txt in enumerate(def_df.web_name):
        plt.annotate(txt, (def_df[f'{para_x}'].iat[i], def_df[f'{para_y}'].iat[i]), fontsize = 12)
    plt.grid(linestyle = '--')
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.xlabel(para_x, fontsize = 15)
    plt.ylabel(para_y, fontsize = 15)
    st.pyplot(fig)

    # Players with issues
    st.subheader('Defenders with issues')
    chance_def = st.text_input('Chance of defenders playing next GW:', 75)
    st.dataframe(def_df[['web_name', 'team_short', 'news']].loc[def_df['chance_of_playing_next_round'] <= int(chance_def)])

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
    mid_para = ['minutes','form', 'total_points', 'assists', 'goals_scored','xG', 'xA','xG_xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals']

    # Performance Analysis 
    st.subheader('Midfielder Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points','xG_xA','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','total_points','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup', 'own_goals'),
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
    st.altair_chart(chart_mid, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    plt.scatter(mid_df[para_x], mid_df[para_y], s = 200, alpha = 0.5)
    for i, txt in enumerate(mid_df.web_name):
        plt.annotate(txt, (mid_df[f'{para_x}'].iat[i], mid_df[f'{para_y}'].iat[i]), fontsize = 12)
    plt.grid(linestyle = '--')
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.xlabel(para_x, fontsize = 15)
    plt.ylabel(para_y, fontsize = 15)
    st.pyplot(fig)

    # Players with issues
    st.subheader('Midfielders with issues')
    chance_mid = st.text_input('Chance of midfielders playing next GW:', 50)
    st.dataframe(mid_df[['web_name', 'team_short', 'news']].loc[mid_df['chance_of_playing_next_round'] <= int(chance_mid)])

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
    fwd_para = ['minutes','form', 'total_points', 'assists', 'goals_scored','xG', 'xA','xG_xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup']

    # Performance Analysis 
    st.subheader('Forwards Performance Analysis')
    para_x = st.selectbox(
        'Select parameter for x-axis:',
        ('total_points','xG_xA','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup'),
        index = 0)
    para_y = st.selectbox(
        'Select parameter for y-axis:',
        ('xG_xA','total_points','minutes','form', 'assists', 'goals_scored','xG', 'xA', 'shots', 'key_passes', 'npg', 'npxG', 'xGChain', 'xGBuildup'),
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
    st.altair_chart(chart_fwd, use_container_width=True)
    fig = plt.figure(figsize = (12,6), dpi=500)
    plt.scatter(fwd_df[para_x], fwd_df[para_y], s = 200, alpha = 0.5)
    for i, txt in enumerate(fwd_df.web_name):
        plt.annotate(txt, (fwd_df[f'{para_x}'].iat[i], fwd_df[f'{para_y}'].iat[i]), fontsize = 12)
    plt.grid(linestyle = '--')
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.xlabel(para_x, fontsize = 15)
    plt.ylabel(para_y, fontsize = 15)
    st.pyplot(fig)

    # Players with issues
    st.subheader('Forwards with issues')
    chance_fwd = st.text_input('Chance of forwards playing next GW:', 75)
    st.dataframe(fwd_df[['web_name', 'team_short', 'news']].loc[fwd_df['chance_of_playing_next_round'] <= int(chance_fwd)])

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
