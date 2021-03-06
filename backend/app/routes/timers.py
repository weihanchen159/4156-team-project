#!/user/bin/python3
# -*- coding: utf-8 -*-
""" Create Api for Timer
"""

import datetime
from dateutil import parser
from flask import request, jsonify
from app.ext import db
from app.routes import routes
from app.models import Timer, TimerToUser
from app.utls.apiStatus import apiStatus
from app.utls.utilities import judgeKeysExist
from app.utls.utilities import judgeKeysCorrect
from app.utls.utilities import judgeInputValid
from app.utls.utilities import judgeIntValid

# @routes.route('/timers')
# def testTimers():
#     """this is for test"""
#     return "timers url"

@routes.route('/timers/', methods=['GET'])
def getTimers():
    """This function is for the server to get timers from the database"""
    code, msg, result = 0, "", {"data": None}
    timerId = request.args.get('timerId', None)
    userId = request.args.get('userId', None)
    if timerId is not None :
        if not judgeIntValid(timerId) :
            code, msg = 400, apiStatus.getResponseMsg(400)
            result["code"] = code
            result["message"] = msg
            return jsonify(result)
        targetTimer = Timer.query.get(timerId)  # query by primary key
        if not targetTimer:
            code, msg = 404, apiStatus.getResponseMsg(404)
        else:
            result["data"] = targetTimer.toDict()
            code, msg = 200, apiStatus.getResponseMsg(200)
        result["code"] = code
        result["message"] = msg
        return jsonify(result)
    if userId is not None:
        result['data'] = [] # should also return an empty list
        targetTimer = Timer.query.filter_by(userId=userId).all()
        if not targetTimer:
            code, msg = 404, apiStatus.getResponseMsg(404)
        else:
            # result['data'] = []
            for timer in targetTimer :
                result['data'].append(timer.toDict()) # to iso format
            code, msg = 200, apiStatus.getResponseMsg(200)
        result["code"] = code
        result["message"] = msg
        return jsonify(result)
    code, msg = 400, apiStatus.getResponseMsg(400)
    result["code"] = code
    result["message"] = msg

    return jsonify(result)

@routes.route('/timers/<timerId>', methods=['DELETE'])
def deleteTimers(timerId):
    """This function is for the server to delete timers"""
    code, msg, result = 0, "", {"data": None}
    if not judgeIntValid(timerId) :
        code, msg = 400, apiStatus.getResponseMsg(400)
        result["code"] = code
        result["message"] = msg
        return jsonify(result)
    targetTimer = Timer.query.get(timerId)  # query by primary key
    if not targetTimer:
        code, msg = 404, apiStatus.getResponseMsg(404)
    else:

        try:
            db.session.delete(targetTimer)
            db.session.commit()
            result["data"] = {"id": timerId}
            code, msg = 200, apiStatus.getResponseMsg(200)
        except:
            code, msg = 500, apiStatus.getResponseMsg(500)
    result["code"] = code
    result["message"] = msg

    return jsonify(result)

