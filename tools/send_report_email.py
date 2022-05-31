def send_report_email(config, receiver_email, report_id):

    import smtplib, ssl
    message = """\
From: {smtp_sender}
To: {receiver_email}
Subject: Your Green Metric report is ready

Your report is now accessible under the URL: {url}/?id={report_id}

--
Green Coding Berlin
https://www.green-coding.org

    """
    message = message.format(
        receiver_email=receiver_email,
        report_id=report_id,
        url=config['project']['url'],
        smtp_sender=config['smtp']['sender'])

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config['smtp']['server'], config['smtp']['port'], context=context) as server:
        # No need to set server.auth manually. server.login will iterater over all available methods
        # see https://github.com/python/cpython/blob/main/Lib/smtplib.py
        server.login(config['smtp']['user'], config['smtp']['password'])
        server.sendmail(config['smtp']['sender'], receiver_email, message)

if __name__ == "__main__":
    import argparse
    import yaml
    import os
    from lib.setup_functions import get_config


    parser = argparse.ArgumentParser()
    parser.add_argument("receiver_email", help="Please supply a receiver_email to send the email to")
    parser.add_argument("report_id", help="Please supply a report_id to include in the email")

    args = parser.parse_args() # script will exit if arguments is not present

    config = get_config()

    send_report_email(config, args.receiver_email, args.report_id)
