import sys
import smtplib
import requests
import time
import json
from datetime import datetime, date, timedelta

def check_availability(center_list=[]):
    appointments = set()
    for center in center_list:
        session_list = center["sessions"]
        hospital = center["name"]
        session_max_date = datetime.combine(date.today(), datetime.min.time())
        for session in session_list:
            date_str = session["date"]
            sess_date = datetime.strptime(date_str, '%d-%m-%Y')
            min_age_limit = int(session["min_age_limit"])
            # print(min_age_limit)
            if min_age_limit == 18:
                availability = int(session["available_capacity"])
                vaccine_name = session["vaccine"]
                if availability > 0:
                    # print('reached')
                    sess_date_str = sess_date.strftime('%d-%m-%Y')
                    appointment = f"{vaccine_name} available at {hospital} on {sess_date_str}"
                    appointments.add(appointment)
    return appointments


def main_task(email_sess, email, recv_email):
    min_date = date.today()
    available_appointments = set()
    while True:
        date_str =  min_date.strftime('%d-%m-%Y')
        url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=149&date={date_str}"
        # print(url)
        data = requests.get(url)
        data = data.text
        data = json.loads(data)
        center_list = data["centers"]
        # print(center_list)
        if len(center_list) > 0:
            available_appointments = available_appointments | check_availability(center_list)
            break
        min_date += timedelta(days = 1)
    # print(available_appointments)
    if len(available_appointments) > 0:
        send_mail(available_appointments, email_sess, email, recv_email)


def send_mail(appointments, sess, email, recv_email):
    message = ""
    for appointment in appointments:
        message += f"{appointment} \n"
    # print(message)
    # print("sendinng mail")
    sess.sendmail(email, recv_email, message)
    # print("mail sent")


def run(email_sess, email, recv_email):
    while True:
        main_task(email_sess, email, recv_email)
        time.sleep(60*10)

if __name__ == "__main__":
    email = sys.argv[1]
    pwd = sys.argv[2]
    recv_email = sys.argv[3]
    sess = smtplib.SMTP('smtp.gmail.com', 587)
    sess.starttls()
    sess.login(email, pwd)
    # sess.sendmail(email, recv_email, "Subscribed to Vaccine appointments")
    run(sess, email, recv_email)
    sess.quit()


