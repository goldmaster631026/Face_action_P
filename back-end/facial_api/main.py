import sys
sys.path.append('facial_api/')
import argparse
import imutils
import numpy as np
import cv2 as cv
import time
from facial_fer_model import FacialExpressionRecog
from image_caption import main_image_caption
import json
from yunet import YuNet

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
# Check OpenCV_py version
assert cv.__version__ >= "4.10.0", \
       "Please install latest opencv-python to try this demo: python3 -m pip install --upgrade opencv-python"

# Valid combinations of backends and targets
backend_target_pairs = [
    [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_TARGET_CPU],
    [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA],
    [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA_FP16],
    [cv.dnn.DNN_BACKEND_TIMVX,  cv.dnn.DNN_TARGET_NPU],
    [cv.dnn.DNN_BACKEND_CANN,   cv.dnn.DNN_TARGET_NPU]
]

parser = argparse.ArgumentParser(description='Facial Expression Recognition')
parser.add_argument('--input', '-i', type=str,
                    help='Path to the input image. Omit for using default camera.')
parser.add_argument('--model', '-m', type=str, default='./model/facial_expression_recognition_mobilefacenet_2022july.onnx',
                    help='Path to the facial expression recognition model.')
parser.add_argument('--backend_target', '-bt', type=int, default=0,
                    help='''Choose one of the backend-target pair to run this demo:
                        {:d}: (default) OpenCV implementation + CPU,
                        {:d}: CUDA + GPU (CUDA),
                        {:d}: CUDA + GPU (CUDA FP16),
                        {:d}: TIM-VX + NPU,
                        {:d}: CANN + NPU
                    '''.format(*[x for x in range(len(backend_target_pairs))]))
parser.add_argument('--save', '-s', action='store_true',
                    help='Specify to save results. This flag is invalid when using camera.')
parser.add_argument('--vis', '-v', action='store_true',
                    help='Specify to open a window for result visualization. This flag is invalid when using camera.')
args = parser.parse_args()


start_time = time.time()
initial_time = time.time()
interval = 1 

flag = 1
start_time = 0
frame_number = 0
frame_json = {}

action_capture_model = "facial_api/model/resnet-34_kinetics.onnx"
facial_model_path = 'facial_api/model/facial_expression_recognition_mobilefacenet_2022july.onnx'
face_model_path = 'facial_api/model/face_detection_yunet_2023mar.onnx'


backend_id = backend_target_pairs[args.backend_target][0]
target_id = backend_target_pairs[args.backend_target][1]


fer_model = FacialExpressionRecog(modelPath=facial_model_path, backendId=backend_id, targetId=target_id)
detect_model = YuNet(modelPath=face_model_path)
gp = cv.dnn.readNet(action_capture_model)






def visualize(image, det_res, fer_res, box_color=(0, 255, 0), text_color=(0, 0, 255)):

    # print('%s %3d faces detected.' % (datetime.datetime.now(), len(det_res)))

    output = image.copy()
    landmark_color = [
        (255,  0,   0),  # right eye
        (0,    0, 255),  # left eye
        (0,  255,   0),  # nose tip
        (255,  0, 255),  # right mouth corner
        (0,  255, 255)   # left mouth corner
    ]
    identification = 0
    for ind, (det, fer_type) in enumerate(zip(det_res, fer_res)):
        bbox = det[0:4].astype(np.int32)
        fer_type = FacialExpressionRecog.getDesc(fer_type)
        # print("Face %2d: %d %d %d %d %s." % (ind, bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3], fer_type))
        cv.rectangle(output, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)
        cv.putText(output, str(ind), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)
        # cv.putText(output, fer_type, (bbox[0], bbox[1]-10 ), cv.FONT_HERSHEY_DUPLEX, 5, text_color)
        cv.putText(output, fer_type, (bbox[0], bbox[1]-10 ), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)
        identification = identification + 1
        landmarks = det[4:14].astype(np.int32).reshape((5, 2))

        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)

    return output

