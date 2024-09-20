import sys
import argparse
import copy
import datetime

import numpy as np
import cv2 as cv

from facial_fer_model import FacialExpressionRecog

# sys.path.append('../face_detection_yunet')
from yunet import YuNet

# Check OpenCV version
assert cv.__version__ >= "4.9.0", \
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

def visualize(image, det_res, fer_res, box_color=(0, 255, 0), text_color=(0, 0, 255)):

    print('%s %3d faces detected.' % (datetime.datetime.now(), len(det_res)))

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
        print("Face %2d: %d %d %d %d %s." % (ind, bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3], fer_type))
        cv.rectangle(output, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)
        cv.putText(output, str(ind), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)
        cv.putText(output, fer_type, (bbox[0], bbox[1]-10 ), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)
        identification = identification + 1
        landmarks = det[4:14].astype(np.int32).reshape((5, 2))
        for idx, landmark in enumerate(landmarks):
            cv.circle(output, landmark, 2, landmark_color[idx], 2)
    return output

#     detect_model = YuNet(modelPath='model/face_detection_yunet_2023mar.onnx')
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


# if __name__ == '__main__':
#     backend_id = backend_target_pairs[args.backend_target][0]
#     target_id = backend_target_pairs[args.backend_target][1]

#     detect_model = YuNet(modelPath='model/face_detection_yunet_2023mar.onnx')

#     fer_model = FacialExpressionRecog(modelPath=args.model,
#                                       backendId=backend_id,
#                                       targetId=target_id)


#     vs = cv.VideoCapture(args.input)

#     print(vs)
#     while vs.isOpened():

#         print("source: ", args.input)
#         ret, frame = vs.read()
#         image = cv.resize(frame, (800,600))

#         status, dets, fer_res = process(detect_model, fer_model, image)

#         # if status:
#         image = visualize(image, dets, fer_res)

#         # if args.save:
#         cv.imwrite('result.jpg', image)
#         print('Results saved to result.jpg\n')

#         # if args.vis:
#         cv.namedWindow(args.input, cv.WINDOW_AUTOSIZE)
#         cv.imshow(args.input, image)
#         cv.waitKey(1)

# backend_id = backend_target_pairs[args.backend_target][0]
# target_id = backend_target_pairs[args.backend_target][1]

# detect_model = YuNet(modelPath='model/face_detection_yunet_2023mar.onnx')

# fer_model = FacialExpressionRecog(modelPath=args.model,
#                                     backendId=backend_id,
#                                     targetId=target_id)


def main_facial_express(input_frame):
    backend_id = backend_target_pairs[args.backend_target][0]
    target_id = backend_target_pairs[args.backend_target][1]

    detect_model = YuNet(modelPath='model/face_detection_yunet_2023mar.onnx')
    facial_model = 'facial_api/model/facial_expression_recognition_mobilefacenet_2022july.onnx'
    fer_model = FacialExpressionRecog(modelPath=facial_model,
                                      backendId=backend_id,
                                      targetId=target_id)
    image = input_frame

    status, dets, fer_res = process(detect_model, fer_model, image)

    # if status:
    image = visualize(image, dets, fer_res)
    return image


