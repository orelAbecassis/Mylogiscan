from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Intervention, Service, Client
from app.extensions import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.dashboard_admin'))
        elif current_user.role == 'client':
            return redirect(url_for('main.dashboard_client'))
        else:
            return redirect(url_for('main.dashboard_intervenant'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard/intervenant')
@login_required
def dashboard_intervenant():
    if current_user.role != 'intervenant':
        return redirect(url_for('main.index'))
    
    # Fetch assigned clients
    clients = current_user.clients
    
    # Fetch interventions
    now = datetime.now()
    all_interventions = current_user.interventions.order_by(Intervention.start_time.desc()).all()
    
    upcoming_interventions = [i for i in all_interventions if i.start_time >= now]
    past_interventions = [i for i in all_interventions if i.start_time < now]
    
    return render_template('dashboard_intervenant.html', 
                           clients=clients,
                           upcoming=upcoming_interventions,
                           history=past_interventions)

@main.route('/schedule_intervention', methods=['POST'])
@login_required
def schedule_intervention():
    if current_user.role != 'intervenant':
        return redirect(url_for('main.index'))
    
    client_id = request.form.get('client_id')
    service_id = request.form.get('service_id')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    
    if client_id and service_id and date_str and time_str:
        start_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        
        intervention = Intervention(
            client_id=int(client_id),
            service_id=int(service_id),
            intervenant_id=current_user.id,
            start_time=start_datetime,
            status='Scheduled'
        )
        db.session.add(intervention)
        db.session.commit()
        flash('Intervention programmée avec succès', 'success')
    else:
        flash('Veuillez remplir tous les champs', 'warning')
        
    return redirect(url_for('main.dashboard_intervenant'))

@main.route('/request_delete_intervention/<int:intervention_id>', methods=['POST'])
@login_required
def request_delete_intervention(intervention_id):
    if current_user.role != 'intervenant':
        return redirect(url_for('main.index'))
        
    intervention = Intervention.query.get_or_404(intervention_id)
    if intervention.intervenant_id != current_user.id:
        return redirect(url_for('main.dashboard_intervenant'))
        
    reason = request.form.get('reason')
    if reason:
        intervention.status = 'DeletionRequested'
        intervention.cancellation_reason = reason
        db.session.commit()
        flash('Demande de suppression envoyée à l\'administrateur', 'info')
    else:
        flash('Motif requis pour la suppression', 'warning')
        
    return redirect(url_for('main.dashboard_intervenant'))

@main.route('/scan_qr', methods=['POST'])
@login_required
def scan_qr():
    # Simulation of QR scan action - In a real app this would process QR data
    # For this prototype, the big button triggers a start/stop of service
    
    # Logic: If last intervention is open -> Close it. Else -> Open new one.
    last_intervention = Intervention.query.filter_by(intervenant_id=current_user.id).order_by(Intervention.start_time.desc()).first()
    
    if last_intervention and last_intervention.end_time is None:
        # Close session
        last_intervention.end_time = datetime.utcnow()
        last_intervention.status = 'Completed'
        db.session.commit()
        flash('Service Terminé', 'success')
    else:
        # Start new session (Mock data for Service/Client since scanned QR would provide this)
        # Using placeholder ID 1 for demonstration if not exists
        # In real app, scan would match a scheduled intervention or create new
        intervention = Intervention(
            intervenant_id=current_user.id, 
            service_id=1, 
            client_id=1, 
            start_time=datetime.utcnow(),
            status='InProgress'
        )
        db.session.add(intervention)
        db.session.commit()
        flash('Service Commencé', 'success')
        
    return redirect(url_for('main.dashboard_intervenant'))


@main.route('/dashboard/client')
@login_required
def dashboard_client():
    if current_user.role != 'client':
        return redirect(url_for('main.index'))
    # Assuming the current user IS the client or linked to a client
    # For simplicity, finding Client entry linked to this User
    client_entry = Client.query.filter_by(user_id=current_user.id).first()
    history = []
    if client_entry:
        history = Intervention.query.filter_by(client_id=client_entry.id).order_by(Intervention.start_time.desc()).all()
    
    return render_template('dashboard_client.html', history=history)

@main.route('/dashboard/admin')
@login_required
def dashboard_admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    interventions = Intervention.query.order_by(Intervention.start_time.desc()).all()
    intervenants = User.query.filter_by(role='intervenant').all()
    clients = Client.query.all()
    services = Service.query.all()
    
    return render_template('dashboard_admin.html', 
                           interventions=interventions,
                           intervenants=intervenants,
                           clients=clients,
                           services=services)

@main.route('/admin/add_intervenant', methods=['GET', 'POST'])
@login_required
def add_intervenant():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Get selected services and clients from form (list of IDs)
        selected_service_ids = request.form.getlist('services')
        selected_client_ids = request.form.getlist('clients')
        
        user = User(username=username, role='intervenant')
        user.set_password(password)
        
        # Add relationships
        if selected_service_ids:
            for s_id in selected_service_ids:
                service = Service.query.get(int(s_id))
                if service:
                    user.services.append(service)
                    
        if selected_client_ids:
            for c_id in selected_client_ids:
                client = Client.query.get(int(c_id))
                if client:
                    user.clients.append(client)
        
        db.session.add(user)
        try:
            db.session.commit()
            flash('Intervenant créé avec succès', 'success')
            return redirect(url_for('main.dashboard_admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
            
    available_services = Service.query.all()
    available_clients = Client.query.all()
    return render_template('admin_add_intervenant.html', services=available_services, clients=available_clients)

@main.route('/admin/edit_intervenant/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_intervenant(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if user.role != 'intervenant':
        flash('Cet utilisateur n\'est pas un intervenant.', 'warning')
        return redirect(url_for('main.dashboard_admin'))
        
    if request.method == 'POST':
        # Update basic info
        username = request.form.get('username')
        user.username = username
        
        # Update Password only if provided
        password = request.form.get('password')
        if password:
            user.set_password(password)
            
        # Update Services
        selected_service_ids = request.form.getlist('services')
        user.services = [] # Clear existing
        for s_id in selected_service_ids:
            service = Service.query.get(int(s_id))
            if service:
                user.services.append(service)
                
        # Update Clients
        selected_client_ids = request.form.getlist('clients')
        user.clients = [] # Clear existing
        for c_id in selected_client_ids:
            client = Client.query.get(int(c_id))
            if client:
                user.clients.append(client)
                
        try:
            db.session.commit()
            flash('Intervenant mis à jour avec succès', 'success')
            return redirect(url_for('main.dashboard_admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
            
    available_services = Service.query.all()
    available_clients = Client.query.all()
    return render_template('admin_edit_intervenant.html', user=user, services=available_services, clients=available_clients)

@main.route('/admin/client/<int:client_id>')
@login_required
def client_details(client_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    client = Client.query.get_or_404(client_id)
    # Fetch interventions for this client
    interventions = client.interventions.order_by(Intervention.start_time.desc()).all()
    
    interventions = client.interventions.order_by(Intervention.start_time.desc()).all()
    
    return render_template('admin_client_details.html', client=client, interventions=interventions)

@main.route('/admin/intervenant/<int:user_id>')
@login_required
def intervenant_details(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if user.role != 'intervenant':
        return redirect(url_for('main.dashboard_admin'))
        
    # Fetch interventions for this intervenant
    interventions = user.interventions.order_by(Intervention.start_time.desc()).all()
    
    return render_template('admin_intervenant_details.html', user=user, interventions=interventions)

@main.route('/admin/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Create User account for client
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Create Client Profile details
        name = request.form.get('name')
        address = request.form.get('address')
        
        user = User(username=username, role='client')
        user.set_password(password)
        db.session.add(user)
        
        try:
            db.session.commit() # Commit user first to get ID
            
            client = Client(name=name, address=address, user_id=user.id)
            db.session.add(client)
            db.session.commit()
            
            flash('Client créé avec succès', 'success')
            return redirect(url_for('main.dashboard_admin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'danger')
            
    return render_template('admin_add_client.html')
    return render_template('admin_add_client.html')

@main.route('/admin/delete_intervention/<int:intervention_id>', methods=['POST'])
@login_required
def delete_intervention(intervention_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
        
    intervention = Intervention.query.get_or_404(intervention_id)
    
    # Check if it was a request or just admin deleting
    action = request.form.get('action') # 'approve' or 'reject'
    
    if action == 'approve':
        db.session.delete(intervention)
        db.session.commit()
        flash('Intervention supprimée avec succès', 'success')
    elif action == 'reject':
        intervention.status = 'Scheduled' # Revert to scheduled
        intervention.cancellation_reason = None
        db.session.commit()
        flash('Demande de suppression rejetée', 'info')
        
    return redirect(url_for('main.dashboard_admin'))

@main.route('/admin/schedule_intervention', methods=['POST'])
@login_required
def admin_schedule_intervention():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    intervenant_id = request.form.get('intervenant_id')
    client_id = request.form.get('client_id')
    service_id = request.form.get('service_id')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    
    if intervenant_id and client_id and service_id and date_str and time_str:
        try:
            start_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            
            intervention = Intervention(
                client_id=int(client_id),
                service_id=int(service_id),
                intervenant_id=int(intervenant_id),
                start_time=start_datetime,
                status='Scheduled'
            )
            db.session.add(intervention)
            db.session.commit()
            flash('Intervention programmée avec succès', 'success')
        except ValueError:
             flash('Format de date invalide', 'danger')
        except Exception as e:
             db.session.rollback()
             flash(f'Erreur: {str(e)}', 'danger')
    else:
        flash('Veuillez remplir tous les champs', 'warning')
        
    return redirect(url_for('main.dashboard_admin'))
