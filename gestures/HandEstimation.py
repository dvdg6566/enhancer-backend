import mediapipe as mp#hand detection
import cv2#video feed
import numpy as np#math
import time#gets current time easier
import multiprocessing
from flask import Flask,Response
from flask_cors import CORS
import requests

mp_drawing = mp.solutions.drawing_utils#helps draw landmarks (joints)
mp_hands =mp.solutions.hands#Hand detection tools

def text(image,txt,pos):#draws text to the screen
    cv2.putText(image,txt,pos,cv2.FONT_HERSHEY_SIMPLEX,1
    ,(0,0,255),2,cv2.LINE_AA,False)
   
#sends commands
target = "http://18.171.127.234:8000/sendGesture"
def command(val):
    cmd = ""
    if(val==0):
        cmd = "throw"
    elif(val==1):
        cmd = "swipe"
    elif(val==2):
        cmd = "middle"
    elif(val==3):
        cmd = "snap"
    elif(val==4):
        cmd = "zoomin"
    elif val == 5:
        cmd = "point"

    print(f"Sending command {cmd}")
    r = requests.post(target, data={"gesture": cmd})

#this bit is fiddly, make sure u check diffrent cams and perms
cap =cv2.VideoCapture(0)#getting camera feed from first device

#DEBUGGER Functions
#gets coords
def joint_coords(joint,hand):
    j =hand.landmark[joint]
    return  np.array([j.x,j.y])
#gets video dimensions
if cap.isOpened():
    width  = cap.get(3)
    height = cap.get(4)

#index-index of hand, hand-landmarks, results-all results
def draw_to_hand(image,hand,txt):#gets string label
    wrist =joint_coords(mp_hands.HandLandmark.WRIST,hand)#wrist coords
    coords = tuple(np.multiply(wrist,[width,height]).astype(int))
    text(image,txt,coords)
#END OF DEBUGGER FUNCTIONS

# function definition to compute magnitude o f the vector
def magnitude(vector):
    return np.sqrt(sum(pow(element, 2) for element in vector))

def get_point_distances(hand,point_list):#gets distance between point pairs
    mlist=[]#magnitude list
    for point in point_list:
        #Turns coordinates into arrays
        j=hand.landmark[point[0]]
        a = [j.x,j.y,j.z]
        
        j=hand.landmark[point[1]]
        b = [j.x,j.y,j.z]
        
        mlist.append(magnitude(np.array([a[0]-b[0],a[1]-b[1],a[2]-b[2]]))*100)#appends rescaled magnitude
    return mlist#returns the list of magnitudes

def abs_pos(hand,num):#return absolut postion of a landmark(point) as an array
    j=hand.landmark[num]
    return np.array([j.x,j.y,j.z])

def finger_values(hand):#gets which fingers are up or down (true is down)
    output=[]
    points = [[4,2],[5,8],[12,9],[16,13],[20,17],[8,4]]#points that need to be comapres
    crits = [5.8,6,6,6,6,4.8]#max distance to be true
    
    distances=get_point_distances(hand,points)#finds distances bettwen important points
    
    for i in range(len(distances)):#for every distance
        output.append(distances[i]<=crits[i])#return wheter it's less than critical
    return output
        
def closeopen(a):
    if(a[1] and a[2] and a[3] and a[4]):
        return 1
    elif (a[1] or a[2] or a[3] or a[4])==False:
        return 0
    else:
        return -1


prev = [np.array([0,0,0]),np.array([0,0,0])]#Previous positon (needed for motion calculation)
ct=[0,0,0,0,0]#counter for the number of times the conditions for each command were met
last_time=0#last time an action was triggered
throw_t=0#needed for functions which change signal
zoom_in_con=False#checks if the start of zoom in has been done

