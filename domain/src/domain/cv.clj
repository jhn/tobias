(ns domain.cv
  (:require [clj-http.client :as http]))

(def microsoft-creds {:key "oof"})

(def face-plus-creds {:api_key "oof"
                      :api_secret "rab"})

(def sightcorp-creds {:app_key "oof"
                      :client_id "rab"})

(defn post-sightcorp [tempfile creds]
  (http/post "http://api.sightcorp.com/api/detect/"
             {:multipart [{:name "img" :content tempfile}
                          {:name "app_key" :content (creds :app_key)}
                          {:name "client_id" :content (creds :client_id)}]}))

(defn post-microsoft [tempfile creds]
  (http/post "https://api.projectoxford.ai/face/v0/detections?analyzesFaceLandmarks=false&analyzesAge=true&analyzesGender=true&analyzesHeadPose=false"
             {:headers {"Content-Type" "application/octet-stream"
                        "Ocp-Apim-Subscription-Key" (creds :key)}
              :body tempfile}))

(defn post-faceplus [tempfile creds]
  (http/post "http://apius.faceplusplus.com/detection/detect"
             {:multipart [{:name "img" :content tempfile}
                                  {:name "api_key" :content (creds :api_key)}
                                  {:name "api_secret" :content (creds :api_secret)}]}))
