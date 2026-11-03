from flask import Blueprint, render_template, jsonify, make_response
from app_package.models import House, Competition, Student, Result
import csv
import io

public_bp = Blueprint('public_bp', __name__)

@public_bp.route('/')
def index():
    houses = House.query.all()
    competitions = Competition.query.filter_by(is_archived=False).all()
    results = Result.query.order_by(Result.id.desc()).all()
    students = Student.query.all()
    
    # Sort houses by total points descending, then wins descending (tie-breaker)
    sorted_houses = sorted(houses, key=lambda h: (h.total_points, h.total_wins), reverse=True)
    
    return render_template('public/index.html', 
                           houses=sorted_houses, 
                           competitions=competitions, 
                           results=results, 
                           students=students)

@public_bp.route('/api/data')
def get_data():
    """API endpoint to fetch live portal state for dynamic frontend updates."""
    houses = House.query.all()
    competitions = Competition.query.filter_by(is_archived=False).all()
    results = Result.query.order_by(Result.id.desc()).all()
    students = Student.query.all()
    
    sorted_houses = sorted(houses, key=lambda h: (h.total_points, h.total_wins), reverse=True)
    
    houses_data = {}
    for h in sorted_houses:
        houses_data[h.name] = {
            "name": h.name,
            "emoji": h.emoji,
            "color": h.display_color,
            "border": h.border_class,
            "glow": h.glow_class,
            "points": h.total_points,
            "wins": h.total_wins
        }
        
    comps_data = [{"id": c.id, "name": c.name, "category": c.category, "date": c.event_date.strftime('%Y-%m-%d'), "maxPoints": c.max_points} for c in competitions]
    results_data = [{"competition": r.competition.name, "category": r.competition.category, "position": r.position, "house": r.house.name, "points": r.points_awarded} for r in results]
    students_data = [{"name": s.full_name, "roll": s.roll_number, "class": s.class_section, "house": s.house.name, "competitions": [reg.competition.name for reg in s.registrations]} for s in students]
    
    return jsonify({
        "houses": houses_data,
        "competitions": comps_data,
        "results": results_data,
        "students": students_data
    })

@public_bp.route('/export/csv')
def export_csv():
    """Exports current house standings as a downloadable CSV file."""
    houses = House.query.all()
    sorted_houses = sorted(houses, key=lambda h: (h.total_points, h.total_wins), reverse=True)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'House', 'Points', 'Wins'])
    
    for idx, h in enumerate(sorted_houses, 1):
        writer.writerow([idx, h.name, h.total_points, h.total_wins])
        
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=school_house_standings.csv"
    response.headers["Content-Type"] = "text/csv"
    return response