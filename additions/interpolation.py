import numpy as np



eye = np.array([1, 2, 3, 4, 5, 6, 7, -999, 9, -999, 5, 60, 10, 4, 8, 9, -999, 4, 6, 8, 2, 15, -999, 6, 14]).reshape(5,5)

eye = np.where(eye <-998, np.nan, eye)
print(eye)


#while np.isnan(np.sum(eye)):

w = 1

for index, x in np.ndenumerate(eye):
    #print(index[0], index[1], x)
    if x == x:
        pass
    else:
        s = eye[index[0]-w:index[0]+w+1,index[1]-w:index[1]+w+1]
        if np.isnan(s).sum() > 2*w:
            pass
        else:
            s = s[np.logical_not(np.isnan(s))]
            eye[index] = np.mean(s)

print(eye)
