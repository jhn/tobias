(ns domain.cv
  (:require [clj-http.client :as http]))

(defn handle-file-sightcorp [tempfile creds]
  (let [r (http/post "http://api.sightcorp.com/api/detect/"
                     {:multipart [{:name "img" :content tempfile}
                                  {:name "app_key" :content (creds :app_key)}
                                  {:name "client_id" :content (creds :client_id)}]})
        body (:body r)]
    (response body)))

(defn handle-file-microsoft [tempfile creds]
  (let [r (http/post "https://api.projectoxford.ai/face/v0/detections?analyzesFaceLandmarks=false&analyzesAge=true&analyzesGender=true&analyzesHeadPose=false"
                     {:headers {"Content-Type" "application/octet-stream"
                                "Ocp-Apim-Subscription-Key" (creds :key)}
                      :body tempfile})
        body (:body r)]
    (response body)))

(defn handle-file-faceplus [tempfile creds]
  (let [r (http/post "http://apius.faceplusplus.com/detection/detect"
                     {:multipart [{:name "img" :content tempfile}
                                  {:name "api_key" :content (creds :api_key)}
                                  {:name "api_secret" :content (creds :api_secret)}]})
        body (:body r)]
    (response body)))
