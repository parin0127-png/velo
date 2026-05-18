from fpdf import FPDF
from datetime import datetime

def generate_pdf(title, content, filename = "report.pdf"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica" , "B" , 20)
    pdf.cell(0, 10, title, ln=10)

    pdf.set_font("Helvetica" , "", 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln = 10)

    pdf.line(10 , 30 , 200 , 30)
    pdf.ln(10)

    pdf.set_font("Helvetica" , "" , 12)
    pdf.multi_cell(0 , 10 ,  content)

    pdf.output(filename)
    print(f"> PDF saved : {filename}")