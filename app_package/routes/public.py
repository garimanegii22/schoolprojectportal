from flask import Blueprint, render_template, Response
from app_package.models import House, Competition, ParticipantRegistration, Result
from app_package import db
from datetime import datetime

public_bp = Blueprint('public_bp', __name__)

@public_bp.route('/')
def index():
    # Fetch all houses and sort them safely in Python by total_points property descending
    houses = House.query.all()
    houses.sort(key=lambda h: h.total_points or 0, reverse=True)
    
    # Safely fetch recent competitions ordered by ID descending
    try:
        recent_competitions = Competition.query.order_by(Competition.id.desc()).limit(5).all()
    except Exception:
        recent_competitions = Competition.query.limit(5).all()
        
    return render_template('public/index.html', houses=houses, recent_competitions=recent_competitions)

@public_bp.route('/export-podium-certificate')
def export_podium_certificate():
    houses = House.query.all()
    houses.sort(key=lambda h: h.total_points or 0, reverse=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"House_Championship_Standings_{timestamp}.html"

    # HTML Printable Certificate Format
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Official House Championship Results</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
        .cert-card {{ border: 3px solid #e2e8f0; border-radius: 20px; padding: 40px; max-width: 800px; margin: 0 auto; background: #1e293b; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        h1 {{ color: #fbbf24; font-size: 32px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 2px; }}
        h3 {{ color: #94a3b8; font-weight: 400; margin-top: 0; }}
        .standings-table {{ width: 100%; border-collapse: collapse; margin-top: 30px; text-align: left; }}
        .standings-table th {{ background: #334155; color: #f1f5f9; padding: 12px; border-bottom: 2px solid #475569; }}
        .standings-table td {{ padding: 14px; border-bottom: 1px solid #334155; font-size: 18px; }}
        .rank-1 {{ color: #fbbf24; font-weight: bold; font-size: 20px; }}
        .rank-2 {{ color: #cbd5e1; font-weight: bold; }}
        .rank-3 {{ color: #b45309; font-weight: bold; }}
        .footer {{ margin-top: 40px; font-size: 12px; color: #64748b; }}
    </style>
</head>
<body>
    <div class="cert-card">
        <h1>🏆 Inter-House Championship Standings</h1>
        <h3>Official Standings Certificate</h3>
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
        rank_class = f"rank-{idx}" if idx <= 3 else ""
        badge = "🥇 " if idx == 1 else ("🥈 " if idx == 2 else ("🥉 " if idx == 3 else f"#{idx} "))
        html_content += f"""
                <tr class="{rank_class}">
                    <td>{badge} Rank {idx}</td>
                    <td>{house.emoji if hasattr(house, 'emoji') else ''} {house.name} House</td>
                    <td>{house.total_points} pts</td>
                </tr>"""

    html_content += f"""
            </tbody>
        </table>
        <div class="footer">
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Official School Competition Portal
        </div>
    </div>
</body>
</html>"""

    response = Response(html_content, mimetype='text/html')
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response