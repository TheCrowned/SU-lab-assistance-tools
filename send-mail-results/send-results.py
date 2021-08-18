'''
Rough script to email lab results to students.

@author Stefano Ottolenghi <stefano@math.su.se>
@date January 2021
'''

import smtplib
import ssl
import re
import unicodedata
import argparse
from getpass import getpass
from os import system
import sys

# Expects to find a file with name STATUS.txt
# for each STATUS below, located in the directory mail-templates
statuses = ['pass', 'minor', 'review', 'fail']

# Teachers to whom to send revisions (for plagiarism checks)
courses_teachers = {
    'DA2004': 'Anders Mörtberg',
    'DA2005': 'Lars Arvestad',
    'MM5016': 'Stefano Ottolenghi' #for labs
}

# Get arguments from commandline - call with -h for help
parser = argparse.ArgumentParser()
parser.add_argument(
    '--from-name',
    required=True,
    dest='from_name',
    help='Name from which email is shown to come from')
parser.add_argument(
    '--from-email',
    required=True,
    dest='from_email',
    help='Email from which email is shown to come from')
parser.add_argument(
    '--lab-n',
    required=True,
    type=int,
    dest='lab_n',
    help='Lab number feedback is about')
parser.add_argument(
    '--course-name',
    required=True,
    dest='course_name',
    help='Course name you are working with (ex. DA2004)')
parser.add_argument(
    '--feedback-file',
    required=True,
    dest='feedback_file',
    help='File path in which feedback for this lab is to be found.')
parser.add_argument(
    '--feedback-lang',
    required=True,
    dest='feedback_lang',
    help='Language of feedback template (only en/se supported)')
parser.add_argument(
    '--send',
    #type=bool,
    default=False,
    action='store_true',
    dest='no_dry_run',
    help='Simulate email sending without actually sending them')
args = parser.parse_args()

print() #nice output

try:
    course_teacher = courses_teachers[args.course_name]
except Exception:
    print('No match for teacher with the given course name. Is the name {} correct?'.format(args.course_name))
    sys.exit()

print('== On behalf of {} <{}>; lab {} of course {} ==\n'.format(
    args.from_name, args.from_email, args.lab_n, args.course_name))

# Fetch templates for all statuses
templates = {}
for status in statuses:
    with open('mail-templates/'+args.course_name+'/'+status+'_'+args.feedback_lang+'.txt', encoding='utf-8') as f:
        templates[status] = f.read().replace("\n", "<br />\n")

# open file to store feedback preview on dry run
if not args.no_dry_run:
    preview = open('preview-{}-lab{}.html'.format(args.course_name, args.lab_n, encoding='utf-8'), 'w')

headers = """From: {from-name} <{from-email}>
To: {to-name} <{to-email}>
Subject: Result of Lab {lab-n} ({course-name})
MIME-Version: 1.0
Content-Type: text/html; charset="UTF-8"

"""
#the trailing line break in headers matters!

# we first create all emails and then send them after
emails = {}

#Open a connection with smtp.su.se and authenticate
if args.no_dry_run:
    try:
        server = smtplib.SMTP_SSL("smtp.su.se", 465, context=ssl.create_default_context())
        username = input("Enter SU username: ")
        password = getpass("Enter SU account password: ")
        server.login(username, password)
        #when connected from SU network, login seems not needed
    except Exception as e:
        print('Fail to connect/authenticate. Check credentials and retry.\n'+str(e))
        sys.exit()

print() #nice output

#with open('{}-lab{}.txt'.format(args.course_name, args.lab_n)) as lab_feedback:
with open(args.feedback_file, encoding='utf-8') as lab_feedback:
    stats = {status: [] for status in statuses}; skipped = [] # for final counts

    #different students are separated by 3 newlines
    students = lab_feedback.read().split('\n\n\n')

    for student in students:
        splitted_single = student.split('\n')

        # empty students are probably just trailing file empty lines
        if len(splitted_single) == 0:
            continue

        stud_name = splitted_single[0]
        stud_email = splitted_single[1]
        status = splitted_single[2]

        if len(splitted_single) >= 4 and '-' in splitted_single[3]:
            tips_list = student[student.find('- '):].strip()
        else:
            tips_list = '<em>Nothing special to say for this lab!</em>'

        # pick correct email template depending on lab student status
        if status == 'none': #skip students with none status
            skipped.append(stud_name)
            continue
        else:
            mail_content = templates[status]
            stats[status].append(stud_name)

        #swedish chars in names need to go away
        #for runtime errors on this line, make sure you running with python3
        #stud_name = unicodedata.normalize('NFKD', stud_name).encode('ascii', 'ignore').decode()

        #concatenate headers and replace placeholders in templates
        mail_content = headers + mail_content
        mail_content = mail_content.replace('{to-name}', stud_name)
        mail_content = mail_content.replace('{to-email}', stud_email)
        mail_content = mail_content.replace('{from-name}', args.from_name)
        mail_content = mail_content.replace('{from-email}', args.from_email)
        mail_content = mail_content.replace('{course-name}', args.course_name)
        mail_content = mail_content.replace('{course-teacher}', course_teacher)
        mail_content = mail_content.replace('{lab-n}', str(args.lab_n))

        #tips should be a bulleted list with dashes
        mail_content = mail_content.replace('{tips-list}', tips_list.replace("\n", "<br />\n"))

        mail_content = re.sub(r"```([^`]+)```", "<pre>\g<1></pre>", mail_content)
        mail_content = re.sub(r"`([^`]+)`", "<code>\g<1></code>", mail_content)

        #underscores/stars are often in code, difficult to parse -> avoid
        #mail_content = re.sub(r"_([^_]+)_", "<em>\g<1></em>", mail_content)
        #mail_content = re.sub(r"\*([^\*]+)\*", "<strong>\g<1></strong>", mail_content)

        # utf-8 encode (supports swedish chars)
        mail_content = mail_content.encode('utf-8')

        emails[stud_email] = {
            'stud_email': stud_email,
            'stud_name': stud_name,
            'content': mail_content
        }

        # decode utf-8 bytes before append
        if not args.no_dry_run:
            preview.write(mail_content.decode('utf-8')+'<br /><hr /><br />')


# open preview in browser if dry run
if not args.no_dry_run:
    system('sensible-browser "preview-{}-lab{}.html"'.format(args.course_name, args.lab_n))

# actually send emails otherwise
else:
    for email in emails.values():
        print('Mailing {} ({})'.format(email['stud_name'], email['stud_email']))
        server.sendmail(args.from_email, email['stud_email'], email['content'])
    server.close()

# print stats
for status in statuses:
    print('\n== {} students with status {} =='.format(len(stats[status]), status))
    print('\n'.join(map(str, stats[status])))
print('\n== {} students skipped =='.format(len(skipped)))
