import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_account = 'postgres'
        self.database_password = 'sandraemma'
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.database_account, self.database_password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
    
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # Delete a different question in each attempt
    def test_delete_question(self):
        res = self.client().delete("/questions/2")
        data = json.loads(res.data)

        # question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        # self.assertEqual(data["deleted"], 2)
        # self.assertTrue(data["total_questions"])
        # self.assertTrue(len(data["questions"]))
        # self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        res = self.client().post("/search", json=({'searchTerm': 'new'}))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)


    def test_quizzes(self):
        res = self.client().post("/quizzes", 
                json=({
                        'previous_questions': [],
                        'quiz_category': 
                            {'id':'1', 'type':'Sports'}
                    }))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_search_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data["current_category"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()