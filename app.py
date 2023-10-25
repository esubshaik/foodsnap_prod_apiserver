from flask import Flask, request, jsonify
import csv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for your app

# Load the data from the CSV file into a dictionary
data = {}

with open('food_data.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        food_name = row['FOOD']
        data[food_name] = {
            'CALORIES(G)': float(row['CALORIES(G)']),
            'CARBOHYDRATES(G)': float(row['CARBOHYDRATES(G)']),
            'PROTEIN(G)': float(row['PROTEIN(G)']),
            'FAT(G)': float(row['FAT(G)'])
        }

@app.route('/get_nutrition', methods=['GET'])
def get_nutrition():
    food_name = request.args.get('food_name')
    if food_name in data:
        return jsonify(data[food_name])
    else:
        return jsonify({'error': 'Food not found'})

if __name__ == '__main__':
    app.run(debug=True)
