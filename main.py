from time import sleep as delay
from datetime import datetime as timestamp
from bs4 import BeautifulSoup as prepare_beautiful_soup
from difflib import context_diff
from difflib import Differ as differentiator
from requests import get as make_get_request
from send_email import main_send_email as send_alert

url = "http://127.0.0.1:5500/index.html"
prev_version = ""
first_run = True
flag = True

from_email = "gaurang.ambasana@dev2.wipro.com"
to_emails = "kevin.sanghavi1@dev2.wipro.com"
email_subject = "test mail"
html_msg = "Hi<br/><br/>HTML MSG"
file_path = "F:\web development\monior-changes-on-webpage\changelog.txt"


def get_plain_str(iterator_str):
    return "\n".join([line.rstrip() for line in '\n'.join(iterator_str).splitlines() if line.strip()])


def compare_content(old_content, new_content):
    return context_diff(old_content, new_content)


def compare_entire_contect(old_content, new_content):
    return differentiator().compare(old_content, new_content)


def create_changelog_file(difference):
    current_time = str(timestamp.now()).replace(" ", "_")

    text = '--> Changes detected at : ' + current_time + \
        ' for webpage :' + url + '\n\n' + difference + \
        '\n\n---------------------------------------------------\n\n'

    file_path = "F:\web development\monior-changes-on-webpage\changelog.txt"

    with open(file_path, 'r') as file:
        og_data = file.read()

    with open(file_path, 'w') as file:
        file.write(text + og_data)

    print("-> Changelog updated!")


def get_soup_without_script_n_style(html_data):
    soup = prepare_beautiful_soup(html_data.text, "lxml")

    tags_to_exclude = ["script", "style"]

    for tag in soup(tags_to_exclude):
        tag.extract()

    new_soup = soup.get_text()

    return new_soup


def show_error_msg(error):
    print("Request failed for URL : " + url + "\nReason : " + str(error))


def send_GET_request_like_browser(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    res = make_get_request(url, headers=headers)

    return res


while flag:

    try:
        response = send_GET_request_like_browser(url)
    except Exception as ex:
        show_error_msg(ex)
        flag = False
        break

    res_soup = get_soup_without_script_n_style(response)

    if prev_version != res_soup:
        if first_run == True:
            first_run = False
            prev_version = res_soup

            print("Now, Monitoring " + url + " at " + str(timestamp.now()))
        else:
            print("Changes detected at: " + str(timestamp.now()))

            old_page = prev_version.splitlines()
            new_page = res_soup.splitlines()

            entire_page_difference = compare_entire_contect(old_page, new_page)
            only_different_content = compare_content(old_page, new_page)

            difference_str = get_plain_str(only_different_content)
            page_difference_str = get_plain_str(entire_page_difference)

            create_changelog_file(page_difference_str)
            send_alert(from_email, to_emails,
                       email_subject, html_msg, file_path)
            print(difference_str)

            old_page, prev_version = new_page, res_soup
    else:
        print("No Changes Detected till : " + str(timestamp.now()))

    delay(5)
    continue
