import streamlit as st
from helper import *
from user_definition import *
from google.oauth2 import service_account
from google.cloud import aiplatform
from PIL import Image


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ['GOOGLE_API_KEY']

st.set_page_config(layout="wide")

# Streamlit App
st.title('Job Search')
st.markdown('Job matching application designed for Data Science oriented people. Select your ideal job title, location, and upload your resume as a pdf.')
st.markdown('Using text matching, this app will output the 5 most optimal job listings for your criteria.')

# Display job statistics
st.subheader(':blue[Job Statistics]             :chart:')
stats_df = get_stats_data()
n = stats_df['total_jobs'].sum()
stats_df = stats_df.rename(columns={"searchTitle": "Job Title", "total_jobs": "Total Number of Jobs",
                                    'average_salary': 'Average Salary', 'city': 'Total Number of Cities', 'state': 'Total Number of States'})
st.write(stats_df)

# Select Location
st.subheader(":violet[Enter location]       :world_map:")
location_options = ['New York', 'San Francisco', 'Chicago', 'Los Angeles', 'Seattle']
selected_location = st.button(location_options[0], key=location_options[0]) or \
                    st.button(location_options[1], key=location_options[1]) or \
                    st.button(location_options[2], key=location_options[2]) or \
                    st.button(location_options[3], key=location_options[3]) or \
                    st.button(location_options[4], key=location_options[4])

if selected_location:
    st.write(f'Selected Location: {selected_location}')
else:
    st.write('No location selected')    

# Select Job Title
st.subheader(":blue[Enter Job Title]      :bar_chart:")
job_title_options = ['Data Scientist', 'Data Analyst', 'Machine Learning Engineer']
selected_job_title = st.button(job_title_options[0], key=job_title_options[0]) or \
                     st.button(job_title_options[1], key=job_title_options[1]) or \
                     st.button(job_title_options[2], key=job_title_options[2])

if selected_job_title:
    st.write(f'Selected Job Title: {selected_job_title}')
    st.session_state['selected_job_title'] = selected_job_title
else:
    st.write('No job title selected')

st.sidebar.image("images/usf_logo.png", use_column_width=True)
st.sidebar.image("images/job.png", use_column_width=True)

# File uploader for PDF
st.subheader(":violet[Upload your resume]      :file_folder:")
resume = st.file_uploader("", type="pdf")

if resume is not None:
    # Submit Button
    if st.button(':rainbow[Find Jobs]'):
        # Processing and display result
        st.write('Processing ...')
        resume_text = parse_resume(resume)
        with st.spinner('Searching best jobs for you ...'):
            jobs_result = find_jobs(st.session_state['selected_job_title'], resume_text)

        for i, row in jobs_result.iterrows():
            st.markdown(f"## {row['companyName']}")
            st.markdown(f"### {row['title']}")
            st.write(f"Similarity Score: {round(row['similarity_score'],2)}")
            st.write(f"Location: {row['location']}")
            st.write(f"Salary: {row['salary']}")
            st.write(f"Job URL: {row['jobUrl']}")
            st.write(f"Matching Points:")
            st.write(f"{row['matching_points']}")
            st.markdown("---")

