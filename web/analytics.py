import pandas as pd
import pymongo, os, random, datetime

# dbconfig
client = pymongo.MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.guestbook


def populate_mongodb(minutes_ago = 60):
    greetings = ['Hello', 'Hi', 'Salutations', 'Greetings']
    verbs = ['really like', 'absolutely adore', 'am OK with', 'enjoy']
    nouns = ['flask', 'pyMongo', 'API', 'upload', 'python script', 'list comprehension']
    users = ['wgleich', 'random_user1', 'known_user', 'power_user', 'test_user', 'helpful_admin', 'friendly_user',
             'Will']
    db.posts.insert_one({'author': random.choice(users),
                         'post': "{0}, I {1} your {2}.".format(random.choice(greetings), random.choice(verbs),
                                                               random.choice(nouns)),
                         'time': datetime.datetime.now() - datetime.timedelta(minutes =minutes_ago)})

def top_users_dataframe():
    posts = [item for item in db.posts.find()]
    df = pd.DataFrame(posts)
    return df['author'].value_counts().head().to_frame().transpose().to_html(index=False)

if __name__ == "__main__":
    # for i in range(25,0,-1):
    #     populate_mongodb(minutes_ago=i)