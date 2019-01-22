# template script to implement a computer vision feature via surround
import logging
import cv2


# generic template to apply inference on an image array
def inference_frame(img_array, config_settings=None):
    """
    Do something with the `img_array'
    :param img_array:
    :param config_settings:
    :return: Inference information
    """
    return None


def main():
    logging.info("This is the main function ...")
    # skeleton for video stream
    video_stream = cv2.VideoCapture(0)
    # iteration to grab frames from the video
    while True:
        # grab the frame array
        boolean_flag, frame_img_bgr = video_stream.read()
        # apply inference on the frame
        modified_frame = inference_frame(frame_img_bgr)
        # show the frame
        cv2.imshow('Frame', frame_img_bgr)
        # stop the video stream via the keyboard: "q"
        keyboard_event_stop = cv2.waitKey(1) & 0xFF
        if keyboard_event_stop == ord("q"):
            break


if __name__ == '__main__':
    main()
