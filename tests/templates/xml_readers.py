import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

current_dir = os.path.dirname(__file__)
templates_dir = os.path.join(current_dir, 'xml')

env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(['html', 'xml'])
)

def accept_invite(user: str, addressed_user: str) -> str:
    temp = env.get_template('accept_invite.xml')
    return temp.render({'username': user, 'addressed_username': addressed_user})

def current_user(user: str) -> str:
    temp = env.get_template('current_user.xml')
    return temp.render({'username': user})

def decline_invite(user: str, addressed_user: str) -> str:
    temp = env.get_template('decline_invite.xml')
    return temp.render({'username': user, 'addressed_username': addressed_user})

def remove_friend(user: str, addressed_user: str) -> str:
    temp = env.get_template('remove_friend.xml')
    return temp.render({'username': user, 'addressed_username': addressed_user})

def send_invite(user: str, addressed_user: str) -> str:
    temp = env.get_template('send_invite.xml')
    return temp.render({'username': user, 'addressed_username': addressed_user})
