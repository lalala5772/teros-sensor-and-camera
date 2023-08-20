import cv2
import time

# 웹캠 캡처 초기화
cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 의미합니다. 다른 카메라를 사용할 경우에는 1, 2, ...

# 저장할 동영상 파일의 경로와 설정
output_path = "captured_video.mp4"
frame_width = int(cap.get(3))  # 웹캠의 프레임 가로 크기
frame_height = int(cap.get(4))  # 웹캠의 프레임 세로 크기
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (frame_width, frame_height))

start_time = time.time()
while True:
    ret, frame = cap.read()  # 프레임 읽기

    if not ret:
        break

    # 프레임을 출력하거나 저장할 수 있습니다.
    cv2.imshow('Webcam', frame)
    out.write(frame)

    # 1초 후 종료
    if time.time() - start_time > 1:
        break

# 사용이 끝난 자원들을 해제합니다.
cap.release()
out.release()
cv2.destroyAllWindows()
