A script to generate template feedback files from PeerGrade/Moodle csv files. It automatically splits the students among TAs. The output files can then be used as a starting point for grading and fed to the `send-results` script for mailing.

TAs need to agree to a numbering at the beginning of the course. For example, if there are a total of 3 TAs, then it must be clear who has ID 1, 2 and 3. This numbering will be kept for the whole course.

A sample run is

`python generate-grading-template.py --csv FILENAME [--lab-n N --TAs M --TA-n K --no-enforce-reviews]`

where

- `FILENAME` is the path to the csv file containing the lab/students info. This can either come from the `Summary` tab of a PG class (PG > Course > Summary > Toggle Columns > check _Name_, _Email_, and _Submissions completed_, _Reviews completed_ of the relevant lab you are grading (scroll down the list)) or from Moodle (participants list).
- `N` is the lab number.
- `M` is the total number of TAs among which the lab correction should be splitted.
- `K` is the ID of the TA that is running the script.

**If N, M, K are given**, the script will automatically split the students among TAs and output a text file containing the students that the `K`-th TA should grade, ready-made to work with the `send-results` script. It will also automatically rotate the groups so that one TA will get a different group of students to grade each time (for `M` times, then it cycles back) - and it is deterministic, so it is possible to re-run it in the future (or on another machine) and obtain who should (have) correct(ed) what.

**If the csv comes from PeerGrade** (i.e. if it has handin/reviews info), the script will also

- remove any student who did not hand in from the output;
- set the grading status to `minor` if reviews were not done, appending a note to the feedback list. If this is unwished, it can be turned off with the flag `--no-enforce-reviews`.

**If N, M, or K are not given**, the script will just spit a grading template will all students together.

**How does it work?** Basing on ~~a sophisticated piece of math~~ an empirically-derived formula with many modulo operations. It just seems to work. Check lines 66 to 77 if you are curious.