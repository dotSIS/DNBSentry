# coding=utf-8
from fbchat import Client
from fbchat.models import *
import logging
import openai
import json

# openai account key
openai.api_key = open("key.txt", "r").read().strip("\n")

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logging.disable(logging.INFO)

# user and bot ids
aid = "000000000000000"# Bot FB ID HERE
zaid = "000000000000000"# Your FB ID HERE
admin_list = [zaid, aid]# Your FB ID AND Bot FB ID

# room threads
thread_id = "3221645394585786"# Messenger GC FB ID HERE
thread_type = ThreadType.GROUP
tid = thread_id
ttp = thread_type

# global modes
listenmode = True
gpt = False

message_history = []

def chatgpt(input, role="user"):
    message_history.append({"role": role, "content": input})
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = message_history
    )
    reply = completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply})
    return reply

# subclass a bot
class DNBSentry(Client):

    # onMessage function
    def onMessage(self, author_id, message_object, thread_id=tid, thread_type=ttp, **kwargs):

        global listenmode, gpt, tid
        
        message = message_object.text

        # if message came from 3r5
        if thread_id == tid:
            
            # if listen mode is on
            if listenmode == True:
                
                # if message came from gc and gpt is on
                if thread_id == tid and gpt == True and author_id != aid:
                    replygpt = chatgpt(message)
                    self.send(Message(text=replygpt), tid, ttp)
                    self.markAsDelivered(author_id, tid)
                    
                    # if message came from admin
                    if author_id == zaid:
                        if message == "-gpt off":
                            gpt = False
                            replygptoff = "ChatGPT deactivated🤖"
                            self.send(Message(text=replygptoff), tid, ttp)
                            self.markAsDelivered(author_id, tid)

                # if message came from gc and gpt is off
                elif thread_id == tid and gpt == False:
                    # spam commands
                    if message == "-gpt on":
                        gpt = True
                        replygpton = "ChatGPT activated🤖" + "\n" + "Ask anything!"
                        self.send(Message(text=replygpton), tid, ttp)
                        self.markAsDelivered(author_id, tid)
                    elif message == "-help":
                        with open('files/0-help.txt', mode='r', encoding='utf-8') as helpFile:
                            replyhelp = helpFile.read()
                            helpFile.close()
                            self.send(Message(text=replyhelp), tid, ttp)
                            self.markAsDelivered(author_id, tid)
                    elif message == "-version":
                        with open('files/0-version.txt', mode='r', encoding='utf-8') as versionFile:
                            replyversion = versionFile.read()
                            versionFile.close()
                            self.send(Message(text=replyversion), tid, ttp)
                            self.markAsDelivered(author_id, tid)

        else:
            # reply = ""
            noreplycount = 1
            noreply = "NO REPLY COUNT = "
            print(noreply + str(noreplycount))
            noreplycount = noreplycount + 1

# -----------------------------------------------------------------------
           
# initialize cookies
cookies = {}
try:
    # Load the session cookies
    with open('files/z-session.json', 'r') as f:
        cookies = json.load(f)
except FileNotFoundError:
    # If it fails, never mind, we'll just login again
    print('Can\'t load session.json.')

# connect bot
try:
    with open('files/z-facebook.json') as js:
        facebook = json.load(js)
except FileNotFoundError:
    with open('files/z-facebook.json', 'w') as js:
        facebook = {'email': input('Enter your email:'), 'password': input('Enter your password:')}
        json.dump(facebook, js)
        
client = DNBSentry(facebook['email'], facebook['password'], session_cookies=cookies)
with open('files/z-session.json', 'w') as file:
    json.dump(client.getSession(), file)
print('Logged in succesfully!')
client.listen()

# Save the session again
with open('files/z-session.json', 'w') as file:
    json.dump(client.getSession(), file)
