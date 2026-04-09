import cv2
import time
import boto3

# AWS S3 setup
s3 = boto3.client('s3')
BUCKET_NAME = 'driver-drowsiness-events'

# Load Haar cascades
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# Camera start
cap = cv2.VideoCapture(0)

sleep_counter = 0
sleep_threshold = 15
image_saved = False

while True:
    ret, frame = cap.read()

    if not ret:
        print("Camera error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    eyes_detected = False

    for (x, y, w, h) in faces:
        # GREEN BOX (FACE)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            # GREEN BOX (EYES)
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            eyes_detected = True

    # 🔴 DROWSINESS LOGIC
    if not eyes_detected:
        sleep_counter += 1
    else:
        sleep_counter = 0
        image_saved = False

    if sleep_counter > sleep_threshold:
        cv2.putText(frame, "DROWSINESS DETECTED!", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        if not image_saved:
            filename = f"drowsy_{int(time.time())}.jpg"

            # Save image
            cv2.imwrite(filename, frame)

            time.sleep(1)

            # Upload to S3
            s3.upload_file(filename, BUCKET_NAME, filename)

            print("Uploaded to S3:", filename)

            image_saved = True

    # Show output
    cv2.imshow("Driver Monitoring", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()