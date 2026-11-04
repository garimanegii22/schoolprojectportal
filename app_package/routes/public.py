from flask import Blueprint, render_template, Response
from app_package.models import House, Competition, ParticipantRegistration, Result
from app_package import db
from datetime import datetime

public_bp = Blueprint('public_bp', __name__)

@public_bp.route('/')
def index():
    houses = House.query.all()
    houses.sort(key=lambda h: h.total_points or 0, reverse=True)
    
    total_points_awarded = sum(h.total_points for h in houses) or 1
    total_events_count = Competition.query.count()
    leading_house = houses[0] if houses else None

    # Calculate share percentages for point distribution chart
    house_shares = []
    for h in houses:
        pts = h.total_points or 0
        percentage = round((pts / total_points_awarded) * 100, 1) if total_points_awarded > 0 else 0
        house_shares.append({
            'name': h.name,
            'points': pts,
            'percentage': percentage
        })

    try:
        recent_competitions = Competition.query.order_by(Competition.id.desc()).limit(6).all()
    except Exception:
        recent_competitions = Competition.query.limit(6).all()
        
    return render_template(
        'public/index.html', 
        houses=houses, 
        recent_competitions=recent_competitions,
        total_points_awarded=total_points_awarded,
        total_events_count=total_events_count,
        leading_house=leading_house,
        house_shares=house_shares
    )

@public_bp.route('/export-csv')
def export_csv():
    houses = House.query.all()
    houses.sort(key=lambda h: h.total_points or 0, reverse=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"School_House_Championship_Report_{timestamp}.html"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Official House Championship Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .cert-card {{ border: 2px solid #334155; border-radius: 16px; padding: 40px; max-width: 800px; margin: 0 auto; background: #1e293b; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; font-size: 28px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }}
        h3 {{ color: #94a3b8; font-weight: 400; margin-top: 0; }}
        .standings-table {{ width: 100%; border-collapse: collapse; margin-top: 30px; text-align: left; }}
        .standings-table th {{ background: #334155; color: #f1f5f9; padding: 12px; border-bottom: 2px solid #475569; }}
        .standings-table td {{ padding: 14px; border-bottom: 1px solid #334155; font-size: 16px; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #64748b; }}
    </style>
</head>
<body>
    <div class="cert-card">
        <h1>Inter-House Championship Report</h1>
        <h3>Official Standings & Score Summary</h3>
        <hr style="border-color: #334155; margin: 20px 0;">
        <table class="standings-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>House Name</th>
                    <th>Total Points</th>
                </tr>
            </thead>
            <tbody>
"""
    for idx, house in enumerate(houses, start=1):
        badge = "🥇 " if idx == 1 else ("🥈 " if idx == 2 else ("🥉 " if idx == 3 else f"#{idx} "))
        html_content += f"""
                <tr>
                    <td>{badge} Rank {idx}</td>
                    <td>{house.name} House</td>
                    <td>{house.total_points} pts</td>
                </tr>"""

    html_content += f"""
            </tbody>
        </table>
        <div class="footer">
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Official School Championship Portal
        </div>
    </div>
</body>
</html>"""

    response = Response(html_content, mimetype='text/html')
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response