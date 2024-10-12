import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
# from sqlalchemy import create_engine
# import pymysql

# Create an SQLAlchemy engine
# db_user = 'root'
# db_password = 'xxxx'
# db_host = 'localhost'
# db_port = '3306'  
# db_name = 'github'

# # Establish a connection to the database
# engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# # SQL query to fetch data
# query = 'SELECT * FROM repository'

# # Read data into a DataFrame using the SQLAlchemy engine
# df = pd.read_sql(query, engine)

df = pd.read_csv("github_repositories_dataset.csv")

# Extract year from 'creation_date'
df['year'] = pd.to_datetime(df['creation_date']).dt.year  # Ensure 'creation_date' is in datetime format

# Set up Streamlit page configuration
st.set_page_config(page_title="GitHub Data Dive", layout="wide")  
st.title(":blue[GitHub Data Dive]")
# st.divider()

# Sidebar for navigation
with st.sidebar:
    selected_menu = option_menu("Menu", ["Home", "Analysis", "About"],
                                 icons=['house', 'activity', 'info-circle-fill'],
                                 menu_icon="cast", default_index=1)

if selected_menu == "Home":
    # st.divider()
    st.subheader(":red[Project Overview]")
    st.write("""
        
        GitHub Data Dive is a comprehensive analysis tool that extracts data from GitHub repositories 
        focusing on trending topics in the data science and software development world.
        
        This tool provides insights into repository characteristics, technology usage, and trends 
        in programming languages by utilizing data visualization techniques. It aims to help developers, 
        organizations, and researchers make informed decisions regarding open-source collaboration.
    """)

    st.subheader(":red[About Github]")
    st.write("""
            GitHub is a web-based platform that facilitates version control and collaborative software development. 
            It is built around the Git version control system, which allows developers to track changes in their code, 
            collaborate with others, and manage their projects more effectively. GitHub provides tools to store code repositories, 
            track issues, manage projects, and document software. It also enables a social networking aspect by allowing users to follow 
            each other, star repositories, and contribute to open-source projects from anywhere in the world.
    """)

