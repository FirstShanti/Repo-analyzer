info='''
| Github grabber v.2.0           |\
\n| Author: Vladislav Shevchenko   |\
\n| https://github.com/FirstShanti | \
\n| shev.vlad.ua@gmail.com         | \n'''

man = '''

usage: start.py url [-s start date] [-e end date] [-b branch]

example: start.py https://github.com/pallets/flask -s 2020-01-01T12:34:56 -e 2020-03-01 -b 1.1.x

Options: 
url    : Url of public github repository,
         Required!
         Format: https://github.com/<username>/<repository>
-s     : Start date of analysis range
         Format: YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DD
         Not required (The default value is the date the repository was created)
-e     : End date of analysis range
         Format: YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DD
         Not required (The default value is the date the script was run)
-b     : Branch of repository
         Not required (The default value is 'master')

'''

man_no_auth = '''
For authorization, go to config.py file and put you personal access <token> (https://github.com/settings/tokens) variable "TOKEN"

$nano ./config.py
'''