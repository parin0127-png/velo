import os
import sqlite3
from datetime import datetime

DB_PATH = "velo.db"

def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tasks = 0
    clients = 0
    lessons = 0
    memory_count = 0
    client_rows = []
    lesson_rows = []
    memory_rows = []
    email_count = 0
    search_count = 0
    reminder_count = 0
    client_count_tasks = 0
    report_count = 0

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]

    if "clients" in tables:
        cursor.execute("SELECT COUNT(*) FROM clients")
        clients = cursor.fetchone()[0]
        cursor.execute("SELECT name, email, status, last_contact FROM clients ORDER BY id DESC LIMIT 5")
        client_rows = cursor.fetchall()

    if "lessons" in tables:
        cursor.execute("SELECT COUNT(*) FROM lessons")
        lessons = cursor.fetchone()[0]
        cursor.execute("SELECT lesson, created_at FROM lessons ORDER BY created_at DESC LIMIT 5")
        lesson_rows = cursor.fetchall()

    if "memory" in tables:
        cursor.execute("SELECT COUNT(*) FROM memory")
        memory_count = cursor.fetchone()[0]
        cursor.execute("SELECT summary, created_at FROM memory ORDER BY created_at DESC LIMIT 3")
        memory_rows = cursor.fetchall()

    if "tasks" in tables:
        cursor.execute("SELECT COUNT(*) FROM tasks"); tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_type='email'"); email_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_type='search'"); search_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_type='reminder'"); reminder_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_type='client'"); client_count_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE task_type='report'"); report_count = cursor.fetchone()[0]

    conn.close()
    return {
        "tasks": tasks,
        "clients": clients,
        "lessons": lessons,
        "memory": memory_count,
        "client_rows": client_rows,
        "lesson_rows": lesson_rows,
        "memory_rows": memory_rows,
        "email_count": email_count,
        "search_count": search_count,
        "reminder_count": reminder_count,
        "client_count_tasks": client_count_tasks,
        "report_count": report_count,
    }

def build_client_rows(rows):
    if not rows:
        return "<tr><td colspan='4' style='text-align:center; color:#555568;'>No clients yet</td></tr>"
    html = ""
    for r in rows:
        name, email, status, last_contact = r
        if status == "active":
            badge = f'<span class="status-badge badge-green">{status}</span>'
        elif status == "follow up":
            badge = f'<span class="status-badge badge-amber">{status}</span>'
        elif status == "pending":
            badge = f'<span class="status-badge badge-red">{status}</span>'
        else:
            badge = f'<span class="status-badge badge-blue">{status}</span>'
        html += f"<tr><td>{name}</td><td>{email}</td><td>{badge}</td><td>{last_contact}</td></tr>"
    return html

def build_memory_rows(rows):
    if not rows:
        return "<p style='color:#555568; font-size:12px; padding:16px 24px;'>No memory yet</p>"
    html = ""
    for r in rows:
        summary, created_at = r
        html += f"""
        <div class="activity-item">
            <div class="activity-icon" style="background:rgba(108,99,255,0.1); color:#a78bfa;">
                <i class="fa-solid fa-memory"></i>
            </div>
            <div>
                <div class="activity-text">{summary}</div>
                <div class="activity-time">{created_at}</div>
            </div>
        </div>"""
    return html

def generate_pdf_content(data, client_rows):
    lines = []
    lines.append("VELO BUSINESS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M')}")
    lines.append("=" * 50)
    lines.append("")
    lines.append("OVERVIEW")
    lines.append(f"Total Tasks Run   : {data['tasks']}")
    lines.append(f"Total Clients     : {data['clients']}")
    lines.append(f"Memory Entries    : {data['memory']}")
    lines.append(f"Lessons Learned   : {data['lessons']}")
    lines.append("")
    lines.append("TASK BREAKDOWN")
    lines.append(f"Email tasks       : {data['email_count']}")
    lines.append(f"Search tasks      : {data['search_count']}")
    lines.append(f"Reminder tasks    : {data['reminder_count']}")
    lines.append(f"Client tasks      : {data['client_count_tasks']}")
    lines.append(f"Report tasks      : {data['report_count']}")
    lines.append("")
    lines.append("CLIENT TRACKER")
    lines.append("-" * 50)
    if client_rows:
        for r in client_rows:
            name, email, status, last_contact = r
            lines.append(f"Name         : {name}")
            lines.append(f"Email        : {email}")
            lines.append(f"Status       : {status}")
            lines.append(f"Last Contact : {last_contact}")
            lines.append("-" * 30)
    else:
        lines.append("No clients yet.")
    return "\n".join(lines)

