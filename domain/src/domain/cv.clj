(ns domain.cv
  (:require [clj-http.client :as http]
            [clojure.core.async :refer [>! go chan alts!! thread >!!]]))

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

(defn post-cv
  [c                                  ; out channel
   f                                  ; a function that POSTs to a cv provider
   image                              ; file on which to run cv
   creds]                             ; creds for the cv api
  (thread                             ; gets its own thread because we're blocking
    (let [res (f image creds)]        ; call f to POST
      (>!! c (:body res)))))          ; put the resulting body in the chan

(defn get-features [image]
  (let [sightcorp-chan (chan)
        microsoft-chan (chan)
        faceplus-chan  (chan)]
    (post-cv microsoft-chan post-microsoft image microsoft-creds)
    (post-cv faceplus-chan post-faceplus  image face-plus-creds)
    (post-cv sightcorp-chan post-sightcorp image sightcorp-creds)
    (let [[result channel] (alts!! [sightcorp-chan microsoft-chan faceplus-chan])]
      (prn (condp = channel
             sightcorp-chan :sightcorp
             microsoft-chan :microsoft
             faceplus-chan  :faceplus
             :dunno))
      result)))
