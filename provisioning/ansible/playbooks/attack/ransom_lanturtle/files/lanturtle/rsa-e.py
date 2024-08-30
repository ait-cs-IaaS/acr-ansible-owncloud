#!/usr/bin/env python3

# pip3 install beautifulsoup4
from bs4 import BeautifulSoup as bs

# READ HTML_CONTENT IN VARIABLE
html_file = open('rsa.html', 'r')
html_content = html_file.read()
html_file.close()

# create html-parser
soup = bs(html_content,'html.parser')

# lookup all pre bodies
for pre in soup.body.find_all('pre', recursive=False):
    # remove the first line(with command:) and 
    # store it in an array
    only_rsa = pre.text.split('\n')[2:]
    # we don't want an array, we want a string
    # so we join it again
    print("\n".join(only_rsa))
