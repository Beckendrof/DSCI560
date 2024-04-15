css = '''
<style>

#chat-with-ai {
    position: fixed;
    top: 5%;
}

.stTextInput {
    position: fixed;
    bottom: 5%;
    width: 50%;
    padding-right: 8%;
    z-index: 999;
}

.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.chat-message.user {
    background-color: #2b313e;
}

.chat-message.bot {
    background-color: #475063;
}

.chat-message .message {
    color: #fff;
    max-width: 80%;
}

</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>
'''
