from app import create_app, db
from app.models import User, Service, Client, Intervention

app = create_app()

with app.app_context():
    db.create_all()

    # Create Services
    menage = Service(name='Ménage')
    baby_sitting = Service(name='Baby-sitting')
    jardinage = Service(name='Jardinage')
    db.session.add_all([menage, baby_sitting, jardinage])
    db.session.commit()

    # Create Users
    admin = User(username='admin', role='admin')
    admin.set_password('admin')
    
    intervenant1 = User(username='orel', role='intervenant')
    intervenant1.set_password('orel')
    intervenant1.services.append(menage)
    intervenant1.services.append(jardinage)
    # Note: client_profile needs to be created before assigning to intervenant1 if we append objects
    
    client_user = User(username='user', role='client')
    client_user.set_password('user')
    
    db.session.add_all([admin, intervenant1, client_user])
    db.session.commit()

    # Create Client Profile FIRST so we can assign it
    client_profile = Client(name='Famille Dupont', address='123 Rue de la Paix', user_id=client_user.id)
    db.session.add(client_profile)
    # Commit to get ID
    db.session.commit() 
    
    # Now assign client to intervenant
    intervenant1.clients.append(client_profile)
    db.session.commit()

    print("Database initialized and seeded successfully.")
