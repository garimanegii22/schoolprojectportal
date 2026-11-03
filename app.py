from app_package import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    from app_package.models import Admin, House, Student, Competition, ParticipantRegistration, Result
    return {
        'db': db,
        'Admin': Admin,
        'House': House,
        'Student': Student,
        'Competition': Competition,
        'ParticipantRegistration': ParticipantRegistration,
        'Result': Result
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)