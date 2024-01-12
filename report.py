import pymongo
import os
from datetime import datetime
from bson import ObjectId
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Paragraph,Image
from reportlab.lib.pagesizes import A4,letter
from flask import Flask, send_file,after_this_request
from PyPDF2 import PdfMerger
from datetime import datetime
import pytz

# Connect to the MongoDB server running on localhost at the default port

def getpdf(type,user_id,req_calories_day,start_date_string,end_date_string):
    client = pymongo.MongoClient("mongodb+srv://esub:7864@foodeyeprod.ytyyxcw.mongodb.net/?retryWrites=true&w=majority")
    database_name = "test"
    db = client[database_name]
    start_date = datetime.fromisoformat(start_date_string)
    end_date = datetime.fromisoformat(end_date_string)
    
    # Construct the query
    query = {
        'updatedAt': {
            '$gte': start_date,
            '$lt': end_date
        },
        "user":ObjectId(user_id)
    }
    user_data = []
    user_data.append("Week")
    if type==2:
        user_data[0] = "Month"
    elif type == 3:
        user_data[0] = "Year"
    user_data.append(user_id)
    collection_name = "users"
    collection = db[collection_name]
    cursor = list(collection.find({"_id":ObjectId(user_id)}))[0]
    # print(cursor)
    user_data.append(cursor['name'])
    user_data.append(cursor['age'])
    user_data.append(cursor['gender'])
    user_data.append(cursor['weight'])
    user_data.append(cursor['height'])
    user_data.append(req_calories_day)
    
    
    # Retrieve all documents in the collection
    cursor = collection.find({"user":ObjectId(user_id)})
    
    
    # Choose the collection within the database
    collection_name = "nutrientries"
    collection = db[collection_name]
    cursor = collection.find(query)
    cursor = list(cursor)
    curr_cal = 0
    p = 0
    f = 0
    c = 0
    table_data = [['Food','Date', 'Time', 'Calories', 'Carb(G)', 'Fat(G)', 'Prot(G)']]
    for i in range(len(cursor)):
        mongo_utc_time = cursor[i]['updatedAt']
        target_time_zone = pytz.timezone('Asia/Kolkata')
        utc_datetime = mongo_utc_time.replace(tzinfo=pytz.utc).astimezone(target_time_zone)
        
        original_string = utc_datetime.astimezone(target_time_zone)
        dt_object = datetime.fromisoformat(str(original_string))
        formatted_date = dt_object.strftime("%d %b %Y").lstrip('0').replace(' 0', ' ')
        formatted_time = dt_object.strftime("%I:%M%p")
        curr_cal += float(cursor[i]['nutridata'][0])
        p+= float(cursor[i]['nutridata'][3])
        f+= float(cursor[i]['nutridata'][2])
        c+= float(cursor[i]['nutridata'][1])
        table_data.append([cursor[i]['foodname'],formatted_date,formatted_time,cursor[i]['nutridata'][0],cursor[i]['nutridata'][1],cursor[i]['nutridata'][2],cursor[i]['nutridata'][3]])
    user_data.append(round(curr_cal,2))
    temp = (p+f+c)
    p = p/temp
    f = f/temp
    c = c/temp
    days = (end_date - start_date).days
    req = int(req_calories_day)
    user_data.append(round(days*req,2))
    user_data.append(str(round(p,2))+" : "+str(round(f,2))+" : "+str(round(c,2)))
    # Close the MongoDB connection
    client.close()
    return user_data,table_data,p,f,c

