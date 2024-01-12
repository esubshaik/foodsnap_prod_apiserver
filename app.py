from flask import Flask, request, jsonify
import csv
from flask_cors import CORS
import os
import base64
from report import * 

app = Flask(__name__)
CORS(app)  
data = {}
with open('food_data.csv', 'r') as file1:
    csv_reader = csv.DictReader(file1)
    for row in csv_reader:
        food_name = row['FOOD']
        data[food_name] = {
            'CALORIES(G)': float(row['CALORIES(G)']),
            'CARBOHYDRATES(G)': float(row['CARBOHYDRATES(G)']),
            'PROTEIN(G)': float(row['PROTEIN(G)']),
            'FAT(G)': float(row['FAT(G)'])
        }
description = {}
with open('food_description.csv', 'r') as file2:
    csv_reader = csv.DictReader(file2)
    for row in csv_reader:
        food_name = row['FOOD']
        description[food_name] = {
            'Description' : str(row['Description'])
        }


@app.route('/get_nutrition', methods=['GET'])
def get_nutrition():
    food_name = request.args.get('food_name')
    if food_name in data:
        return jsonify(data[food_name])
    else:
        return jsonify({'error': 'Food not found'})

def get_images(food_name):
    # food_name = request.args.get('food_name')
    images = []
    food_folder = os.path.join('myfoodimages', food_name)  # Replace with your data folder path

    if not os.path.exists(food_folder):
        return jsonify({'error': 'Food not found'})

    for filename in os.listdir(food_folder):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
            with open(os.path.join(food_folder, filename), 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                images.append(image_data)
    return images


@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    try:
        weight = float(request.args.get('weight'))
        height = float(request.args.get('height'))*30.48
        # age = float(request.args.get('age'))
        foodname = str(request.args.get('foodname'))
        # age = (30.48*age)

        # gender = str(request.args.get('gender'))
        # if gender.lower() == "m":
        #     DCN = 66.5 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
        # else:
        #     DCN = 655 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

        BMI = weight / (height / 100)**2
        BMI_category = ""
        if BMI < 18.5:
            BMI_category = "Underweight"
        elif BMI >= 18.5 and BMI < 25:
            BMI_category = "Normal Weight"
        elif BMI >= 25 and BMI < 30:
            BMI_category = "Overweight"
        else:
            BMI_category = "Obese"

        suggested_foods = []
        if foodname in data.keys():
            if BMI_category == "Underweight":
                if float(data[foodname]['PROTEIN(G)']) > 10 and float(data[foodname]['CARBOHYDRATES(G)']) > 10 or float(data[foodname]['CALORIES(G)']) > 200:
                    suggested_foods.append([foodname, data[foodname] ,get_images(foodname),description[foodname]])
            elif BMI_category == "Normal Weight":
                if float(data[foodname]['PROTEIN(G)']) > 10 and float(data[foodname]['CARBOHYDRATES(G)']) > 10 and float(data[foodname]['FAT(G)']) < 10 or float(data[foodname]['CALORIES(G)']) >= 10:
                    suggested_foods.append([foodname, data[foodname] ,get_images(foodname),description[foodname]])
            elif BMI_category == "Overweight" or BMI_category == "Obese":
                if float(data[foodname]['PROTEIN(G)']) > 10 and float(data[foodname]['CARBOHYDRATES(G)']) < 10 and float(data[foodname]['FAT(G)']) < 10 or float(data[foodname]['CALORIES(G)']) < 200:
                    suggested_foods.append([foodname, data[foodname] ,get_images(foodname),description[foodname]])
        # print(suggested_foods)
        return jsonify(suggested_foods),200
    except Exception as e:
        error_message = str(e)  # Get the string representation of the exception
        print(error_message)  # Optional: Print the error message for debugging purposes
        return jsonify({"error": error_message}), 500

agedata = []

# Read the CSV file and store the data in a list of dictionaries
with open('minmax_calorie.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        agedata.append({
            'age_min': int(row['age_min']),
            'age_max': int(row['age_max']),
            'women_min': float(row['women_min']),
            'women_max': float(row['women_max']),
            'men_min': float(row['men_min']),
            'men_max': float(row['men_max'])
        })

@app.route('/get_minmax_calorie', methods=['GET'])
def get_minmax_calorie():
    try:
        user_age = int(request.args.get('user_age'))
        user_gender = request.args.get('user_gender')
        for item in agedata:
            if item['age_min'] <= user_age <= item['age_max']:
                if user_gender.lower() == 'women':
                    return jsonify({'min_calories': item['women_min'], 'max_calories': item['women_max']})
                elif user_gender.lower() == 'men':
                    return jsonify({'min_calories': item['men_min'], 'max_calories': item['men_max']})
                else:
                    return jsonify({'error': 'invalid gender or age'})
        
        return jsonify({'error': 'age not found in any range'})
    except ValueError:
        return jsonify({'error': 'invalid age'})
    

@app.route('/get_description', methods=['GET'])
def get_food_description():
    food_name = request.args.get('foodname')
    try:
        file_path = os.path.join('descriptions', f"{food_name}.txt")
        with open(file_path, 'r') as file:
            content = file.read()
            return jsonify({'data': content})
    except FileNotFoundError:
        print({'data': "Description file for '{food_name}' not found."})
    except Exception as e:
        print({'data': "An error occurred: {str(e)}"})

@app.route('/get_pdf', methods=['POST'])
def get_pdf():
    delete_files_in_folder('./generated_pdfs')
    type = 1
    user_id = "659d8386695e77372c201c84"
    start_date_string = "2024-01-01T00:00:00.000+00:00"
    end_date_string = "2024-01-13T00:00:00.000+00:00"
    user_data, table_data, p, f, c = getpdf(type, user_id, start_date_string, end_date_string)
    if len(table_data) < 21:
        first_page(user_data, table_data, p, f, c)
    else:
        first_page(user_data, table_data, p, f, c)
        table_data = table_data[21:]
        ind = 1
        while table_data:
            if len(table_data) > 40:
                next_page(table_data[:40], ind)
                table_data = table_data[40:]
            else:
                next_page(table_data, ind)
                table_data = []
            ind += 1
    pdf_path = merge_pdfs_in_folder('./generated_pdfs')
    custom_filename = 'diet-report.pdf'
    return send_file(pdf_path, as_attachment=True, download_name=custom_filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)