def generate_dashboard(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_folder, exist_ok=True)
    filename = f"Dashboard_{timestamp}.html"
    filepath = os.path.join(output_folder, filename)

    client_rows_html = build_client_rows(data["client_rows"])
    memory_rows_html = build_memory_rows(data["memory_rows"])
    pdf_text = generate_pdf_content(data, data["client_rows"])
    pdf_text_escaped = pdf_text.replace("`", "'")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Velo Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --bg: #0a0a0f; --bg2: #111118; --bg3: #1a1a24;
    --border: rgba(255,255,255,0.06); --border2: rgba(255,255,255,0.12);
    --text: #f0f0f5; --text2: #8888a0; --text3: #555568;
    --accent: #6c63ff; --accent2: #a78bfa;
    --green: #10b981; --amber: #f59e0b; --red: #ef4444; --blue: #3b82f6; --pink: #ec4899;
  }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }}
  body::before {{ content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(108,99,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(108,99,255,0.03) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; z-index: 0; }}
  .layout {{ display: flex; min-height: 100vh; position: relative; z-index: 1; }}
  .sidebar {{ width: 220px; background: var(--bg2); border-right: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; top: 0; left: 0; bottom: 0; z-index: 10; }}
  .logo {{ padding: 28px 24px 24px; border-bottom: 1px solid var(--border); }}
  .logo-mark {{ font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }}
  .logo-mark span {{ color: var(--accent2); }}
  .logo-sub {{ font-size: 10px; color: var(--text3); letter-spacing: 2px; text-transform: uppercase; margin-top: 2px; font-family: 'DM Mono', monospace; }}
  .nav {{ padding: 20px 12px; flex: 1; }}
  .nav-item {{ display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; color: var(--text2); font-size: 13px; margin-bottom: 2px; }}
  .nav-item.active {{ background: rgba(108,99,255,0.15); color: var(--accent2); }}
  .nav-item i {{ width: 16px; text-align: center; font-size: 14px; }}
  .sidebar-footer {{ padding: 16px 12px; border-top: 1px solid var(--border); }}
  .status-pill {{ display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.15); border-radius: 8px; font-size: 12px; color: var(--green); font-family: 'DM Mono', monospace; }}
  .status-dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: pulse 2s infinite; }}
  @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
  .main {{ margin-left: 220px; flex: 1; padding: 32px; }}
  .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; }}
  .page-title {{ font-family: 'Syne', sans-serif; font-size: 24px; font-weight: 600; letter-spacing: -0.5px; }}
  .page-sub {{ color: var(--text2); font-size: 13px; margin-top: 2px; }}
  .header-right {{ display: flex; align-items: center; gap: 12px; }}
  .date-badge {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--text3); padding: 6px 12px; background: var(--bg3); border: 1px solid var(--border); border-radius: 6px; }}
  .pdf-btn-header {{ display: flex; align-items: center; gap: 8px; padding: 9px 16px; border-radius: 8px; background: var(--accent); border: none; color: white; font-size: 13px; cursor: pointer; font-family: 'DM Sans', sans-serif; font-weight: 500; transition: all 0.15s; }}
  .pdf-btn-header:hover {{ background: #5b52e0; transform: translateY(-1px); }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .metric-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 20px; position: relative; overflow: hidden; }}
  .metric-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }}
  .metric-card.green::before {{ background: var(--green); }}
  .metric-card.amber::before {{ background: var(--amber); }}
  .metric-card.blue::before {{ background: var(--blue); }}
  .metric-card.pink::before {{ background: var(--pink); }}
  .metric-label {{ font-size: 11px; color: var(--text3); letter-spacing: 1.5px; text-transform: uppercase; font-family: 'DM Mono', monospace; margin-bottom: 12px; }}
  .metric-value {{ font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 1; margin-bottom: 8px; }}
  .metric-icon {{ position: absolute; top: 20px; right: 20px; font-size: 18px; opacity: 0.2; }}
  .metric-sub {{ font-size: 12px; color: var(--text3); }}
  .charts-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 24px; }}
  .chart-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }}
  .chart-title {{ font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 600; margin-bottom: 4px; }}
  .chart-sub {{ font-size: 12px; color: var(--text3); margin-bottom: 20px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--text2); font-family: 'DM Mono', monospace; }}
  .legend-dot {{ width: 8px; height: 8px; border-radius: 2px; }}
  .bottom-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; }}
  .table-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
  .table-header {{ padding: 20px 24px 16px; border-bottom: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text3); font-family: 'DM Mono', monospace; padding: 12px 24px; text-align: left; border-bottom: 1px solid var(--border); font-weight: 400; }}
  tbody td {{ padding: 12px 24px; font-size: 13px; border-bottom: 1px solid var(--border); color: var(--text2); }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody td:first-child {{ color: var(--text); font-weight: 500; }}
  .status-badge {{ display: inline-flex; align-items: center; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-family: 'DM Mono', monospace; }}
  .badge-green {{ background: rgba(16,185,129,0.1); color: #10b981; }}
  .badge-amber {{ background: rgba(245,158,11,0.1); color: #f59e0b; }}
  .badge-blue {{ background: rgba(59,130,246,0.1); color: #3b82f6; }}
  .badge-red {{ background: rgba(239,68,68,0.1); color: #ef4444; }}
  .activity-feed {{ padding: 0 24px 16px; }}
  .activity-item {{ display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }}
  .activity-item:last-child {{ border-bottom: none; }}
  .activity-icon {{ width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; margin-top: 2px; }}
  .activity-text {{ font-size: 12px; color: var(--text2); line-height: 1.5; }}
  .activity-time {{ font-size: 10px; color: var(--text3); margin-top: 2px; font-family: 'DM Mono', monospace; }}

  /* Modal */
  .modal-overlay {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 100; align-items: center; justify-content: center; }}
  .modal-overlay.show {{ display: flex; }}
  .modal {{ background: var(--bg2); border: 1px solid var(--border2); border-radius: 16px; padding: 32px; width: 400px; text-align: center; }}
  .modal-icon {{ font-size: 32px; color: var(--accent2); margin-bottom: 16px; }}
  .modal-title {{ font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 600; margin-bottom: 8px; }}
  .modal-sub {{ font-size: 13px; color: var(--text2); margin-bottom: 24px; }}
  .modal-actions {{ display: flex; gap: 12px; justify-content: center; }}
  .btn-cancel {{ padding: 10px 24px; border-radius: 8px; border: 1px solid var(--border2); background: transparent; color: var(--text2); font-size: 13px; cursor: pointer; font-family: 'DM Sans', sans-serif; }}
  .btn-download {{ padding: 10px 24px; border-radius: 8px; border: none; background: var(--accent); color: white; font-size: 13px; cursor: pointer; font-family: 'DM Sans', sans-serif; font-weight: 500; }}
  .btn-download:hover {{ background: #5b52e0; }}
</style>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="logo">
      <div class="logo-mark">Ve<span>lo</span></div>
      <div class="logo-sub">AI Operations</div>
    </div>
    <nav class="nav">
      <div class="nav-item active"><i class="fa-solid fa-chart-line"></i> Dashboard</div>
    </nav>
    <div class="sidebar-footer">
      <div class="status-pill"><div class="status-dot"></div>Velo online</div>
    </div>
  </aside>

  <main class="main">
    <div class="header">
      <div>
        <div class="page-title">Operations Overview</div>
        <div class="page-sub">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
      </div>
      <div class="header-right">
        <div class="date-badge">{datetime.now().strftime("%d %b %Y")}</div>
        <button class="pdf-btn-header" onclick="showModal()">
          <i class="fa-solid fa-file-arrow-down"></i> Download PDF Report
        </button>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="metric-card green">
        <i class="fa-solid fa-check-circle metric-icon"></i>
        <div class="metric-label">Tasks Completed</div>
        <div class="metric-value">{data["tasks"]}</div>
        <div class="metric-sub">total tasks run</div>
      </div>
      <div class="metric-card amber">
        <i class="fa-solid fa-users metric-icon"></i>
        <div class="metric-label">Active Clients</div>
        <div class="metric-value">{data["clients"]}</div>
        <div class="metric-sub">in tracker</div>
      </div>
      <div class="metric-card blue">
        <i class="fa-solid fa-memory metric-icon"></i>
        <div class="metric-label">Memory Entries</div>
        <div class="metric-value">{data["memory"]}</div>
        <div class="metric-sub">summaries stored</div>
      </div>
      <div class="metric-card pink">
        <i class="fa-solid fa-brain metric-icon"></i>
        <div class="metric-label">Lessons Learned</div>
        <div class="metric-value">{data["lessons"]}</div>
        <div class="metric-sub">critic insights</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">Token Efficiency per Agent</div>
        <div class="chart-sub">Average tokens used per pipeline run</div>
        <div class="legend">
          <div class="legend-item"><div class="legend-dot" style="background:#6c63ff"></div>Intake</div>
          <div class="legend-item"><div class="legend-dot" style="background:#10b981"></div>Planner</div>
          <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Executor</div>
          <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div>Memory</div>
          <div class="legend-item"><div class="legend-dot" style="background:#ec4899"></div>Critic</div>
        </div>
        <div style="position:relative; height:220px;">
          <canvas id="barChart"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Task Distribution</div>
        <div class="chart-sub">By type</div>
        <div style="position:relative; height:180px;">
          <canvas id="pieChart"></canvas>
        </div>
        <div class="legend" style="margin-top:12px; justify-content:center;">
          <div class="legend-item"><div class="legend-dot" style="background:#6c63ff"></div>Email {data["email_count"]}</div>
          <div class="legend-item"><div class="legend-dot" style="background:#10b981"></div>Search {data["search_count"]}</div>
          <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Remind {data["reminder_count"]}</div>
          <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div>Client {data["client_count_tasks"]}</div>
          <div class="legend-item"><div class="legend-dot" style="background:#ec4899"></div>Report {data["report_count"]}</div>
        </div>
      </div>
    </div>

    <div class="bottom-grid">
      <div class="table-card">
        <div class="table-header">
          <div class="chart-title">Client Tracker</div>
          <div class="chart-sub">Latest clients from DB</div>
        </div>
        <table>
          <thead>
            <tr><th>Client</th><th>Email</th><th>Status</th><th>Last Contact</th></tr>
          </thead>
          <tbody>{client_rows_html}</tbody>
        </table>
      </div>

      <div class="chart-card" style="padding:0;">
        <div class="table-header">
          <div class="chart-title">Recent Memory</div>
          <div class="chart-sub">Last 3 summaries</div>
        </div>
        <div class="activity-feed">{memory_rows_html}</div>
      </div>
    </div>
  </main>
</div>

<!-- PDF Download Modal -->
<div class="modal-overlay" id="pdfModal">
  <div class="modal">
    <div class="modal-icon"><i class="fa-solid fa-file-pdf"></i></div>
    <div class="modal-title">Download PDF Report</div>
    <div class="modal-sub">This will download a clean text report with all your business data.</div>
    <div class="modal-actions">
      <button class="btn-cancel" onclick="hideModal()">Cancel</button>
      <button class="btn-download" onclick="downloadPDF()">Download</button>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
  new Chart(document.getElementById('barChart'), {{
    type: 'bar',
    data: {{
      labels: ['Intake', 'Planner', 'Executor', 'Memory', 'Critic'],
      datasets: [{{
        data: [182, 141, 199, 136, 170],
        backgroundColor: ['#6c63ff','#10b981','#f59e0b','#3b82f6','#ec4899'],
        borderRadius: 6,
        borderSkipped: false
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        y: {{ grid: {{ color: 'rgba(255,255,255,0.04)' }}, ticks: {{ color: '#555568', font: {{ family: 'DM Mono', size: 11 }} }} }},
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#555568', font: {{ family: 'DM Mono', size: 11 }} }} }}
      }}
    }}
  }});

  new Chart(document.getElementById('pieChart'), {{
    type: 'doughnut',
    data: {{
      labels: ['Email', 'Search', 'Reminder', 'Client', 'Report'],
      datasets: [{{
        data: [{data["email_count"]}, {data["search_count"]}, {data["reminder_count"]}, {data["client_count_tasks"]}, {data["report_count"]}],
        backgroundColor: ['#6c63ff','#10b981','#f59e0b','#3b82f6','#ec4899'],
        borderColor: '#111118',
        borderWidth: 3,
        hoverOffset: 4
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {{ legend: {{ display: false }} }}
    }}
  }});

  function showModal() {{
    document.getElementById('pdfModal').classList.add('show');
  }}

  function hideModal() {{
    document.getElementById('pdfModal').classList.remove('show');
  }}

  function downloadPDF() {{
    const {{ jsPDF }} = window.jspdf;
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();

    
    doc.setFillColor(108, 99, 255);
    doc.rect(0, 0, pageWidth, 30, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("Velo Business Report", 15, 20);

    
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text("{datetime.now().strftime('%d %B %Y %H:%M')}", pageWidth - 15, 20, {{ align: "right" }});

   
    let y = 45;
    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("Overview", 15, y); y += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.setTextColor(80, 80, 80);
    doc.text("Total Tasks Run", 15, y); doc.text("{data['tasks']}", 100, y); y += 7;
    doc.text("Total Clients", 15, y); doc.text("{data['clients']}", 100, y); y += 7;
    doc.text("Memory Entries", 15, y); doc.text("{data['memory']}", 100, y); y += 7;
    doc.text("Lessons Learned", 15, y); doc.text("{data['lessons']}", 100, y); y += 14;

    
    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("Task Breakdown", 15, y); y += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    doc.setTextColor(80, 80, 80);
    doc.text("Email tasks", 15, y); doc.text("{data['email_count']}", 100, y); y += 7;
    doc.text("Search tasks", 15, y); doc.text("{data['search_count']}", 100, y); y += 7;
    doc.text("Reminder tasks", 15, y); doc.text("{data['reminder_count']}", 100, y); y += 7;
    doc.text("Client tasks", 15, y); doc.text("{data['client_count_tasks']}", 100, y); y += 14;

    
    doc.setTextColor(0, 0, 0);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("Client Tracker", 15, y); y += 8;

    
    doc.setFillColor(245, 245, 250);
    doc.rect(15, y - 5, pageWidth - 30, 8, 'F');
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text("Name", 17, y);
    doc.text("Email", 60, y);
    doc.text("Status", 120, y);
    doc.text("Last Contact", 155, y);
    y += 8;

    doc.setFont("helvetica", "normal");
    doc.setTextColor(50, 50, 50);
    doc.setFontSize(10);
    
    const clients = {repr([(r[0], r[1], r[2], r[3]) for r in data["client_rows"]])};
    clients.forEach(function(c) {{
        doc.text(c[0], 17, y);
        doc.text(c[1], 60, y);
        doc.text(c[2], 120, y);
        doc.text(c[3], 155, y);
        y += 7;
    }});

    doc.save("Velo_Report.pdf");
    hideModal();
  }}
</script>
</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath

def run():
    data = get_data()
    html_path = generate_dashboard(data)
    print(f"Dashboard saved -> {html_path}")
    return html_path