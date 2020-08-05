from datetime import datetime

from nottingtable import db


class Course(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    activity = db.Column(db.String(256), nullable=False)
    module = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    start = db.Column(db.String(10), nullable=False)
    end = db.Column(db.String(10), nullable=False)
    duration = db.Column(db.String(10), nullable=False)
    room = db.Column(db.String(100), nullable=True)
    staff = db.Column(db.String(256), nullable=True)
    weeks = db.Column(db.String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'Activity': self.activity,
            'Module': self.module,
            'Type': self.type,
            'Day': self.day,
            'Start': self.start,
            'End': self.end,
            'Duration': self.duration,
            'Room': self.room,
            'Staff': self.staff,
            'Weeks': self.weeks
        }

    def __repr__(self):
        return '<Course %r>' % self.activity


class Department(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    department_id = db.Column(db.String(20), nullable=False)
    department_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Department %r>' % self.department_name


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    timetable = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.student_id


class MasterPlan(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    plan_id = db.Column(db.String(50), unique=True, nullable=False)
    plan_name = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return '<MPlan %r>' % self.plan_id
