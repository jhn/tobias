(ns tobias.cv
  (:require [clj-http.client :as http]
            [clojure.data.json :as json]
            [clojure.core.async :refer [chan alts!! thread >!!]]
            [tobias.util :refer [timed load-config]]))

(def config (load-config (clojure.java.io/resource "config.edn")))

(def microsoft-creds (:microsoft config))

(def faceplus-creds (:faceplus config))

(def sightcorp-creds (:sightcorp config))

(defn post-sightcorp [tempfile creds]
  (http/post "http://api.sightcorp.com/api/detect/"
             {:multipart [{:name "img" :content tempfile}
                          {:name "app_key" :content (creds :app_key)}
                          {:name "client_id" :content (creds :client_id)}]}))

(defn post-microsoft [tempfile creds]
  (http/post (str "https://api.projectoxford.ai/face/v0/detections"
                  "?analyzesFaceLandmarks=false"
                  "&analyzesAge=true"
                  "&analyzesGender=true"
                  "&analyzesHeadPose=false")
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
   image                              ; image on which to run cv
   creds]                             ; creds for the cv api
  (thread                             ; gets its own thread because we're blocking
    (let [res (timed (f image creds))]        ; call f to POST
      (>!! c (json/read-str (:body res) :key-fn keyword))))) ; parse result as json, put it in c

(defn- age->sym [n]
  (let [age (if (string? n)
              (Integer/parseInt n)
              n)]
    (cond
      (>= age 50) :old
      (>= age 30) :mid
      :else       :young)))

(defn- str->kw [str]
  (-> str (.toLowerCase) (keyword)))


(defn normalize-sightcorp [result]
  (map (fn [r]
         {:age       (age->sym (get-in r [:age :value]))
          :gender    (str->kw  (get-in r [:gender :value]))
          :ethnicity (str->kw  (get-in r [:ethnicity :value]))})
       (:persons result)))

(defn normalize-microsoft [result]
  (map (fn [r]
         {:age    (age->sym (get-in r [:attributes :age]))
          :gender (str->kw  (get-in r [:attributes :gender]))})
       result))

(defn normalize-faceplus [result]
  (map (fn [r]
         {:age    (age->sym (get-in r [:attribute :age :value]))
          :gender (str->kw  (get-in r [:attribute :gender :value]))})
       (:face result)))

(defn get-features
  "Returns a normalized response for the features in the image"
  [image]
  (let [sightcorp-chan (chan)
        microsoft-chan (chan)
        faceplus-chan  (chan)]
    (post-cv microsoft-chan post-microsoft image microsoft-creds)
    (post-cv faceplus-chan  post-faceplus  image faceplus-creds)
    (post-cv sightcorp-chan post-sightcorp image sightcorp-creds)
    (let [[result channel] (alts!! [sightcorp-chan microsoft-chan faceplus-chan])]
      (condp = channel
             sightcorp-chan :>> (fn [_] (prn :sightcorp) (normalize-sightcorp result))
             microsoft-chan :>> (fn [_] (prn :microsoft) (normalize-microsoft result))
             faceplus-chan  :>> (fn [_] (prn :faceplus)  (normalize-faceplus result))
             :dunno))))
