from flask import  Flask, request, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy
import json
from mail_sender_utils import MailSender

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ctf_submissions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.cli.command("create-db")
def create_db():
    """Creates the database."""
    with app.app_context():
        db.create_all()
    print("Database created!")

def make_json_response(data, status_code=200):
    return Response(response=json.dumps(data), status=status_code)

def success_dict(status="success", data=None):
    return  {"status": status } if data is None else  {"status": status, "data":data }

def error_dict(err_desc):
    return {"status": "error", "error_description": err_desc}

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, nullable=False)
    contest_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    submission_datetime = db.Column(db.DateTime, nullable=False)
    submitted_flag = db.Column(db.String(255), nullable=False)
    solved = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "type": "Submission",
            "id": self.id,
            "challenge_id": self.challenge_id,
            "contest_id": self.contest_id,
            "user_id": self.user_id,
            "submission_datetime": self.submission_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "submitted_flag": self.submitted_flag,
            "solved": self.solved
        }

@app.route("/submissions", methods=["POST"])
def create_submission():
    data = request.get_json()
    challenge_id = int(data["challenge_id"])
    contest_id = int(data["contest_id"])
    user_id = int(data["user_id"])
    email = data["user_email"]
    
    if "submission_datetime" in data: 
        submission_datetime = datetime.strptime(data["submission_datetime"], "%Y-%m-%d %H:%M:%S")
    else:
        submission_datetime = datetime.now()
    
    submitted_flag = data["submitted_flag"]
    solved = data["solved"]
    submission = Submission(challenge_id=challenge_id, contest_id=contest_id, user_id=user_id, 
                            submission_datetime=submission_datetime, submitted_flag=submitted_flag, solved=bool(solved))
    db.session.add(submission)
    db.session.commit()
    if solved:
        mailSender=MailSender()
        mailSender.user_notification(email=email)
    print(submission.to_dict())
    resp_dict = success_dict("created", data={"count":1, "objects":[submission.to_dict()]})
    return make_json_response(resp_dict, 201)

@app.route("/submissions", methods=["GET"])
def get_submissions():
    chal_id = request.args.get("challenge_id")
    cont_id = request.args.get("contest_id")
    user_id = request.args.get("user_id")
    solved = request.args.get("solved")
    query = Submission.query
    if chal_id is not None:
        query = query.filter_by(challenge_id=chal_id)
    if cont_id is not None:
        query = query.filter_by(contest_id=cont_id)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    if solved is not None:
        query = query.filter_by(solved=bool(solved))

    submissions = query.all()
    resp_dict = success_dict("ok", data={"count": len(submissions), "objects": [sub.to_dict() for sub in submissions]})
    return make_json_response(resp_dict, 200)

@app.route("/submissions/getbyuseridandcontestid/<int:user_id>/<int:contest_id>", methods=["GET"])
def get_submissions_by_user_id_and_contest_id(user_id, contest_id):
    submissions=Submission.query.filter_by(user_id=user_id, contest_id=contest_id).all()
    resp_dict = success_dict(data={"count":len(submissions), "objects":
                    [submission.to_dict() for submission in submissions]})
    return make_json_response(resp_dict)

if __name__=="__main__":
    app.run(debug=True, port=8083)