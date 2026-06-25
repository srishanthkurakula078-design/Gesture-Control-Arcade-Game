def fingersUp(lmList):

    if len(lmList) == 0:
        return []

    fingers = []

    # Thumb
    if lmList[4][1] > lmList[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Index
    if lmList[8][2] < lmList[6][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Middle
    if lmList[12][2] < lmList[10][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Ring
    if lmList[16][2] < lmList[14][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Pinky
    if lmList[20][2] < lmList[18][2]:
        fingers.append(1)
    else:
        fingers.append(0)

    return fingers


def detectGesture(fingers):

    if fingers == [0, 0, 0, 0, 0]:
        return "FIST"

    elif fingers == [1, 1, 1, 1, 1]:
        return "OPEN PALM"

    elif fingers == [0, 1, 0, 0, 0]:
        return "POINTING"

    elif fingers == [0, 1, 1, 0, 0]:
        return "PEACE"

    elif fingers == [1, 0, 0, 0, 0]:
        return "THUMBS UP"

    else:
        return "UNKNOWN"
        