# initializing variables with values
def first_page(user_data,table_data,p,f,c):
    fileName = './generated_pdfs/first.pdf'
    documentTitle = 'sample'
    
    table_width = 700
    pdf = canvas.Canvas(fileName)
    pdf.setTitle(documentTitle)
    # pdfmetrics.registerFont(TTFont('abc_light', 'SakBunderan.ttf'))
    
    text = "FOODSNAP DIET REPORT"
    text_color = colors.black
    text_size = 10
    is_bold = True
    
    # Define a style for the text
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = text_size
    style.textColor = text_color
    
    if is_bold:
        style.fontName = 'Times-Bold'
    
    
    # Set border attributes
    border_width = 2  # Adjust the border width as needed
    margin = 20  # Adjust the margin as needed
    border_color = (0, 0, 0)  # Black color, you can adjust RGB values if needed
    
    # Calculate the content area dimensions within the page
    A4 = letter
    content_width = A4[0] - (2 * margin)
    content_height = A4[1] - (2 * margin)
    
    # Draw borders around the content area to create a box-like border
    pdf.setStrokeColor(border_color)
    pdf.setLineWidth(border_width)
    
    # Draw top border
    pdf.line(margin, A4[1] - margin+45, A4[0] - margin-20, A4[1] - margin+45)
    
    # Draw bottom border
    pdf.line(margin, margin, A4[0] - margin-20, margin)
    
    # Draw left border
    pdf.line(margin, margin, margin, A4[1] - margin+45)
    
    # Draw right border
    pdf.line(A4[0] - 2*margin, margin, A4[0] - margin*2, A4[1] - margin+45)
    init_y = pdf._pagesize[1]-200
    
    def printInfo(heading,text, init_y):
        text1 = Paragraph(heading,style=style)
        text1.wrapOn(pdf,400,20)
        text1.drawOn(pdf,(pdf._pagesize[0]-520)//2,init_y)
        text2 = Paragraph(":"+"\t ")
        text2.wrapOn(pdf,400,20)
        text2.drawOn(pdf,(pdf._pagesize[0]-160)//2,init_y)
        text3 = Paragraph(text)
        text3.wrapOn(pdf,400,20)
        text3.drawOn(pdf,(pdf._pagesize[0]-120)//2,init_y)
        init_y -=20
        return init_y
        
    init_y = printInfo("Report Type",user_data[0],init_y)
    init_y = printInfo("Unique Id","FS"+user_data[1][:7],init_y)
    init_y = printInfo("Name",user_data[2],init_y)
    init_y = printInfo("Age",user_data[3],init_y)
    init_y = printInfo("Gender",user_data[4],init_y)
    init_y = printInfo("Weight",user_data[5],init_y)
    init_y = printInfo("Height",user_data[6],init_y)
    init_y = printInfo("Required Calories Per Day",user_data[7],init_y)
    init_y = printInfo("Weekly Caloric Balance",str(user_data[8])+"/"+str(user_data[9]),init_y)
    init_y = printInfo("P:F:C Ratio" ,user_data[10],init_y)
    
    
    
    data = [p,f, c]
    labels = ['Protein', 'Fat', 'Carbohydrates']
    
    # Draw a B/W pie chart
    drawing = Drawing(100, 200)
    pie = Pie()
    pie.x = 150
    pie.y = 20
    pie.width = 150
    pie.height = 150
    pie.data = data
    pie.labels = labels
    pie.slices.strokeWidth = 1
    pie.slices.strokeColor = colors.white# Set slice border color to black
    pie.slices[0].fillColor = colors.brown  # Set slice fill color to black
    pie.slices[1].fillColor = colors.green  # Set slice fill color to gray
    pie.slices[2].fillColor = colors.skyblue # Set slice fill color to white
    pie.slices[3].popout = 10  # Pop out a slice
    
    drawing.add(pie)
    
    # Render the chart on the PDF canvas
    drawing.drawOn(pdf, 240, 470)
    
    image_path = os.path.join(os.path.dirname(__file__), 'pdf-gen-assets', 'header.png')


    img = Image(image_path, width=550, height=140)
    img.drawOn(pdf,(pdf._pagesize[0]-552)// 2 ,pdf._pagesize[1]-166)
    
    # text_paragraph = Paragraph(text, style)
    # text_paragraph.wrapOn(pdf, 500, 200) 
    # text_paragraph.drawOn(pdf,(pdf._pagesize[0]-340)// 2 ,pdf._pagesize[1]-40)
    line_start_x = 40
    line_start_y = 770
    line_end_x = 560
    line_end_y = 770
    
    data = table_data
    
    # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    # Calculate table width
    table_width = pdf._pagesize[0] - 1 * pdf._pagesize[0] * 0.1  # Assuming 10% margin on each side
    col_widths = [table_width / len(data[0])] * len(data[0])
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    
    # Wrap and draw the table
    table.wrapOn(pdf, 0, 0)
    table_height = table._height
    
    x_position = pdf._pagesize[0] * 0.048  # Horizontal margin of 10%
    y_position = pdf._pagesize[1] - table_height - 400  # Adjust vertical position as needed
    table.drawOn(pdf, x_position, y_position)
    pdf.save()


# initializing variables with values
def next_page(table_data,index):
    fileName = './generated_pdfs/next'+index+'.pdf'
    documentTitle = 'next'
    
    table_width = 700
    pdf = canvas.Canvas(fileName)
    pdf.setTitle(documentTitle)
    # pdfmetrics.registerFont(TTFont('abc_light', 'SakBunderan.ttf'))
    
    text = "FOODSNAP DIET REPORT"
    text_color = colors.black
    text_size = 10
    is_bold = True
    
    # Define a style for the text
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontSize = text_size
    style.textColor = text_color
    
    if is_bold:
        style.fontName = 'Times-Bold'
    
    border_width = 2  # Adjust the border width as needed
    margin = 20  # Adjust the margin as needed
    border_color = (0, 0, 0)  # Black color, you can adjust RGB values if needed
    
    # Calculate the content area dimensions within the page
    A4 = letter
    
    # Draw borders around the content area to create a box-like border
    pdf.setStrokeColor(border_color)
    pdf.setLineWidth(border_width)
    
    # Draw top border
    pdf.line(margin, A4[1] - margin+45, A4[0] - margin-20, A4[1] - margin+45)
    
    # Draw bottom border
    pdf.line(margin, margin, A4[0] - margin-20, margin)
    
    # Draw left border
    pdf.line(margin, margin, margin, A4[1] - margin+45)
    
    # Draw right border
    pdf.line(A4[0] - 2*margin, margin, A4[0] - margin*2, A4[1] - margin+45)
    init_y = pdf._pagesize[1]-200
    
    data = table_data
    
    # Define table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    table_width = pdf._pagesize[0] - 1 * pdf._pagesize[0] * 0.1  # Assuming 10% margin on each side
    col_widths = [table_width / len(data[0])] * len(data[0])
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(table_style)
    
    table.wrapOn(pdf, 0, 0)
    table_height = table._height
    
    x_position = pdf._pagesize[0] * 0.048  # Horizontal margin of 10%
    y_position = pdf._pagesize[1] - table_height - 30  # Adjust vertical position as needed
    table.drawOn(pdf, x_position, y_position)
    pdf.save()


def merge_pdfs_in_folder(folder_path):
    merger = PdfMerger()
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    pdf_files.sort()
    for pdf_file in pdf_files:
        file_path = os.path.join(folder_path, pdf_file)
        merger.append(file_path)

    merged_pdf_path = os.path.join(folder_path, "diet-report.pdf")

    with open(merged_pdf_path, "wb") as output_file:
        merger.write(output_file)
    return merged_pdf_path

def delete_files_in_folder(folder_path):
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    except Exception as err:
        print("Ugh! directory doesn't have files")
            
app = Flask(__name__)

# @app.route('/get_pdf', methods=['POST'])
# def get_pdf():
#     delete_files_in_folder('./generated_pdfs')
#     type = 1
#     user_id = "659d8386695e77372c201c84"
#     req_calories_day = "1800"
#     start_date_string = "2024-01-01T00:00:00.000+00:00"
#     end_date_string = "2024-01-13T00:00:00.000+00:00"
#     user_data, table_data, p, f, c = getpdf(type, user_id, req_calories_day, start_date_string, end_date_string)
#     if len(table_data) < 21:
#         first_page(user_data, table_data, p, f, c)
#     else:
#         first_page(user_data, table_data, p, f, c)
#         table_data = table_data[21:]
#         ind = 1
#         while table_data:
#             if len(table_data) > 40:
#                 next_page(table_data[:40], ind)
#                 table_data = table_data[40:]
#             else:
#                 next_page(table_data, ind)
#                 table_data = []
#             ind += 1
#     pdf_path = merge_pdfs_in_folder('./generated_pdfs')
#     custom_filename = 'diet-report.pdf'

#     return send_file(pdf_path, as_attachment=True, download_name=custom_filename)

if __name__ == '__main__':
    app.run(debug=True,port=8082)