from app import application
from app import database
from flask import request
from flask import jsonify
from models import User
from models import Chat
from models import Message


# нужен полный рефакторинг под REST


def construct_responce(reason, **additional): # переделать в декоратор для обработки json
    pass


@application.route('/')
def index():
    return jsonify({'status': '1',
                    'reason': 'api is active'})


@application.route('/register', methods=['GET', 'POST'])
def register():
    json_request = request.json # нужно проверить метод запроса и его тело
    new_user = User(username=json_request['username'],
                    password=json_request['password'],
                    slug=json_request['username']) # проверить регистрацию # проверить правильность заполнения формы
    database.session.add(new_user) # убедиться, что база работает
    database.session.commit()
    return jsonify({'status': '1',
                    'reason': 'successful register'})


@application.route('/login', methods=['GET', 'POST'])
def login():
    json_request = request.json # нужно проверить метод запроса и его тело

    recieved_user = User.query.filter(User.username == json_request['username']).first() # может быть 2 пользователя с одним именем # пользователь может не существовать
    if (recieved_user.password != json_request['password']):
        return jsonify({'status': '0',
                        'reason': 'invalid password'})

    return jsonify({'status': '1',
                    'reason': 'successful login'})


@application.route('/chat')
def chatlist():
    all_chats = Chat.query.all() # нет проверки валидации
    chat_slugs = []
    for n in all_chats:
        chat_slugs.append(n.slug)

    return jsonify({'status': '1',
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs})


@application.route('/chat/<slug>', methods=['GET', 'POST'])
def chat(slug):
    json_request = request.json # нужно проверить метод запроса и его тело
    if (json_request['action'] == 'read'):
        last_messages = Message.query.order_by(Message.id.desc()).count(json_request['value'])
        last_messages_content = []
        for n in last_messages:
            last_messages_content.append(n.content)

        return jsonify({'status': '1',
                        'reason': 'returned messages',
                        'last_messages': last_messages_content})

    if (json_request['action'] == 'send'):
        current_chat = Chat.query.filter(Chat.slug == slug).first()
        new_message = Message(content=json_request['value'], chat=current_chat.id, author=1)
        database.session.add(new_message)
        database.session.commit()

        return jsonify({'status': '1',
                        'reason': 'sended message to server'})

    return jsonify({'status': '0',
                    'reason': 'no action given'})

# настройки чата
# форма создания нового чата
@application.errorhandler(404)
def page_not_found(e):
    return ''.join(['Страница не найдена. Убедитесь, что:\n',
                    '1. Это не прикол\n',
                    '2. Адрес написан правильно\n',
                    '3. Если вы перешли сюда по гиперссылке, дайте по башке\n',
                    ' тому, кто её сделал']), 404


@application.errorhandler(400)
def bad_request(e):
    return 'Возникла ошибка запроса со стороны клиента. Обратитесь к тому, кто такое посмел допустить. Если вы не уверены, кто это может быть, обратитесь к администрации WinSy c настолько подробным описанием проблемы, насколько вы можете себе позволить', 400


if __name__ == '__main__':
    application.run()
