import json

def load_data():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Data file not found.")
        return {}
    except:
        print("Something went wrong when reading data.")
        return {}
    else:
        print("Data successfully imported.")

def save_data(data):
    try:
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)
    except:
        print("Data saving error!")
    else:
        print("Data saved successfully.")