def ConvertJsonData(det_res, fer_res):

    total_face_json ={}
    identification = 0
    for ind, (det, fer_type) in enumerate(zip(det_res, fer_res)):

        personal_face_json = '{}'
        bbox = det[0:4].astype(np.int32)
        fer_type = FacialExpressionRecog.getDesc(fer_type)
        identification = identification + 1
        landmarks = det[4:14].astype(np.int32).reshape((5, 2))

        personal_data = {}
        personal_data["Face Location"] = {"top_left": (bbox[0], bbox[1]), "bottom_right": (bbox[0]+bbox[2], bbox[1]+bbox[3]) }
        personal_data["Face expression"] = fer_type
        personal_data["Right Eye Location"] = {"x": landmarks[0][0], "y": landmarks[0][1]}
        personal_data["Left Eye Location"] = {"x": landmarks[1][0], "y": landmarks[1][1]}
        personal_data["Noise Eye Location"] = {"x": landmarks[2][0], "y": landmarks[2][1]}
        personal_data["Right Mouse Location"] = {"x": landmarks[3][0], "y": landmarks[3][1]}
        personal_data["Left Mouse Location"] = {"x": landmarks[4][0], "y": landmarks[4][1]}

        total_face_json["person " + str(ind)] = personal_data
    return total_face_json


def process(detect_model, fer_model, frame):
    h, w, _ = frame.shape
    detect_model.setInputSize([w, h])
    dets = detect_model.infer(frame)

    if dets is None:
        return False, None, None

    fer_res = np.zeros(0, dtype=np.int8)
    for face_points in dets:
        fer_res = np.concatenate((fer_res, fer_model.infer(frame, face_points[:-1])), axis=0)
    return True, dets, fer_res



def Face_capture(frame, frame_time):
    
    status, dets, fer_res = process(detect_model, fer_model, frame)

    # (if ischaractoristic == True:)
    # print("Charaterization " + str(frame_time) )
    frame_json["Time_" + str(frame_time) + "_Seconds"] = ConvertJsonData(dets, fer_res)
        # with open('data.json', 'w') as file:
        #     json.dump(frame_json, file, cls=NumpyEncoder, indent=4)

    # return frame
    return frame_json


def main_facial_api(video, facial_unit, caption_unit ):
    global frame_number, frame_json

    frame_number = 0
    frame_json = {}
    # if args["gpu"] > 0:
    #     print("setting preferable backend and target to CUDA...")
    # gp.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
    # gp.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
    
    video_capture = cv.VideoCapture(video)
    fps = video_capture.get(cv.CAP_PROP_FPS) 

    start_time = time.time()

    # width = int(video_capture.get(cv.CAP_PROP_FRAME_WIDTH))
    # height = int(video_capture.get(cv.CAP_PROP_FRAME_HEIGHT))


    # fourcc = cv.VideoWriter_fourcc(*'mp4v')# *'MJPG' for .avi format
    # video_writer = cv.VideoWriter('facial_api/output/result.mp4', fourcc, fps, (width, height), True)
    fps = int(fps)
    print("fps: " + str(fps))
    print(start_time)
    cap_img = ' '
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        frame_time = 0
        if not ret:
            break
        
        if frame_number % (fps * caption_unit) == 0:
            frame = cv.resize(frame, (256,256))
            cap_img = main_image_caption(frame)
            
            # print("Image_caption: " + cap_img)

        if frame_number % (fps * facial_unit) == 0:
            frame = cv.resize(frame, (800,600))
            frame_time = frame_number/(fps)
            Face_capture(frame, frame_time)


            # Check if the key "Person" is present in the dictionary
            if "person 0" in frame_json["Time_" + str(frame_time) + "_Seconds"]:
                frame_json["Time_" + str(frame_time) + "_Seconds"]["Caption of Frame"] = cap_img
                # print("The key 'Person' is present in the JSON data.")
            else:
                # print("The key 'Person' is not present in the JSON data.")
                frame_json["Time_" + str(frame_time) + "_Seconds" ]["Caption of Frame"] = "There is no person in this frame."




        frame_number = frame_number + 1
        

    video_capture.release()
    # video_writer.release()
    frame_number = 0
    # end_time = time.time()
    # print(end_time - start_time)
    return json.dumps(frame_json, cls=NumpyEncoder, indent=4)
    # return frame_json

# main_facial_api("input/c1.mp4")