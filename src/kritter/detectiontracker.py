#
# This file is part of Vizy 
#
# All Vizy source code is provided under the terms of the
# GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
# Those wishing to use Vizy source code, software and/or
# technologies under different licensing terms should contact us at
# support@charmedlabs.com. 
#

# This code was adapted from pyimagesearch.com.

from scipy.spatial import distance as dist
from collections import OrderedDict, defaultdict
import numpy as np

def iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou  


class DetectionTracker:
    def __init__(self, maxDisappeared=1, maxDistance=250, maxClassHistory=100, threshold=0.5, iouEquiv=0.4, classSwitch=False):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.classHistory = OrderedDict()

        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared

        # store the maximum distance between centroids to associate
        # an object -- if the distance is larger than this maximum
        # distance we'll start to mark the object as "disappeared"
        self.maxDistance = maxDistance

        self.maxClassHistory = maxClassHistory
        self.threshold = threshold
        self.iouEquiv = iouEquiv
        self.classSwitch = classSwitch
        if not self.classSwitch:
            self.maxClassHistory = 1

    def register(self, box, classScore):
        # Create new entry in object tables.
        # when registering an object we use the next available object
        # ID to store the box
        self.objects[self.nextObjectID] = box
        self.classHistory[self.nextObjectID] = [classScore]
        self.disappeared[self.nextObjectID] = -self.maxDisappeared
        self.nextObjectID += 1

    def deregister(self, objectID):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        del self.objects[objectID]
        del self.classHistory[objectID]
        del self.disappeared[objectID]

    def mostLikelyClass(self, history):
        histogram = defaultdict(lambda: np.array([0.0, 0.0]))
        for h in history:
            histogram[h[0]] += np.array([h[1], 1.0])
        max_ = [0.0, 1.0]
        for k, v in histogram.items():
            if v[0]>max_[0]:
                max_ = v 
                class_ = k 
        return class_, max_[0]/max_[1] 

    def removeOverlaps(self):
        ious = {}
        deregs = set()
        for i in self.objects:
            for j in self.objects:
                if i==j:
                    break
                ious[(i, j)] = iou(self.objects[i], self.objects[j])
            if i==j:
                continue
        ious = {k: v for k, v in sorted(ious.items(), key=lambda item: item[1], reverse=True)}
        for k, v in ious.items():
            if v>=self.iouEquiv:
                i, j = k
                if self.classSwitch:
                    if len(self.classHistory[i])>len(self.classHistory[j]):
                        deregs.add(j)
                    else:
                        deregs.add(i)
                else:
                    if self.classHistory[i][0][0]==self.classHistory[j][0][0]:
                        if self.classHistory[i][0][1]>self.classHistory[j][0][1]:
                            print("*** remove j", self.classHistory[i][0][1], self.classHistory[j][0][1])
                            deregs.add(j)
                        else:
                            print("*** remove i", self.classHistory[i][0][1], self.classHistory[j][0][1])
                            deregs.add(i)
            else: # v<self.iouEquiv, which means no more left
                break
        for d in deregs:
            self.deregister(d)

    def mostLikelyState(self, showDisappeared):
        objects = {}
        for obj in self.objects:
            if self.disappeared[obj]>=0 and (showDisappeared or self.disappeared[obj]==0):
                classScore = self.mostLikelyClass(self.classHistory[obj])
                objInfo = {"box": self.objects[obj], "class": classScore[0], "score": classScore[1]}
                try:
                    classScore0 = self.classScore0[obj]
                    objInfo['class0'] = classScore0[0]
                    objInfo['score0'] = classScore0[1]
                except: 
                    pass
                objects[obj] = objInfo


        return objects

    def update(self, dets, showDisappeared=False):
        self.classScore0 = {}
        # check to see if the list of input bounding box rectangles
        # is empty      
        if len(dets)==0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                if self.disappeared[objectID]>=0:
                    self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, or if we're pre-registered, deregister it
                if self.disappeared[objectID]<0 or self.disappeared[objectID]>self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.mostLikelyState(showDisappeared)

        classScores = []
        # initialize an array of input centroids for the current frame
        if self.classSwitch:
            inputBoxes = np.zeros((len(dets), 4), dtype=int)
        else:
            inputBoxes = np.zeros((len(dets), 5), dtype=int)

        # loop over the bounding box rectangles
        for i, det in enumerate(dets):
            if self.classSwitch:
                inputBoxes[i] = det['box']
            else:
                # use the bounding box coordinates to derive the centroid
                # Add class index so we can use the class index to match between images.
                # Use 10000 multiplier because this exceeds all likely image resolutions 
                # and distances within the image.  
                inputBoxes[i] = det['box'] + [det['index']*10000]
            classScores.append((det['class'], det['score']))
        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputBoxes)):
                if classScores[i][1]>=self.threshold:
                    self.register(inputBoxes[i], classScores[i])
        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectBoxes = np.array(list(self.objects.values()))

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            if self.classSwitch:
                objectCentroids = np.vstack(((objectBoxes[:, 0] + objectBoxes[:, 2])/2, (objectBoxes[:, 1] + objectBoxes[:, 3])/2)).T
                inputCentroids = np.vstack(((inputBoxes[:, 0] + inputBoxes[:, 2])/2, (inputBoxes[:, 1] + inputBoxes[:, 3])/2)).T
            else:
                objectCentroids = np.vstack(((objectBoxes[:, 0] + objectBoxes[:, 2])/2, (objectBoxes[:, 1] + objectBoxes[:, 3])/2, objectBoxes[:, 4])).T
                inputCentroids = np.vstack(((inputBoxes[:, 0] + inputBoxes[:, 2])/2, (inputBoxes[:, 1] + inputBoxes[:, 3])/2, inputBoxes[:, 4])).T
            D = dist.cdist(objectCentroids, inputCentroids)
            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value as at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                if row in usedRows or col in usedCols:
                    continue

                # if the distance between centroids is greater than
                # the maximum distance, do not associate the two
                # centroids to the same object
                if D[row, col] > self.maxDistance:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputBoxes[col]
                self.classScore0[objectID] = classScores[col]
                self.classHistory[objectID].insert(0, classScores[col])
                if len(self.classHistory[objectID])>self.maxClassHistory:
                    self.classHistory[objectID] = self.classHistory[objectID][0:self.maxClassHistory]
                if self.disappeared[objectID]<0:
                    self.disappeared[objectID] += 1
                else:
                    self.disappeared[objectID] = 0
                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # we need to check and see if some of these objects have
            # potentially disappeared
            # loop over the unused row indexes
            for row in unusedRows:
                # grab the object ID for the corresponding row
                # index and increment the disappeared counter
                objectID = objectIDs[row]
                if self.disappeared[objectID]>=0:
                    self.disappeared[objectID] += 1

                # check to see if the number of consecutive
                # frames the object has been marked "disappeared"
                # for warrants deregistering the object
                if self.disappeared[objectID]<0 or self.disappeared[objectID]>self.maxDisappeared:
                    self.deregister(objectID)

            # if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            for col in unusedCols:
                if classScores[col][1]>=self.threshold:
                    self.register(inputBoxes[col], classScores[col])


        self.removeOverlaps()
        # return the set of trackable objects
        return self.mostLikelyState(showDisappeared)

    def setThreshold(self, threshold):
        self.threshold = threshold