def webcam():
    global prev, ct, last_time, throw_t, zoom_in_con
    #instantiantes Hands model
    #Min_detection ->first detection
    #min_tracking_ is -> after first detection
    with mp_hands.Hands(min_detection_confidence=0.8,min_tracking_confidence=0.5,max_num_hands =2)as hands:
        while cap.isOpened():#looping frames while open
            ret, frame = cap.read()# read the return value and frame(image)
            
            image =cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)#converts frame to RGB for mp
            
            image = cv2.flip(image,1)#horizontal flip of image
            
            #makes sure to to accidently override
            image.flags.writeable =False#also preformace boost
            
            results = hands.process(image)#actually detects the hands
            
            image.flags.writeable =True #lets actually change
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)#converts back to gbr
            
            #Renders to screen
            if(results.multi_hand_landmarks):#if a hand was actually detected
                print_vals=[]#stores values to be printed to the screen
                for num, hand in enumerate(results.multi_hand_world_landmarks):#looks at hand postions usign real world coords
                    vals = finger_values(hand)#gets wheter fingers are up or down plus zoom con
                    print_vals.append(vals)#adds them to the print vals
                                    
                    w=[abs_pos(hand,9),abs_pos(hand,0)]#current world postion of the two important points
                    move=[magnitude(np.subtract(w[0],prev[0]))*1000,
                        magnitude(np.subtract(w[1],prev[1]))*100]#calculaates how much the two important points have moved
                    prev=w[:]#new prev
                    
                    co=closeopen(vals)#checks for the close open or neither command
                    
                    #Flick testing
                    move_con=move[0]>1.6 and move[0]<15 and move[1]>1.6 and move[1]<15#checks if hand is moving rapidly
                    if(move_con):
                        if(co==1 and ((time.time()-last_time)>2)):#starts throw conditon
                            ct[0]+=1
                            throw_t=time.time()#reset timer
                        elif co==0 and ((time.time()-last_time)>2):#starts swipe conditon
                            ct[1]+=1
                            
                    else:
                        ct[1]=0#resets swipe
                        if((time.time()-throw_t)>0.5):#resets throw after time
                            ct[0]=0
                    
                    #holding m test
                    hold_con=(vals[1] and vals[3] and vals[4]) and not(vals[2])# finger m hold contiond
                    if(hold_con and co==-1  and ((time.time()-last_time)>4)):#checks counter conditon
                        ct[2]+=1
                    else:
                        ct[2]=0
                        
                    #snap (maybe rewrite)
                    snap_con=(vals[3] and vals[4]) and not(vals[0]or vals[2])#pre snaping conditon
                    if(snap_con and co==-1  and ((time.time()-last_time)>2)):#checks counter conditon
                        ct[3]+=1
                        throw_t=time.time()#resets timer
                    else:
                        if((time.time()-throw_t)>0.5):
                            ct[3]=0
                            
                    #zoom in
                    if(zoom_in_con and co==-1  and not(vals[5]) and (vals[2] and vals[3] and vals[4]) and ((time.time()-last_time)>2)):#checks zoom
                        ct[4]+=1
                    elif(vals[5]):
                        zoom_in_con=True
                        ct[4]=0
                    else:
                        zoom_in_con=False
                        ct[4]=0
                        
                    #command caller
                    if(ct[0]>=2 and co==0):
                        last_time=time.time()
                        command(0)
                        ct[0]=0
                    elif(ct[1]>=2 and co==0):
                        last_time=time.time()
                        command(1)
                        ct[1]=0
                    elif(ct[2]>=4):
                        last_time=time.time()
                        command(2)
                        ct[2]=0
                    elif(ct[3]>=2 and co==-1 and (vals[3] and vals[4] and vals[2]) and not(vals[0])):
                        last_time=time.time()
                        command(3)
                        ct[3]=0
                    elif(ct[4]>=2):
                        last_time=time.time()
                        command(4)
                        ct[4]=0
                        
                for num, hand in enumerate(results.multi_hand_landmarks):#splits into vars
                    #image is the main image aka frame
                    #hand is the landmarks
                    #mp_hands.Hand_CONNECTIONS tells hand connections
                    mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)#draws landmarks
                    draw_to_hand(image,hand,str(print_vals[num]))#DEBUGGER
                        
            # cv2.imshow('Hand tracking', image)
            #renders image to the screen
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            if cv2.waitKey(10) & 0xFF == ord('q'):#closes window when q
                break
        
    cap.release()#stops reacording
    cv2.destroyAllWindows()#breaks window

app = Flask(__name__)

# Disables flask logging
app.logger.disabled = True
import logging
log = logging.getLogger('werkzeug')
log.disabled = True

CORS(app)

@app.route('/webcam')
def webcam_display():
    return Response(webcam(), mimetype='multipart/x-mixed-replace;boundary=frame')

def run_server():
    print("[+] Starting flask server in background")
    print("[+] Flask Server listening on port 8080")
    app.run(host='0.0.0.0', port=8080, debug=False)

time.sleep(3)
# server_process = multiprocessing.Process(target=run_server)
# server_process.start()
# time.sleep(1)
run_server()
