#!/usr/bin/python3.6
# -*- coding: utf8 -*-
import os
import time
import re
import argparse
from random import randint
from datetime import datetime, timedelta
from slackclient import SlackClient
from logger import setup_logger
import logging


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

setup_logger(logger_name="slackbot",log_file="slackbot.log", stream="N")
botlog = logging.getLogger("slackbot")

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
NOTIFY = []

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
LIVE_BOT = 'ping'
ALT_MONITOR_SUB = 'sub'
ALT_MONITOR_UNSUB = 'unsub'
MONITOR_TODAY = 't0'
MONITOR_TOMOR = 't1'
MONITOR_TOMOR2 = 't2'
SENT2CHANNEL = 'send'
SETCHANNEL = 'setchannel'

LUNCH_TIME = '11:45:00'
WORK_TIME = '12:45:00'

PUBLIC_CHANNEL = "C1ATEGSQ5"
TEST_CHANNEL = "GBZ5T4CUQ"

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

LICHTRUC = [2,3,1]
TODAY = None
TEAM = {'1':'@rin, @tanvuong', '2':'@huyenluong.vu, @nguyennam1991', '3':'@mickey, @tam.nguyen'}
DAYWORK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
WEEKENDAY = ['Fri', 'Sat']
WEEKENDAY2 =  ['Sat', 'Sun']
FRIDAY = 'Fri'
SATDAY = 'Sat'
SUNDAY = 'Sun'
HOURNOTIFY = 17

def parse_bot_commands(slack_events):
    global  starterbot_id
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def append_channel(channel):
    global NOTIFY
    if channel not in NOTIFY:
        NOTIFY.append(channel)
        botlog.debug("Appen_channel >> %s" % (channel))

def remove_channel(channel):
    global NOTIFY
    if channel in NOTIFY:
        NOTIFY.remove(channel)
        botlog.debug("Remove_channel >> %s" % (channel))

def handle_command(command, channel):
    global NOTIFY
    global TODAY

    botlog.debug("command: %s, channel: %s" % (command, channel))
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Hehe, bạn nói gì mình không hiểu, thử gõ @altbot do."

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = """Chào bạn, mình là altBot thuộc cty ALTISSS,
Mình là botchat hỗ trợ thông báo lịch monitor:
    + Để nhận thông báo gõ: @altBot sub
    + Bỏ nhận thông báo gõ: @altBot unsub
    + Kiểm tra lịch :
    \t- Hôm nay : @altBot t0
    \t- Ngày mai: @altBot t1
    \t- Ngày mốt: @altBot t2
CÁM ƠN BẠN ĐÃ SỬ DỤNG altBot nhé :joy:"""
    elif command.startswith(SENT2CHANNEL):
        target = command.split("|")[1]
        text = command.split("|")[2]
        channel = target
        response = text
    elif command.startswith(SETCHANNEL):
        try:
            newchannel = command.split(" ")[1]
            append_channel(newchannel)
            response = "Channel [%s] vừa được kích hoạt nhận thông báo" % (newchannel)
        except:
            botlog.debug("Error command (%s)" % (command))
    elif command.startswith(LIVE_BOT):
        response = "Sure... I'm heartbeat with you"
    elif command.startswith(ALT_MONITOR_SUB):
        append_channel(channel)
        response = "Đã kích hoạt để nhận thông báo"
    elif command.startswith(ALT_MONITOR_UNSUB):
        remove_channel(channel)
        response = "Đã hủy kích hoạt nhận thông báo"
    elif command.startswith(MONITOR_TODAY):
        today = datetime.now()
        NameDay = str(today.now().strftime('%a'))
        if TODAY != None:
            response = "Lịch monitor hôm nay (%s) là (%s)" % (str(today.strftime("%a, %d %b %Y")), TEAM[str(TODAY)])
        else:
            response = "Hình như bạn chưa subscribe để nhận thông báo lịch monitor !!! Thử gõ @altBot %s" % (ALT_MONITOR_SUB)
            if NameDay in WEEKENDAY2:
                response = "Chúc bạn cuối tuần vui vẻ :kissing_heart: !!!"
    elif command.startswith(MONITOR_TOMOR):
        today = datetime.now()
        Dhour = str(today.strftime('%H'))
        NameDay = str(today.now().strftime('%a'))
        tomor = today + timedelta(1)

        if NameDay in WEEKENDAY:
            response = "Ngày mai không monitor nhé cậu ^^, ở nhà dành thời gian cho gia đình/bạn bè nè"
        else:
            if int(Dhour) >= int(HOURNOTIFY) or NameDay == SUNDAY:
                response = "Lịch monitor ngày mai (%s) là (%s)" % (str(tomor.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[0])])
            else:
                response = "Lịch monitor ngày mai (%s) là (%s)" % (str(tomor.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[1])])
    
    elif command.startswith(MONITOR_TOMOR2):
        today = datetime.now()
        Dhour = str(today.strftime('%H'))
        NameDay = str(today.now().strftime('%a'))
        tomor2 = today + timedelta(2)

        if NameDay == FRIDAY:
            response = "Ngày mốt không monitor nhé cậu ^^, ở nhà ngủ cho thoải thích nhé :kissing_heart:"
        elif NameDay == SATDAY:
            response = "Lịch monitor ngày mốt (%s) là (%s)" % (str(tomor2.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[0])])
        elif NameDay == SUNDAY:
            response = "Lịch monitor ngày mốt (%s) là (%s)" % (str(tomor2.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[1])])
        else:
            if int(Dhour) >= int(HOURNOTIFY):
                response = "Lịch monitor ngày mốt (%s) là (%s)" % (str(tomor2.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[1])])
            else:
                response = "Lịch monitor ngày mốt (%s) là (%s)" % (str(tomor2.strftime("%a, %d %b %Y")), TEAM[str(LICHTRUC[2])])
    
        
    # Sends the response back to the channel
    botlog.debug("command: %s, channel: %s, text: %s" % (command, channel, response))
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response if response != None else default_response 
    )

