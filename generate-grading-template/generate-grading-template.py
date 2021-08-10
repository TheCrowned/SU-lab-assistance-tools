"""
Rough script to generate text grading templates from PeerGrade/Moodle csv files.
Output can then be fed to the send-results script.

@author Stefano Ottolenghi <stefano@math.su.se>
        Thanks to Emilia Dunfelt for suggestions/testing.
@date August 2021
"""

import argparse
import csv
from math import floor

def main():
    # Get arguments from commandline - call with -h for help
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--csv',
        required=True,
        dest='csv_file',
        help='Path to csv file to parse (with names/emails/lab status)')
    parser.add_argument(
        '--lab-n',
        required=False,
        type=int,
        dest='lab_n',
        help='Lab number feedback is about')
    parser.add_argument(
        '--TAs',
        required=False,
        type=int,
        dest='TAs_total',
        help='The total number of TAs among whom the grading is split')
    parser.add_argument(
        '--TA-n',
        required=False,
        type=int,
        dest='TA_n',
        help='The TA ID for which you wish to see the students list to grade')
    parser.add_argument(
        '--no-enforce-reviews',
        default=True,
        action='store_false',
        dest='enforce_reviews',
        help='Whether grading status should (not) be set to `minor` if PeerGrade reviews were not done')
    args = parser.parse_args()

    # Shortcuts
    csv_path = args.csv_file
    enforce_reviews = args.enforce_reviews
    N = args.lab_n
    M = args.TAs_total
    K = args.TA_n

    # Proper main
    students = parse_csv_to_dict(csv_path)
    students = maybe_purge_nohandin_students(students)
    J = len(students)

    if N == None or M == None or K == None:
        print('Lab N, TAs total or TA_n is missing, so you will just get a grading template for all students.')
        filename = 'grading-template.txt'
        dump_students_to_file(students, filename, False)

    else:
        # How many students should there be in each group? z is group ID
        how_many = lambda z: int(floor(J/M) + ((J%M - (z-1))>0))

        # Build list with indexes of each group boundaries
        groups = [(0, how_many(1))]
        for i in range(2, M+1):
            groups.append((groups[-1][1], groups[-1][1] + how_many(i)))

        # Pick group for given TA according to rotation
        group_choser = ((N-1)+(K-1)) % M
        start_index = groups[group_choser][0]
        end_index = groups[group_choser][1]

        print('TA {} takes {} out of {} students, with indexes {}'.format(K, end_index-start_index, J, groups[group_choser]))
        filename = 'lab{}-TA{}.txt'.format(N, K)
        dump_students_to_file(students[start_index:end_index], filename, enforce_reviews)


def parse_csv_to_dict(csv_path):
    """Parses csv into a dict

    Input
    -----
    csv_path : string
        Path to csv file containing student info.

    Output
    ------
    students : dict
        Alphabetically sorted dict of students with info from csv.
    """

    students = []
    with open(csv_path, 'r') as handle:
        csvreader = csv.DictReader(handle)
        fields = csvreader.fieldnames

        for row in csvreader:
            student = {
                'name' : row[fields[0]],
                'email' : row[fields[1]],
            }

            # If file has info about current lab (ie comes from peergrade), use it
            if len(fields) > 2:
                student['lab_handedin'] = row[fields[2]]
            # If file has info about peergrading, use it
            if len(fields) > 3:
                student['reviews'] = row[fields[3]]

            students.append(student)
            # enforce alphabetical sort by name
            students = sorted(students, key=lambda k: k['name'])

    return students


def maybe_purge_nohandin_students(students):
    """Remove students that did not hand in."""

    purged_students = []
    for student in students:
        if student.get('lab_handedin'):
            if student['lab_handedin'] == 'Yes':
                purged_students.append(student)
        else: #lacking handin info
            purged_students.append(student)

    return purged_students


def dump_students_to_file(students, filename, enforce_reviews):
    """Write a grading template text file that can be later used with send-results.py.

    Input
    -----
    students : dict
    filename : str
        Output file name
    enforce_reviews : bool
        If True, students who did not complete reviews will automatically get
        `minor` as status, and a note about not having completed reviews.
    """

    with open(filename, 'w') as handle:
        for student in students:
            handle.write('{}\n'.format(student['name']))
            handle.write('{}\n'.format(student['email']))

            if (enforce_reviews == True
            and student.get('reviews') and student['reviews'][0] == '0'):
                handle.write('minor\n') #status is minor is reviews were not done
                handle.write('- * PeerGrade reviews were not done.\n')
            else:
                handle.write('none\n')

            handle.write('\n\n') #spacing between students


if __name__ == '__main__':
    main()