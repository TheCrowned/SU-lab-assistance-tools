A script to send lab feedback and results to students.

It generates HTML emails with some rough formatting. In particular, it supports backticks \` for inline code and triple backticks \`\`\` for a block of code. I would have also wanted to add bold and italic with \* and \_, but when they get nested inside code blocks it gets quite messy, so I just gave up. I hardcoded some bold in the email templates, but we cannot put any in the feedback we write.

## How to run it
It supports a number of command line arguments, call it with `-h` to see the details.

Here a sample run:

`python3 send-results.py --course-name DA2004 --lab-n 2 --from-name "Stefano Ottolenghi" --from-email "stefano@math.su.se" --feedback-file ex-DA2004-lab2.txt`

This will take feedback contained in the file `ex-DA2004-lab2.txt`, build emails for it, and output them all in a single html file as a preview (which, if you are on linux, should pop up in the browser automatically - otherwise, look for a file called `preview-COURSENAME-LABN.html` in the directory where you run the script.

Adding the argument `--send` will instead result in emails being sent and no preview to be generated. As a sanity check, I used to have an email to myself as well at the top of the feedback list.

## Feedback structure
A sample file containing feedback `ex-DA2004-lab2.txt` is provided so you can have a look at the structure yourself, but the constraints to keep in mind when noting down the feedback are (important!):

- different students are separated by 2 empty lines. That is, after the feedback of a student, hit enter 3 times.
- for each student, the structure is

```
Name
Email
Status (one among [pass, fail, review, none])
- * first feedback line
- second feedback line

even with an empty line it's okay, as long as it's not 2 (otherwise it becomes a new student)
- last feedback line
```

If there is no specific feedback for a student, still include a point

My convention is to note with a star the feedback points that were compulsory to be corrected to pass the lab, in case the current result was fail. I also always put them at the top for clarity.

The current statuses are `pass, minor, review, fail, none` and should all be self-explanatory, except for `none`. That is used for a student who did not submit anything for that lab. The only manual work needed at course start is to create a feedback template file, with all students names and emails and the correct structure, to duplicate and to write into for every lab.

## Email templates
The actual texts of the emails are contained the three text files inside the directory `mail-templates`. There must be a file `status.txt` for each of the statuses we have. It should be straightforward to add a new status in the future (i.e. add the status to a list in the script and provide the corresponding email template in the directory).

Email templates _can_ contain HTML markup, plus a number of placeholders that are replaced per-mail with dynamic content. Supported placeholders are `{to-name}, {to-email}, {from-name}, {from-email}, {course-name}, {course-teacher}, {lab-n}, {tips-list}`.

## Notes on code maintenance
I have tried to make the code as much general as possible, so that it can be used by many people for multiple courses. Look at the two variables `statuses` and `course_teachers` to add additional statuses and courses.