# Analysis Tab
elif selected_menu == "Analysis":
    tab_overview, tab_topic_wise, tab_year_wise = st.tabs(["**Overview**", "**Topic-wise**", "**Year-wise**"])

    # Overview Tab
    with tab_overview:
        with st.container(border=True):
            col1,col2 = st.columns(2)

            with col1:
                # Group by programming language to get the count of each language
                language_count = df['programming_language'].value_counts().reset_index()
                language_count.columns = ['programming_language', 'count']

                # Create a donut chart for programming language distribution
                fig_language_donut = px.pie(
                    language_count,
                    names='programming_language',
                    values='count',
                    hole=0.5,
                    title='Programming Language Distribution',
                    width=600,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_language_donut)
            
            with col2:

                # Count the number of repositories created each year
                yearly_repo_count = df['year'].value_counts().reset_index()
                yearly_repo_count.columns = ['year', 'repository_count']
                yearly_repo_count = yearly_repo_count.sort_values('year')

                # Create a bar chart for repositories created by each year
                fig_repo_year = px.bar(
                    yearly_repo_count,
                    x='year',
                    y='repository_count',
                    title='Repositories Created by Each Year',
                    labels={'year': 'Year', 'repository_count': 'Repository Count'},
                    width=600,
                    color_discrete_sequence=['#636EFA']
                )
                st.plotly_chart(fig_repo_year)
            
            st.divider()
            col3,col4 = st.columns(2)
            with col3:

                # Summarize repository activity by topic
                activity_summary_topic = df.groupby('topic')[['number_of_stars', 'number_of_forks', 'number_of_open_issues']].sum().reset_index()

                # Create a horizontal stacked bar chart for repository activity by topic
                fig_activity_topic = px.bar(
                    activity_summary_topic,
                    x=['number_of_stars', 'number_of_forks', 'number_of_open_issues'],
                    y='topic',
                    orientation='h',
                    title='Repository Activity by Topic',
                    labels={'value': 'Count', 'topic': 'Topic'},
                    height=600,
                    color_discrete_sequence=px.colors.sequential.Teal
                )
                st.plotly_chart(fig_activity_topic)

            with col4:
                # Summarize repository activity by year
                activity_summary_year = df.groupby('year')[['number_of_stars', 'number_of_forks', 'number_of_open_issues']].sum().reset_index()

                # Create a horizontal stacked bar chart for repository activity by year
                fig_activity_year = px.bar(
                    activity_summary_year,
                    x=['number_of_stars', 'number_of_forks', 'number_of_open_issues'],
                    y='year',
                    orientation='h',
                    title='Repository Activity by Year',
                    labels={'value': 'Count', 'year': 'Year'},
                    height=600,
                    color_discrete_sequence=px.colors.sequential.Sunset
                )
                st.plotly_chart(fig_activity_year)

            st.divider()
            

            language_count = df.groupby(['topic', 'programming_language']).size().reset_index(name='count')

            # Get the top 10 programming languages based on total count
            top_languages = language_count.groupby('programming_language')['count'].sum().nlargest(10).index

            # Filter the language_count DataFrame to include only top 10 languages
            top_language_count = language_count[language_count['programming_language'].isin(top_languages)]

            # Create a heat map for topic vs programming language with the count of programming languages
            fig_heatmap = px.density_heatmap(
                top_language_count, 
                x='topic', 
                y='programming_language', 
                z='count',  # Using the count of programming languages
                color_continuous_scale='Viridis',  # You can change the color scale here
                text_auto=True,  # Display counts directly on the map
                title=f'Top 10 Programming Languages Usage by Topic',
                height=700,
                width=1000,
                labels={'topic': 'Topic', 'programming_language': 'Programming Language', 'count': 'Language Count'}
            )

            # Display the heat map in Streamlit
            st.plotly_chart(fig_heatmap)


    # Topic-wise Analysis Tab
    with tab_topic_wise:

        with st.container(border=True): 
            unique_topics = df['topic'].unique()
            selected_topics = st.multiselect('Select Topics', options=unique_topics, default=[unique_topics[0]])

            # Filter DataFrame based on selected topics
            filtered_df = df[df['topic'].isin(selected_topics)]

            # Create two columns in Streamlit layout
            col1, col2 = st.columns(2)

            with col1:
                # Group by language and get the top 10
                top_languages = filtered_df['programming_language'].value_counts().nlargest(10).reset_index()
                top_languages.columns = ['language', 'count']

                # Create a donut chart for top programming languages
                fig_top_languages = px.pie(top_languages, 
                                            names='language', 
                                            values='count', 
                                            title='Top 10 Programming Languages', 
                                            color_discrete_sequence=px.colors.qualitative.Pastel,
                                            width=600,
                                            hole=0.5)
                st.plotly_chart(fig_top_languages)

            with col2:
                # Group by license type to get the count of each license for the selected topic
                license_count_topic = filtered_df['license_type'].value_counts().reset_index()
                license_count_topic.columns = ['license_type', 'count']

                # Create a donut chart for license distribution for the selected topic
                fig_license_distribution = px.pie(
                    license_count_topic,
                    names='license_type',
                    values='count',
                    hole=0.5,
                    title='License Distribution for Repositories for Selected Topic',
                    width=600,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_license_distribution)

            st.divider()

            # Group by year and topic, and count the number of repositories
            yearly_counts = filtered_df.groupby(['year', 'topic']).size().reset_index(name='repository_count')

            # Create a line chart for year-wise repository counts
            fig_yearly_counts = px.line(yearly_counts, 
                                        x='year', 
                                        y='repository_count', 
                                        color='topic',
                                        title='Year-wise Repository Count for Selected Topics',
                                        labels={'repository_count': 'Repository Count', 'year': 'Year'},
                                        width=1100,
                                        markers=True)
            st.plotly_chart(fig_yearly_counts)

            st.divider()

            # Summarize repository activity for each repository within the filtered topics
            activity_summary_repo = filtered_df.groupby('repository_name')[['number_of_stars', 'number_of_forks', 'number_of_open_issues']].sum().reset_index()
            activity_summary_repo = activity_summary_repo.sort_values('number_of_stars', ascending=False).head(10)

            # Create a bar chart to visualize repository activity for top repositories

            fig_repo_activity = px.bar(activity_summary_repo, 
                                        x='repository_name', 
                                        y=['number_of_stars', 'number_of_forks', 'number_of_open_issues'],
                                        title='Repository Activity for Selected Topics',
                                        labels={'value': 'Count', 'repository_name': 'Repository'},
                                        height=600,
                                        width=800,
                                        barmode='group')
            st.plotly_chart(fig_repo_activity)

    # Year-wise Analysis Tab
    with tab_year_wise:
        with st.container(border=True):
            # Order the years in ascending order for display
            years = sorted(df['year'].unique())
            default_year = 2024 if 2024 in years else years[0]

            # Create a year-based filter dropdown with orderly display
            selected_year = st.selectbox("Select Year", years, index=years.index(default_year))
            filtered_year_df = df[df['year'] == selected_year]

            col1,col2 = st.columns(2)

            with col1:
                # Summarize programming language usage based on the selected year
                language_summary = filtered_year_df['programming_language'].value_counts().reset_index()
                language_summary.columns = ['programming_language', 'count']

                # Create a donut chart for programming languages
                fig_language_usage = px.pie(language_summary, 
                                            names='programming_language', 
                                            values='count', 
                                            title=f'Programming Language Usage in {selected_year}',
                                            width=600,
                                            hole=0.5,
                                            color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_language_usage)

            with col2:
                # Group by license type to get the count of each license
                license_count = filtered_year_df['license_type'].value_counts().reset_index()
                license_count.columns = ['license_type', 'count']

                # Create a donut chart for license distribution
                fig_donut = px.pie(
                    license_count,
                    names='license_type',
                    values='count',
                    hole=0.5,  # Creates the donut shape
                    title=f'License Distribution for Repositories in {selected_year}',
                    width=600,
                    color_discrete_sequence=px.colors.qualitative.Pastel  # Customize colors for better visualization
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig_donut)
            st.divider()

            # Summarize repository activity for the selected year
            activity_summary_year = filtered_year_df.groupby('repository_name')[['number_of_stars', 'number_of_forks', 'number_of_open_issues']].sum().reset_index()
            activity_summary_year = activity_summary_year.sort_values('number_of_stars', ascending=False).head(10)

            # Create a bar chart to visualize repository activity
            fig_top_repositories = px.bar(activity_summary_year, 
                                        x='repository_name', 
                                        y=['number_of_stars', 'number_of_forks', 'number_of_open_issues'],
                                        title=f'Top 10 Repositories in {selected_year}',
                                        labels={'value': 'Count', 'repository_name': 'Repository'},
                                        width=1000,
                                        height=600,
                                        barmode='group')
            st.plotly_chart(fig_top_repositories)
            st.divider()

            # Get the top 10 programming languages based on their count
            top_languages = filtered_year_df['programming_language'].value_counts().nlargest(10).index

            # Filter the dataframe to include only the top 10 programming languages
            filtered_top_languages_df = filtered_year_df[filtered_year_df['programming_language'].isin(top_languages)]

            # Group by topic and programming language to get the count of programming languages
            language_count = filtered_top_languages_df.groupby(['topic', 'programming_language']).size().reset_index(name='count')

            # Create a heat map for topic vs programming language with the count of programming languages
            fig_heatmap = px.density_heatmap(
                language_count, 
                x='topic', 
                y='programming_language', 
                z='count',  # Using the count of programming languages
                color_continuous_scale='Viridis',  # You can change the color scale here
                text_auto=True,  # Display counts directly on the map
                title=f'Top 10 Programming Languages Usage by Topic for {selected_year}',
                height=700,
                width=1000,
                labels={'topic': 'Topic', 'programming_language': 'Programming Language', 'count': 'Language Count'}
            )

            # Display the heat map in Streamlit
            st.plotly_chart(fig_heatmap)




