import cv2

# 웹캠 캡처 초기화
cap = cv2.VideoCapture(0)  # 0은 기본 웹캠을 의미합니다. 다른 카메라를 사용할 경우에는 1, 2, ...

ret, frame = cap.read()  # 프레임 읽기

if ret:
    # 이미지 저장할 경로
    output_path = "captured_image.jpg"
    
    # 프레임을 이미지로 저장
    cv2.imwrite(output_path, frame)
    print(f"Captured image saved at {output_path}")
else:
    print("Failed to capture image")

# 사용이 끝난 자원들을 해제합니다.
cap.release()
cv2.destroyAllWindows()
