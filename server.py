from flask import Flask, json, request
import os
import csv

app = Flask(__name__)


def open_file(mode):
    file_object = {}
    file_name = "data/groceries.csv"

    if mode == "r":
        csvfile = open(file_name, mode)
        reader = csv.DictReader(csvfile, delimiter=",", quotechar=",")
        file_object["csvfile"] = csvfile
        file_object["reader"] = reader

    elif mode == "w" or mode == "a":
        csvfile = open(file_name, mode)
        fieldnames = ["item", "quantity", "purchased"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        file_object["csvfile"] = csvfile
        file_object["writer"] = writer

    return file_object


def close_file(file_object):
    file_object["csvfile"].close()


def file_exists_check():
    if os.path.exists("data/groceries.csv"):
        return 1
    else:
        return 0


def item_already_exists(item):
    file = open_file("r")
    reader = file["reader"]

    item_found = False

    for row in reader:
        if row["item"] == item:
            item_found = True
            break

    close_file(file)
    return item_found


def find_item(item):
    file = open_file("r")
    reader = file["reader"]

    item_found = False
    found_at_line = 0
    line = 0

    for row in reader:
        if row["item"] == item:
            item_found = True
            found_at_line = line
            break
        line += 1

    close_file(file)
    return found_at_line


def file_line_count():
    file = open_file("r")
    reader = file["reader"]

    line_count = 0

    for row in reader:
        line_count += 1

    close_file(file)
    return line_count


def edit_item(item_no, item, quantity):
    file = open_file("r")
    reader = file["reader"]

    file_data = []
    for row in reader:
        file_data.append(row)

    close_file(file)

    for i in range(len(file_data)):
        if i == item_no:
            file_data[i]["item"] = item
            file_data[i]["quantity"] = quantity

    file = open_file("w")
    writer = file["writer"]
    writer.writeheader()

    for row in file_data:
        writer.writerow(
            {"item": row["item"], "quantity": row["quantity"], "purchased": row["purchased"]})

    close_file(file)


def delete_item(item_no):
    file = open_file("r")
    reader = file["reader"]

    file_data = []
    for row in reader:
        file_data.append(row)

    close_file(file)
    modified_file_data = []

    for i in range(len(file_data)):
        if not i == item_no:
            modified_file_data.append(file_data[i])

    file = open_file("w")
    writer = file["writer"]
    writer.writeheader()

    for row in modified_file_data:
        writer.writerow(
            {"item": row["item"], "quantity": row["quantity"], "purchased": row["purchased"]})

    close_file(file)


def find_purchased_items():
    if file_exists_check():
        file = open_file("r")
        reader = file["reader"]

        purchased_items = []
        for row in reader:
            if row["purchased"] == "True":
                purchased_items.append(row)

        return purchased_items

    else:
        return json.dumps({"code": 400, "message": "groceries.csv file does not exist"})


def mark_purchased(item_no):
    if file_exists_check():
        file = open_file("r")
        reader = file["reader"]

        file_data = []
        for row in reader:
            file_data.append(row)

        close_file(file)

        for i in range(len(file_data)):
            if i == item_no:
                file_data[i]["purchased"] = True

        file = open_file("w")
        writer = file["writer"]
        writer.writeheader()

        for row in file_data:
            writer.writerow(
                {"item": row["item"], "quantity": row["quantity"], "purchased": row["purchased"]})

        close_file(file)

    else:
        return json.dumps({"code": 400, "message": "groceries.csv file does not exist"})


def read_file():
    file = open_file("r")
    reader = file["reader"]

    response = []

    for row in reader:
        temp = {}
        temp["item"] = row["item"]
        temp["quantity"] = row["quantity"]
        temp["purchased"] = row["purchased"]
        response.append(temp)

    close_file(file)
    return response


def write_file(item, quantity, purchased):
    if file_exists_check():
        if item_already_exists(item):
            return 0
        else:
            file = open_file("a")
            writer = file["writer"]
            writer.writerow(
                {"item": item, "quantity": quantity, "purchased": purchased})
            close_file(file)
            return 1

    else:
        file = open_file("w")
        writer = file["writer"]
        writer.writeheader()
        writer.writerow(
            {"item": item, "quantity": quantity, "purchased": purchased})
        close_file(file)
        return 1


@app.route("/listing", methods=["GET"])
def send_groceries_data():
    if file_exists_check():
        response = read_file()
        if len(response):
            return json.dumps({"code": 200, "message": "Success", "items": response})
        else:
            return json.dumps({"code": 400, "message": "No items present currently"})

    else:
        return json.dumps({"code": 400, "message": "groceries.csv file does not exist"})


@app.route("/create", methods=["POST"])
def create_item():
    item = request.json["item"].capitalize()
    quantity = int(request.json["quantity"])

    if item == "" and quantity == "":
        return json.dumps({"code": 400, "message": "Item and Quantity missing"})
    elif item == "":
        return json.dumps({"code": 400, "message": "Item missing"})
    elif quantity == "":
        return json.dumps({"code": 400, "message": "Quantity missing"})
    elif quantity == 0:
        return json.dumps({"code": 400, "message": "Quantity cannot be 0"})

    if write_file(item, quantity, False):
        return json.dumps({"code": 200, "message": "Item added successfully"})
    else:
        return json.dumps({"code": 400, "message": "Item already exists"})


@app.route("/edit/<item_no>", methods=["POST"])
def edit_item_at_a_given_line(item_no):
    item_no = int(item_no) - 1
    item = request.json["item"].capitalize()
    quantity = int(request.json["quantity"])

    if item_no == -1:
        return json.dumps({"code": 400, "message": "item_no cannot be 0"})
    elif quantity == 0:
        return json.dumps({"code": 400, "message": "Quantity cannot be 0"})

    lines_in_file = file_line_count()

    if item_no >= lines_in_file:
        return json.dumps(
            {"code": 400, "message": "item_no cannot be greater than file row count of " + str(lines_in_file)})

    if file_exists_check():
        if item_already_exists(item):
            index = find_item(item)
            if index == item_no:
                edit_item(item_no, item, quantity)
                return json.dumps({"code": 200, "message": "Item updated successfully"})
            else:
                return json.dumps(
                    {"code": 400,
                     "message": "Item that you want to edit already exists. Please enter a unique item different from what already exist"})

        else:
            edit_item(item_no, item, quantity)
            return json.dumps({"code": 200, "message": "Item updated successfully"})

    else:
        return json.dumps({"code": 400, "message": "groceries.csv file does not exist"})


@app.route("/delete", methods=["POST"])
def delete_item_at_given_line():
    item_no = int(request.json["item_no"]) - 1

    if item_no == -1:
        return json.dumps({"code": 400, "message": "item_no cannot be 0"})

    lines_in_file = file_line_count()

    if item_no >= lines_in_file:
        return json.dumps(
            {"code": 400, "message": "item_no cannot be greater than file row count of " + str(lines_in_file)})

    else:
        if file_exists_check():
            delete_item(item_no)
            return json.dumps({"code": 200, "message": "Item deleted"})
        else:
            return json.dumps({"code": 400, "message": "groceries.csv file does not exist"})


@app.route("/purchased", methods=["GET", "POST"])
def send_purchased_data():
    if request.method == "GET":
        purchased_items = find_purchased_items()
        return json.dumps({"code": 200, "message": "Success", "items": purchased_items})

    elif request.method == "POST":
        item_no = int(request.json["item_no"]) - 1

        if item_no == -1:
            return json.dumps({"code": 400, "message": "item_no cannot be 0"})

        lines_in_file = file_line_count()

        if item_no >= lines_in_file:
            return json.dumps(
                {"code": 400, "message": "item_no cannot be greater than file row count of " + str(lines_in_file)})

        else:
            mark_purchased(item_no)
            return json.dumps({"code": 200, "message": "Item marked purchased"})


@app.after_request
def add_header(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization ')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')

    return response