# About Tab
elif selected_menu == "About":
    st.subheader(":red[About Project]")
    st.write("""
        "GitHub Data Dive" is a web application designed to leverage the extensive capabilities of GitHub by utilizing its API to extract data on repositories that are currently trending in specific topics. The application focuses on trending areas like machine learning, deep learning, data visualization, and more.
        
        **How It Works:**
        - **Data Extraction:** The application uses the GitHub API to fetch detailed information about repositories based on trending topics. It gathers metrics like repository names, programming languages, stars, forks, and other relevant information.
        - **Data Cleaning and Storage:** The extracted data is cleaned to ensure consistency and accuracy before being stored in a SQL database, making it easily accessible for analysis.
        - **Interactive Visualization:** Built using Streamlit, the application provides a user-friendly interface for visualizing data. Users can interact with the data using various filters to see trends in programming languages, repository activity, and other key metrics.
        
        ### :red[Use Cases]
        - **Developers:** Quickly identify popular projects to contribute to or learn from.
        - **Organizations:** Analyze the activity and popularity of specific open-source technologies.
        - **Educators and Researchers:** Find projects to use as teaching or research resources.
        
        ### :red[Deployment]
        The web application is deployed on Render, making it easily accessible to anyone interested in exploring GitHub's open-source ecosystem.
        
        ### :red[User Experience]
        The goal is to provide a seamless experience with intuitive navigation, interactive charts, and insightful analysis that can guide decision-making regarding project collaboration, technology trends, and educational resources.
    """)