def sendtoSlack(res, channel):
    for child in channel:
        # Sends the response back to the channel
        botlog.debug("channel: %s, text: %s" % (channel, res))
        slack_client.api_call(
            "chat.postMessage",
            channel=child,
            text=res
        )

def main():
    global starterbot_id
    global LICHTRUC
    global TODAY
    HAVESENT = False
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            if NOTIFY != []:
                today = datetime.now()
                tomorrow = today + timedelta(1)
                Dhour = str(today.strftime('%H'))
                # FullTime = str(today.strftime('%H:%M:%S'))
                NameDay = str(today.now().strftime('%a'))
                if NameDay in DAYWORK:
                    res = None
                    if HAVESENT == False:
                        if int(Dhour) >= int(HOURNOTIFY):
                            TODAY = LICHTRUC.pop(0)
                            LICHTRUC.append(TODAY)
                            if NameDay == FRIDAY:
                                tomorrow2 = today + timedelta(3)
                                res = "Lịch Monitor ngày thứ hai (%s) là (%s) ^^\nChúc mọi người cuối tuần vui nhé nhé :kissing_heart:" % (str(datetime.strftime(tomorrow2,'%Y-%m-%d')),TEAM[str(LICHTRUC[0])])
                                sendtoSlack(res, NOTIFY)
                                HAVESENT = True
                            else:
                                res = "Lịch Monitor ngày mai (%s) là (%s)\nHai cậu nhớ đi nhé ^^" % (str(datetime.strftime(tomorrow,'%Y-%m-%d')),TEAM[str(LICHTRUC[0])])
                                sendtoSlack(res, NOTIFY)
                                HAVESENT = True
                        else:
                            TODAY = LICHTRUC[0]
                            HAVESENT == False
                else:
                    TODAY = None
                    if HAVESENT == False:
                        if NameDay == SUNDAY:
                            if int(Dhour) >= 19:
                                res = "Tạm biệt cuối tuần, mình trở lại nhiệm vụ nhé\nLịch Monitor ngày mai (%s) là (%s) :joy:" % (str(datetime.strftime(tomorrow,'%Y-%m-%d')),TEAM[str(LICHTRUC[0])])
                                sendtoSlack(res, NOTIFY)
                                HAVESENT = True
                            else:
                                HAVESENT = False
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Slack Client')
    parser.add_argument('endday', type=str, help='endday')
    args = parser.parse_args()
    HOURNOTIFY = str(args.endday)
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        res = "Service altBot buộc Stop, User: (%s)!!!\n" % (str(os.environ.get('USER')))
        sendtoSlack(res, NOTIFY)
