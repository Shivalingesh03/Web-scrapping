from flask import Flask, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup 
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,current_user,login_manager

app = Flask(__name__)


@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/scrap', methods=['POST'])
def index(): 
    if request.method == 'POST':
        skills = request.form['skills'].split()
        location = request.form['location']
        date_posted = int(request.form['dateposted'])
        experience = int(request.form['experience'])

        url = f"https://www.techgig.com/job_search?page=1&txtKeyword={'+'.join(skills)}&cboWorkExp1={experience}&NoOfDaysSincePosted={date_posted * 7}&keyword=&txtLocation={location}"

        print("-----TECHGIG-----")
        html_text = requests.get(url)
        soup = BeautifulSoup(html_text.text, 'html.parser')

        jobs = soup.find_all('div', class_='col-md-6 col-sm-12')
        techgig_list = []
        for job in jobs:
            job = job.find('div', class_='job-box-lg')
            company = job.find('div', class_='job-header clearfix').find('div', class_='details full-width').p.text
            title = job.find('div', class_='job-header clearfix').find('div', class_='details full-width').h3.text
            contents = job.find('div', class_='job-content').find('dl', class_='description-list').find_all("dd")
            more_details = job.find('div', class_='job-footer clearfix').a['href']
            experience = contents[0].text
            ctc = contents[1].text
            skills = contents[2].text
            posted = job.find('div', class_='job-footer clearfix').span.text.split()
            posted = posted[2] + ' ' + posted[3]

            techgig_dict = {
                "title": title,
                "company": company,
                "experience": experience,
                "ctc": ctc,
                "skills": skills,
                "posted": posted,
                "details": more_details
            }
            techgig_list.append(techgig_dict)
        print(techgig_list)
        return render_template('results.html', techgig_list=techgig_list)

# def index():
    # skills = request.form['skills'].split()
    # location = request.form['location']
        # date_posted = int(request.form['dateposted'])
        # experience = int(request.form['experience'])
        
    # for page in range(0, 1):
    # if page == 0:
    website_link = f'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from' \
                           f'=submit&txtKeywords={skills}&txtLocation={location} '
            # else:
            #  website_link = f'https://www.timesjobs.com/candidate/job-search.html?from=submit&actualTxtKeywords={skills}' \
            #                f'&searchBy=0&rdoOperator=OR&searchType=personalizedSearch&luceneResultSize=25' \
            #                f'&postWeek=60&txtKeywords=data%20scientist&pDate=I&sequence=2&startPage={page} '

    times_list=[]
    html_file = requests.get(website_link).text
    soup = BeautifulSoup(html_file, 'lxml')
    job_list = soup.find_all('li', class_="clearfix job-bx wht-shd-bx")
    for job in job_list:
      post_date = job.find('span', class_="sim-posted").span.text
      print(f"Job Post Date: {post_date}")
      company_name = job.find('h3', class_="joblist-comp-name").text
      print(f"Company Name - {company_name.strip()}")
      job_description = job.find('ul', class_="list-job-dtl clearfix").li.text.replace('Job Description:',
                                                                                       '').replace('  ', ' ')
      
      experience_level = job.find('ul', class_="top-jd-dtl").li.text.replace('card_travel', '')
      location = job.find('span').text.replace('  ', ' ')
      key_skills = job.find('span', class_="srp-skills").text.replace('  ', ' ').replace(' ,', ',')
  
    
    # dict_for_df = {'CompanyName': company_name, 'Location': location, 'Experience': experience_level'Skills': key_skills, 'Job Description': job_description, 'Posted Date': post_date}
      times_dict = {
        
        "company": company_name,
        "experience":  experience_level,
        
        "skills": key_skills,
        "posted":  post_date,
        "details": job_description 
    }
    times_list.append(times_dict)


    return render_template('results.html', times_list=times_dict)




if __name__ == "__main__":
    
    app.run(port=5500,debug=True)