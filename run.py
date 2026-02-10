from app import create_app, db
from app.models import User, Service, Client, Intervention

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Service': Service, 'Client': Client, 'Intervention': Intervention}

if __name__ == '__main__':
    app.run(debug=True)