@routes.route('/timers/', methods=['POST'])
def createTimers():
    """This function is for the server to create new timers"""
    data =  request.get_json()
    postAttrs = ['userId', 'title', 'startTime', 'duration', 'breakTime', 'round']
    code, msg, result = 0, "", {"data": None}
    if not judgeKeysExist(data, postAttrs):
        code, msg = 400, apiStatus.getResponseMsg(400)
    else:
        if not judgeInputValid(data) :
            code, msg = 400, apiStatus.getResponseMsg(400)
            result["code"] = code
            result["message"] = msg
            return jsonify(result)
        userId = data['userId']
        title = data['title']
        description = data['description'] if 'description' in data else None
        zoomLink = data['zoomLink'] if 'zoomLink' in data else None
        startTime = data['startTime']
        # formatStartTime = parser.parse(startTime)
        # testFormStartTime = datetime.datetime.fromisoformat(startTime)
        # print(formatStartTime, testFormStartTime)
        duration = int(data['duration'])
        breakTime = int(data['breakTime'])
        round = int(data['round'])

        oldTimers = Timer.query.filter_by(userId=userId).all()
        if oldTimers is not None:
            for oldTimer in oldTimers:
                totalDuration = (oldTimer.duration + oldTimer.breakTime) * oldTimer.round
                totalDuration = datetime.timedelta(minutes=totalDuration)
                endTime =  parser.parse(oldTimer.startTime) + totalDuration
                # sTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
                sTime = parser.parse(startTime)
                newDuration = (duration + breakTime) * round
                newDuration = datetime.timedelta(minutes=newDuration)
                eTime = sTime + newDuration
                if parser.parse(oldTimer.startTime) <= sTime < endTime or parser.parse(oldTimer.startTime) < eTime <= endTime:
                    code, msg = 403, apiStatus.getResponseMsg(403)
                    result["code"] = code
                    result["message"] = msg
                    return jsonify(result)
                if sTime < parser.parse(oldTimer.startTime) and eTime > endTime:
                    code, msg = 403, apiStatus.getResponseMsg(403)
                    result["code"] = code
                    result["message"] = msg
                    return jsonify(result)
        try:
            newTimer = Timer(userId=str(userId), title=str(title),
                             description=str(description), zoomLink=str(zoomLink),
                             startTime=startTime, duration=str(duration),
                             breakTime=str(breakTime), round=str(round))
            db.session.add(newTimer)
            newTimerTwo = Timer.query.filter_by(userId=userId).all()
            # print(newTimerTwo)

            newTimerToUser = TimerToUser(timerId=newTimer.id, userId=userId, status=1)
            db.session.add(newTimerToUser)
            db.session.commit()

            result["data"] = newTimer.toDict({
                "added": True,
                "isCreator": True,
                "timerToUserId": userId,
            })
            # result["data"]["startTime"] = startTime # remain to be string for the frontend consistent, or change to utcstring
            code, msg = 201, apiStatus.getResponseMsg(201)
        except:
            code, msg = 500, apiStatus.getResponseMsg(500)
    result["code"] = code
    result["message"] = msg
    return jsonify(result)


@routes.route('/timers/<timerId>', methods=['PUT'])
def putTimers(timerId):
    """This function is for the server to update timers"""
    data =  request.get_json()
    postAttrs = ['id', 'userId', 'title', 'startTime', 'duration',
                 'breakTime', 'round', 'description', 'zoomLink',
                 'isCreator', 'timerToUserId', 'added']
    code, msg, result = 0, "", {"data": None}
    if not judgeKeysCorrect(data, postAttrs):
        code, msg = 400, apiStatus.getResponseMsg(400)
    else:
        if not judgeInputValid(data) :
            code, msg = 400, apiStatus.getResponseMsg(400)
            result["code"] = code
            result["message"] = msg
            return jsonify(result)
        targetTimer = Timer.query.get(timerId)
        if not targetTimer:
            code, msg = 404, apiStatus.getResponseMsg(404)
        else:
            try:
                targetTimer.update(data)
                db.session.commit()
                result["data"] = targetTimer.toDict({
                    "added": data["added"] if "added" in data else True,
                    "isCreator": data["isCreator"] if "isCreator" in data else True,
                    "timerToUserId": data["timerToUserId"] if "timerToUserId" in data else targetTimer.userId,
                })
                code, msg = 201, apiStatus.getResponseMsg(201)
            except:
                code, msg = 500, apiStatus.getResponseMsg(500)
    result["code"] = code
    result["message"] = msg
    return jsonify(result)


# @routes.route('/timers/test', methods=['POST'])
# def tTimers():
#     data =  request.get_json()
#     postAttrs = ['userId', 'title', 'startTime', 'duration', 'breakTime', 'round']
#     code, msg, result = 0, "", {"data": None}
#     if not judgeKeysExist(data, postAttrs):
#         code, msg = 400, apiStatus.getResponseMsg(400)
#     else:
#         userId = data['userId']
#         oldTimers = Timer.query.filter_by(userId=userId).all()
#         for oldTimer in oldTimers:
#             print(oldTimer.startTime)
#             print(type(oldTimer.startTime))
#             totalDuration = (oldTimer.duration + oldTimer.breakTime)*oldTimer.round
#             totalDuration = datetime.timedelta(minutes=totalDuration)
#             endTime = oldTimer.startTime + totalDuration
#             startTime = data['startTime']
#             startTime = datetime.datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
#             duration = data['duration']
#             breakTime = data['breakTime']
#             round = data['round']
#             newDuration = (duration + breakTime)*round
#             newDuration = datetime.timedelta(minutes=newDuration)
#             newEndTime = startTime + newDuration
#             print(startTime)
#             print(newEndTime)
#             if oldTimer.startTime <= startTime < endTime \
#                   or oldTimer.startTime < newEndTime <= endTime:
#                 return "error1"
#             elif startTime < oldTimer.startTime and newEndTime > endTime:
#                 return "error2"
#
#             print(endTime)
#     return "test"
