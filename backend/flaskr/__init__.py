from multiprocessing import current_process
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        if len(categories) == 0:
           abort(404)

        return jsonify({
            'success': True,
            'categories': {category['id']:category['type'] for category in formatted_categories}
        })
   

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        
        categories = Category.query.all()

        formatted_questions = [question.format() for question in questions]
        formatted_categories = [category.format() for category in categories]

        if len(current_questions) == 0:
           abort(404)


        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': {category['id']:category['type'] for category in formatted_categories},
            'current_category': None,
            'total_questions': len(formatted_questions)
        })


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(400)

            question.delete()
            return jsonify({
                'success': True,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()
        try:
            newQuestion = Question(question=body['question'],answer=body['answer'],category=body['category'],difficulty=body['difficulty']
        )
            newQuestion.insert()

            return jsonify({
                'success': True,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        
        searchTerm = request.get_json()
        questions = Question.query.filter(Question.question.ilike("%"+searchTerm["searchTerm"]+"%")).all()

        if questions is None:
            abort(404)
        
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': None
        })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def search_category(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()

        if category is None:
            abort(404)
        
        if category is not None:
            questions = Question.query.filter_by(category=str(category_id)).all()

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })
            
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=['POST'])
    def quizzes():

        body = request.get_json()
        previous_questions = body.get('previous_questions')
        category = body.get('quiz_category')

        if category is None:
            abort(404)

        if previous_questions is None:
            abort(404)

        questions = None
        if (category['id'] == 0):
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(Question.id.notin_(previous_questions),Question.category == category['id']).all()


        total_questions = len(questions)
        
        if total_questions:
            question = random.choice(questions)
            return jsonify({'success': True, 'question': question.format()})


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}), 
            400,
        )
    
    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({
                "success": False, "error": 405, "message": "method not allowed"}),
            405,
        )


    return app

