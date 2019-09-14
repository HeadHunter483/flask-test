from datetime import datetime, timedelta
import unittest

from flask_testing import TestCase

from app import app, db
from app.models import User, Post


class UserModelCase(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='test')
        u.set_password('testcat')
        self.assertFalse(u.check_password('testdog'))
        self.assertTrue(u.check_password('testcat'))

    def test_avatar(self):
        u = User(username='testagain', email='upwkacml@gmail.com')
        self.assertEqual(u.avatar(64), ('https://www.gravatar.com/avatar/'
                                        '8ec93fcea862520b8d4f50a4abc4eb2e'
                                        '?d=identicon&s=64'))

    def test_follow(self):
        u1 = User(username='test1', email='test1@example.com')
        u2 = User(username='test2', email='test2@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'test2')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'test1')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # creating test users
        u1 = User(username='test1', email='test1@example.com')
        u2 = User(username='test2', email='test2@example.com')
        u3 = User(username='test3', email='test3@example.com')
        u4 = User(username='test4', email='test4@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # creating test posts
        now = datetime.utcnow()
        p1 = Post(body="post from test1", author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body="post from test2", author=u2,
                  timestamp=now + timedelta(seconds=2))
        p3 = Post(body="post from test3", author=u3,
                  timestamp=now + timedelta(seconds=3))
        p4 = Post(body="post from test4", author=u4,
                  timestamp=now + timedelta(seconds=4))

        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup followers
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        # check followed posts for each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p4, p2, p1])
        self.assertEqual(f2, [p3, p2])
        self.assertEqual(f3, [p4, p3])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
