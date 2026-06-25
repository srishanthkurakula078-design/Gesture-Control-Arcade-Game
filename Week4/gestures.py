import math


def distance(lmList, p1, p2):

    x1, y1 = lmList[p1][1], lmList[p1][2]
    x2, y2 = lmList[p2][1], lmList[p2][2]

    return math.hypot(x2 - x1, y2 - y1)


def handScale(lmList):

    scale = distance(lmList, 0, 9)

    if scale == 0:
        return 1

    return scale


def fingersUp(lmList, handLabel="Right"):

    fingers = []

    if handLabel == "Right":
        fingers.append(1 if lmList[4][1] > lmList[3][1] else 0)
    else:
        fingers.append(1 if lmList[4][1] < lmList[3][1] else 0)

    for tip in [8, 12, 16, 20]:

        if lmList[tip][2] < lmList[tip-2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def classify(lmList, handLabel="Right"):

    if len(lmList) < 21:
        return "NONE"

    fingers = fingersUp(lmList, handLabel)

    scale = handScale(lmList)

    pinch = distance(lmList, 4, 8) / scale

    if pinch < 0.30 and fingers[2] and fingers[3] and fingers[4]:
        return "OK"

    if fingers == [0,0,0,0,0]:
        return "FIST"

    if fingers == [1,1,1,1,1]:
        return "OPEN PALM"

    if fingers == [0,1,0,0,0]:
        return "POINT"

    if fingers == [0,1,1,0,0]:
        return "PEACE"

    if fingers == [1,0,0,0,0]:
        return "THUMB"

    return "UNKNOWN"
    