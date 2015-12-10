(ns tobias.cv
  (:require [clj-http.client :as http]
            [clojure.data.json :as json]
            [clojure.core.async :refer [chan alts!! thread >!!]]
            [tobias.util :refer [timed load-config]])
  (:refer-clojure :exclude [name]))

(def config (load-config (clojure.java.io/resource "config.edn")))

(def microsoft-creds (:microsoft config))

(def faceplus-creds (:faceplus config))

(def sightcorp-creds (:sightcorp config))

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

(defn- extract-json-body [body]
  (json/read-str (:body body) :key-fn keyword))

(defprotocol CvProvider
  "Encapsulates a CV provider"
  (name       [this]        "The name for this provider")
  (post-image [this image]  "Posts an image")
  (normalize  [this result] "Normalizes a result"))

(def microsoft
  (reify CvProvider
    (name [_] "Microsoft")

    (post-image [_ image] (http/post (str "https://api.projectoxford.ai/face/v0/detections"
                                          "?analyzesFaceLandmarks=false"
                                          "&analyzesAge=true"
                                          "&analyzesGender=true"
                                          "&analyzesHeadPose=false")
                                     {:headers {"Content-Type" "application/octet-stream"
                                                "Ocp-Apim-Subscription-Key" (microsoft-creds :key)}
                                      :body image}))

    (normalize [_ result] (map (fn [r]
                                 {:age    (age->sym (get-in r [:attributes :age]))
                                  :gender (str->kw  (get-in r [:attributes :gender]))})
                               result))))

(def sightcorp
  (reify CvProvider
    (name [_] "Sightcorp")

    (post-image [_ image] (http/post "http://api.sightcorp.com/api/detect/"
                                     {:multipart [{:name "img" :content image}
                                                  {:name "app_key" :content (sightcorp-creds :app_key)}
                                                  {:name "client_id" :content (sightcorp-creds :client_id)}]}))

    (normalize [_ result] (map (fn [r]
                                 {:age       (age->sym (get-in r [:age :value]))
                                  :gender    (str->kw  (get-in r [:gender :value]))
                                  :ethnicity (str->kw  (get-in r [:ethnicity :value]))
                                  :clothing  (get r :clothingcolors [])})
                               (:persons result)))))

(def faceplus
  (reify CvProvider
    (name [_] "Faceplus")

    (post-image [_ image] (http/post "http://apius.faceplusplus.com/detection/detect"
                                     {:multipart [{:name "img" :content image}
                                                  {:name "api_key" :content (faceplus-creds :api_key)}
                                                  {:name "api_secret" :content (faceplus-creds :api_secret)}]}))

    (normalize [_ result] (map (fn [r]
                                 {:age    (age->sym (get-in r [:attribute :age :value]))
                                  :gender (str->kw  (get-in r [:attribute :gender :value]))})
                               (:face result)))))

(defn get-features
  "Returns a normalized response for the features in the image"
  ([image]
   (get-features image [sightcorp microsoft faceplus]))

  ([image providers]
   (let [results (map (fn [provider]
                        (thread
                          (timed
                            (name provider)
                            (->> image
                                 (post-image provider)
                                 (extract-json-body)
                                 (normalize provider)))))
                      providers)
         [first-result _] (alts!! results)]
     first-result)))
