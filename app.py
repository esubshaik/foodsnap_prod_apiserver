from flask import Flask, request, jsonify
import csv
from flask_cors import CORS
import os
import base64

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


if __name__ == '__main__':
    app.run(debug=True)
