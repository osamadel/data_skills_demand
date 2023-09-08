import pandas as pd
import streamlit as st
import plotly.express as px
from pandas.api.types import CategoricalDtype

@st.cache_data
def read_data(path='./data/skills_with_jobs.csv'):
    df = pd.read_csv(path)
    return df


st.set_page_config(
    page_icon='https://static.vecteezy.com/system/resources/previews/018/930/587/original/linkedin-logo-linkedin-icon-transparent-free-png.png',
    page_title='LinkedIn Data Science Skills Dashboard',
    layout='wide'
)

df = read_data()
companies = ['All'] + df.company_name.unique().tolist()
employment_types = ['All'] + df.Employment_type.unique().tolist()
seniority_levels = ['All'] + df.Seniority_level.unique().tolist()
countries = ['All'] + df.job_country.unique().tolist()
job_positions = ['All'] + df.job_position.unique().tolist()


country_sel = st.sidebar.multiselect(label='Select Country(s):', options=countries, default='All')
employment_type_sel = st.sidebar.multiselect(label='Select Employment Type(s):', options=employment_types, default='All')
seniority_sel = st.sidebar.multiselect(label='Select Seniority Level(s):', options=seniority_levels, default='All')
jobpos_sel = st.sidebar.multiselect(label='Select Job Position(s):', options=job_positions, default='All')
companies_sel = st.sidebar.multiselect(label='Select Company/ie(s):', options=companies, default='All')

# print(type(country_sel), country_sel)

country_sel_mask = pd.Series([True] * len(df)) if country_sel in [['All'], []] else df.job_country.isin(country_sel)
employment_type_sel_mask = pd.Series([True] * len(df)) if employment_type_sel in [['All'], []] else df.Employment_type.isin(employment_type_sel)
seniority_sel_mask = pd.Series([True] * len(df)) if seniority_sel in [['All'], []] else df.Seniority_level.isin(seniority_sel)
jobpos_sel_mask = pd.Series([True] * len(df)) if jobpos_sel in [['All'], []] else df.job_position.isin(jobpos_sel)
companies_sel_mask = pd.Series([True] * len(df)) if companies_sel in [['All'], []] else df.job_country.isin(companies_sel)

df_filt = df[country_sel_mask & employment_type_sel_mask & seniority_sel_mask & jobpos_sel_mask & companies_sel_mask]
df_filt_viz = df_filt[['Skill', 'Type']].groupby('Skill').agg(['size', 'first']).reset_index()
df_filt_viz.columns = ['Skill', 'Count', 'Type']
# skill_type_order = {'TECHNICAL': 0, 'TECHNOLOGY': 1, 'BUSINESS': 2, 'SOFT': 3}
# skillType_cat = CategoricalDtype(categories=['TECHNICAL', 'TECHNOLOGY', 'BUSINESS', 'SOFT'].reverse(), ordered=True)
# df_filt_viz['Type'] = df.Type.astype(skillType_cat)
df_filt_viz = df_filt_viz.sort_values(by=['Count'], ascending=True)


# Filter skills by count threshold
filter_threshold = st.sidebar.slider(
    label='Select `N` to show skills that repeated at least `N` times:',
    min_value=int(df_filt_viz.Count.min()),
    max_value=int(df_filt_viz.Count.max()),
    value=10,
    step = 5,
)

# print(country_sel)
# print(country_sel_mask)

fig = px.bar(
            df_filt_viz[df_filt_viz.Count > filter_threshold],
            x='Count',
            y='Skill',
            color='Type',
            height=1200,
            orientation='h',
            color_discrete_sequence=px.colors.qualitative.Vivid,
            category_orders={'Type':reversed(['TECHNICAL', 'TECHNOLOGY', 'BUSINESS', 'SOFT'])}
)
fig.update_layout(
   yaxis = dict(
      tickmode = 'linear',
    #   tick0 = 0.5,
    #   dtick = 0.75
   )
)


st.markdown('# LinkedIn Data Science Skills Dashboard')

charts, explanation, match_calc = st.tabs(['Skills Chart', 'Explanation', 'Skills Match Calculator'])

with charts:
    st.plotly_chart(fig, use_container_width=True)

