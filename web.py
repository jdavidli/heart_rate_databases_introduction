from flask import Flask, jsonify, request
from pymodm import connect
import requests
import models
import datetime
from flask_cors import CORS
#from datetime import datetime


# open up connection to db
connect("mongodb://vcm-3476.vm.duke.edu:27017/heart_rate_app")
app = Flask(__name__)
CORS(app)

@app.route("/api/heart_rate/<user_email>", methods=["GET"])
def get_heart_rate(user_email):
    """
    Gets all heart rate measurements for the specified user
    :param email: str email of the user
    :return heart_rate: heart rates for specified user
    :raises HTTPError: User not in database
    """
    try:
        # Get the first user where _id=email
        user = models.User.objects.raw({"_id": user_email}).first()
        hr = user.heart_rate
        times = user.heart_rate_times
        stuffed = [{'time': time, 'heartrate': heartrate} for time, heartrate in zip(times, hr)]
        return jsonify(stuffed)
    except:
        raise requests.HTTPError('404: User not found')


@app.route("/api/heart_rate/average/<user_email>", methods=["GET"])
def get_avg_heart_rate(user_email):
    """
    Gets the average heart rate measurement for the specified user
    :param email: str email of the user
    :return avg: average heart rate for specified user
    :raises HTTPError: User not in database
    """
    try:
        user = models.User.objects.raw({"_id": user_email}).first()
        heart_rates = user.heart_rate
        avg = sum(heart_rates)/float(len(heart_rates))
        return jsonify(avg)
    except:
        raise requests.HTTPError('404: User not found')


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """
    Creates a user with the given data, if the user doesn't exist. otherwise
    adds heart rate to existing user.
    :return user_data: JSON of user data
    :raises KeyError: input data is missing key
    :raises TypeError: input data is the wrong type
    """
    try:
        user_data = request.get_json()
        if not 'user_email' in user_data:
            raise KeyError('Missing user email')
        if not 'user_age' in user_data:
            raise KeyError('Missing user age')
        if not 'heart_rate' in user_data:
            raise KeyError('Missing user heart rate')
        if not isinstance(user_data['user_email'], str):
            raise TypeError('Email is not a string')
        if not isinstance (user_data['user_age'], int):
            raise TypeError('Age is not a number')
        if not isinstance (user_data['heart_rate'], int):
            raise TypeError('Heart rate is not a number')
        # check if user exists
        user = models.User.objects.raw({"_id": user_data['user_email']}).first()
        add_heart_rate(user_data['user_email'], user_data['heart_rate'], datetime.datetime.now())
        return jsonify(user_data)
    except TypeError:
        raise
    except KeyError:
        raise
    except:
        create_user(email=user_data['user_email'], age=user_data[
            'user_age'], heart_rate=user_data['heart_rate'], time=datetime.datetime.now())
        return jsonify(user_data)


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def interval_heart_rate():
    """
    Gets all heart rate measurements for the specified user
    :param email: str email of the user
    """
    user_data = request.get_json()
    # Get the first user where _id=email
    user = models.User.objects.raw({"_id": user_data['user_email']}).first()
    datetime_object = datetime.strptime(user_data['heart_rate_average_since'], '%Y-%m-%d %H:%M:%S.%f')
    # identifies the heart rates after the specified time
    i = 0
    interval_hr = []
    for j in user.heart_rate_times:
        if j > datetime_object:
            interval_hr.append(user.heart_rate[i])
        i = i+1
    avg = sum(interval_hr)/float(len(interval_hr))
    data = {
    "interval_heart_rate": avg, "tachycardic": False
    }
    # tachycardia
    if 1/365 <= user.age <= 2/365:
        if avg > 159:
            data["tachycardic"] = True
    if 3/365 <= user.age <= 6/365:
        if avg > 166:
            data["tachycardic"] = True
    if 7/365 <= user.age <= 21/365:
        if avg > 182:
            data["tachycardic"] = True
    if 22/365 <= user.age <= 60/365:
        if avg > 179:
            data["tachycardic"] = True
    if 61/365 <= user.age <= 150/365:
        if avg > 186:
            data["tachycardic"] = True
    if 151/365 <= user.age <= 330/365:
        if avg > 169:
            data["tachycardic"] = True
    if 331/365 <= user.age <= 2:
        if avg > 151:
            data["tachycardic"] = True
    if 3 <= user.age <= 4:
        if avg > 137:
            data["tachycardic"] = True
    if 5 <= user.age <= 7:
        if avg > 133:
            data["tachycardic"] = True
    if 8 <= user.age <= 11:
        if avg > 130:
            data["tachycardic"] = True
    if 12 <= user.age <= 15:
        if avg > 119:
            data["tachycardic"] = True
    if user.age > 15:
        if avg > 100:
            data["tachycardic"] = True
    return jsonify(data)


def create_user(email, age, heart_rate, time):
    """
    Creates a user with the specified email and age. If the user already exists in the DB this WILL
    overwrite that user. It also adds the specified heart_rate to the user
    :param email: str email of the new user
    :param age: number age of the new user
    :param heart_rate: number initial heart_rate of this new user
    :param time: datetime of the initial heart rate measurement
    """
    u = models.User(email, age, [], [])  # create a new User instance
    u.heart_rate.append(heart_rate)  # add initial heart rate
    u.heart_rate_times.append(time)  # add initial heart rate time
    u.save()  # save the user to the database


def add_heart_rate(email, heart_rate, time):
    """
    Appends a heart_rate measurement at a specified time to the user specified by
    email. It is assumed that the user specified by email exists already.
    :param email: str email of the user
    :param heart_rate: number heart_rate measurement of the user
    :param time: the datetime of the heart_rate measurement
    """
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    user.heart_rate.append(heart_rate)  # Append the heart_rate to the user's list of heart rates
    user.heart_rate_times.append(time)  # append the current time to the user's list of heart rate times
    user.save()  # save the user to the database


def print_user(email):
    """
    Prints the user with the specified email
    :param email: str email of the user of interest
    :return:
    """
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)


if __name__ == '__main__':
    app.run(debug=True)
