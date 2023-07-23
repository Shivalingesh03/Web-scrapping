'''
v2
Dynamic searching made possible
'''
from flask import Flask, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup 
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin,login_user,login_required,current_user,login_manager

# conn= mysql.connector.connect(host='localhost',port='5500',database='logindb',user='root',password='root')


app = Flask(__name__)
app.secret_key="super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/logindb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db= SQLAlchemy(app)

class User(db.Model):
    # __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True,unique=True)
    email=db.Column(db.String(50),nullable=False)
    username = db.Column(db.String(50), unique=False, nullable=False)
    pwds = db.Column(db.String(50), nullable=False)
    
    # def __init__(self,email,username,pwds):
    #     self.username = username
    #     self.email= email
    #     self.pwds= pwds
 
    # def __repr__(self):
    #     return f"{self.username}:{self.email}:{self.pwds}"


db.init_app(app)



@app.route('/', methods=['GET','POST'])
def loginpage():
    if request.method == 'POST':
        email = request.form.get['email']
        password = request.form.get['password']

        # Check if the username exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the password matches
            if user.password == password:
                # Authentication successful, redirect to the homepage or another route
                return redirect(url_for('index'))
            else:
                # Authentication failed, display an error message or redirect to the login page
                return render_template('login.html', error='Invalid password')
        else:
            # Authentication failed, display an error message or redirect to the login page
            return render_template('login.html', error='Invalid username')

    return render_template('login.html')

@app.route('/reg', methods=['GET','POST'])
def regpage():
    
    if request.method == 'POST':
        username = request.form.get['username']
        email=request.form.get['email']
        password = request.form.get['password']
        
        entry=User(username=username,email=email,pwds=password)
      
        # Add the new user to the database
        db.session.add(entry)
        db.session.commit()

        # Registration successful, redirect to a success page or another route
        return redirect(url_for('index'))
    return render_template('reg.html')



@app.route('/index', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/scrap', methods=['POST'])
def index():
    skills = request.form['skills'].split()#input("Looking for a job in the field? (python, java, etc) : ").split()
    location = request.form['location']#input("Location ? : ").lower()
    date_posted = request.form['dateposted']#int(input("How recent? 1 - for 1 week, 2 - 2 week, 0 - None : "))
    experience = request.form['experience']#int(input("Previous experience : 0 - fresher, 1 for 1 year and so on : "))
    techgig_find_jobs(skills, location, date_posted, experience)
    # times_find_jobs(skills, location, date_posted, experience)


def techgig_find_jobs(skills, location, date_posted, experience):

    url = f"https://www.techgig.com/job_search?page=1&txtKeyword={'+'.join(skills)}&cboWorkExp1={experience}&" \
          f"NoOfDaysSincePosted={date_posted * 7}&keyword=&txtLocation={location}"

    # print("URL : "+url)
    print("-----TECHGIG-----")

    html_text = requests.get(url)
    soup = BeautifulSoup(html_text.text, 'xml')
    box = soup.find('div', class_='row')
    jobs = box.find_all('div', class_='col-md-6 col-sm-12')
    techgig_list=[]
    
    # print(jobs)
    for job in jobs:
        job = job.find('div', class_='details')
        company = job.find('div', class_='job-header clearfix').find('div', class_='details').p.text
        title = job.find('div', class_='job-header clearfix').find('div', class_='details').h3.text
        contents = job.find('div', class_='job-content').find('dl', class_='description-list').find_all("dt")
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
        # return render_template('results.html', techgig_list=techgig_list)
        
        # print(contents) # For debugging process

        print(f"Job title : {title}\nCompany Name : {company}\nExperience  : {experience}\nCTC : {ctc}\n"
              f"Skills : {skills}\nPosted : {posted}\nMore details : {more_details}")
        print("\n")


# def times_find_jobs(skills, location, date_posted, experience):
    print("-----Timesjobs-----")

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
      techgig_dict = {
        
        "company": company_name,
        "experience":  experience_level,
        
        "skills": key_skills,
        "posted":  post_date,
        "details": job_description 
    }
    techgig_list.append(techgig_dict)


    return render_template('results.html', techgig_list=techgig_dict)


if __name__ == '__main__':
    app.run(port=5500,debug=True)
    '''while True:
        times_find_jobs()
        time_wait = 10
        print(f"Waiting {time_wait} minutes...")
        time.sleep(time_wait * 60)'''
    # techgig_find_jobs()
    # times_find_jobs()
    # index()