with explanation:
    st.write(
        """
        ## What does the skills chart show us?

        It shows us that there are key skills that are required almost by every employer and those are:

        **Technologies:**
        * Python
        * SQL
        * R
        * NLP
        * Business Intelligence

        **Technical Skills:**
        * Data Science (obviously, but very vague)
        * Machine Learning
        * AI
        * Analytics skills
        * Statistics
        * Algorithms
        * Mathematics
        * Deep learning
        * Optimization
        * Data Visualization

        **Soft Skills:**
        * Communication Skills
        * Learning Skills
        * Leadership Skills

        Clearly, the charts have duplicates, like *AI* and *Artificial Intelligence*. Also, some key terms in the charts are subsets of other skills like *Data* and *Data Modeling* or *Data Sets* etc.
        However, at least, the chart can show us the most in-demand skills over all the filters we have. However, you can further filter by country or seniority level to see what are the skills required at such level of details.

        Also, it is worth mentioning how many different job positions/titles are there for data scientists. So when you look for a new data scientist vacancy, you can search by these different titles.
        """
    )

    with match_calc:
        st.write('## Do your skills match a Data Science\'s Job Requirements?')
        st.info('Here, you can select the country, employment type, and seniority level, '
                'then add your current skills to show you your chance of matching the job '
                'requirements of your selected criteria.')

        country_sel_calc = st.multiselect(label='Select Country(s):', options=countries, default='All', key='country_sel_calc')
        employment_type_sel_calc = st.multiselect(label='Select Employment Type(s):', options=employment_types, default='All', key='emp_type_sel_calc')
        seniority_sel_calc = st.multiselect(label='Select Seniority Level(s):', options=seniority_levels, default='All', key='seniority_sel_calc')

        country_sel_mask = pd.Series([True] * len(df)) if country_sel in [['All'], []] else df.job_country.isin(country_sel)
        employment_type_sel_mask = pd.Series([True] * len(df)) if employment_type_sel in [['All'], []] else df.Employment_type.isin(employment_type_sel)
        seniority_sel_mask = pd.Series([True] * len(df)) if seniority_sel in [['All'], []] else df.Seniority_level.isin(seniority_sel)
        
        # Filter the data to the selected criteria
        df_filt_calc = df[country_sel_mask & employment_type_sel_mask & seniority_sel_mask].reset_index(drop=True)


        # Now, get the skills that the use have

        # Get the skills available after the previous filteration
        technical_skills = ['All'] + df_filt_calc.loc[df_filt_calc['Type'] == 'TECHNICAL', 'Skill'].value_counts().index.tolist()
        technology_skills = ['All'] + df_filt_calc.loc[df_filt_calc['Type'] == 'TECHNOLOGY', 'Skill'].value_counts().index.tolist()
        soft_skills = ['All'] + df_filt_calc.loc[df_filt_calc['Type'] == 'SOFT', 'Skill'].value_counts().index.tolist()
        business_skills = ['All'] + df_filt_calc.loc[df_filt_calc['Type'] == 'BUSINESS', 'Skill'].value_counts().index.tolist()

        technical_skills_sel = st.multiselect(label='Select Your Current Technical Skill(s):', options=technical_skills, default='All')
        technology_skills_sel = st.multiselect(label='Select Your Current Technology Skill(s):', options=technology_skills, default='All')
        soft_skills_sel = st.multiselect(label='Select Your Current Soft Skill(s):', options=soft_skills, default='All')
        business_skills_sel = st.multiselect(label='Select Your Current Business Skill(s):', options=business_skills, default='All')

        technical_skills_sel_mask = df_filt_calc.Type == 'TECHNICAL' if technical_skills_sel in [['All']] else df_filt_calc.Skill.isin(technical_skills_sel)
        technology_skills_sel_mask = df_filt_calc.Type == 'TECHNOLOGY' if technology_skills_sel in [['All']] else df_filt_calc.Skill.isin(technology_skills_sel)
        soft_skills_sel_mask = df_filt_calc.Type == 'SOFT' if soft_skills_sel in [['All']] else df_filt_calc.Skill.isin(soft_skills_sel)
        business_skills_sel_mask = df_filt_calc.Type == 'BUSINESS' if business_skills_sel in [['All']] else df_filt_calc.Skill.isin(business_skills_sel)

        print('technical skills', technical_skills_sel_mask.sum())
        print('technology skills', technology_skills_sel_mask.sum())
        print('soft skills', soft_skills_sel_mask.sum())
        print('business skills', business_skills_sel_mask.sum())

        sel_skills_df = df_filt_calc[technical_skills_sel_mask 
                                     | technology_skills_sel_mask 
                                     | soft_skills_sel_mask 
                                     | business_skills_sel_mask]

        calc_button = st.button('Calculate Matching Score')


        if calc_button:
            print(len(sel_skills_df), len(df_filt_calc))
            matching_score = len(sel_skills_df) / len(df_filt_calc)
            matching_score_df = pd.DataFrame({'Matching': ['Matching', 'Not Matching'], 'Score': [round(matching_score, 2), 1-round(matching_score, 2)]})
            fig2 = px.pie(matching_score_df, 
                          values='Score', 
                          names='Matching', 
                          hole=0.3, 
                          width=900, 
                          color_discrete_sequence=px.colors.qualitative.Vivid,
                          title='Your Chances of having a data science job with your current skills',
                          category_orders={'Matching':['Matching', 'Not Matching']}
                          )
            st.plotly_chart(fig2, use_container_width=True)