(ns tobias.cv
  (:require [clj-http.client :as http]
            [clojure.data.json :as json]
            [clojure.core.async :as async]
            [tobias.util :refer [timed load-config]])
  (:refer-clojure :exclude [name]))

(def config (load-config (clojure.java.io/resource "config.edn")))

(def microsoft-creds (:microsoft config))

(def sightcorp-creds (:sightcorp config))

(defn- age->sym [n]
  (let [age (if (string? n)
              (Integer/parseInt n)
              n)]
    (cond
      (>= age 50) :elder
      (>= age 30) :mid
      :else       :young)))

(defn- str->kw [str]
  (-> str (.toLowerCase) (keyword)))

(defn- extract-json-body [body]
  (json/read-str (:body body) :key-fn keyword))

(defprotocol CvProvider
  (name      [this])
  (features  [this image])
  (normalize [this result]))

(def microsoft
  (reify CvProvider
    (name [_] "Microsoft")
    (features [_ image]
      (http/post (str "https://api.projectoxford.ai/face/v1.0/detect"
                      "?returnFaceId=false"
                      "&returnFaceAttributes=age,gender")
                 {:headers {"Content-Type" "application/octet-stream"
                            "Ocp-Apim-Subscription-Key" (:key microsoft-creds)}
                  :body image}))
    (normalize [_ result]
      (map (fn [r]
             {:age    (age->sym (get-in r [:faceAttributes :age]))
              :gender (str->kw  (get-in r [:faceAttributes :gender]))})
           result))))

(def sightcorp
  (reify CvProvider
    (name [_] "Sightcorp")
    (features [_ image]
      (http/post "http://api.sightcorp.com/api/detect/"
                 {:multipart [{:name "img" :content image}
                              {:name "app_key" :content (:app_key sightcorp-creds)}
                              {:name "client_id" :content (:client_id sightcorp-creds)}]}))
    (normalize [_ result]
      (map (fn [r]
             {:ethnicity (str->kw  (get-in r [:ethnicity :value]))
              :clothing  (get r :clothingcolors [])})
           (:persons result)))))

(defn get-features
  "Returns a normalized response for the features in the image"
  ([image]
   (get-features image [sightcorp microsoft]))
  ([image providers]
   (let [timed-features (fn [provider]
                          (async/thread
                            (timed (name provider)
                                   (->> image
                                        (features provider)
                                        (extract-json-body)
                                        (normalize provider)))))]
     (->> providers
          (map timed-features)      ; do the call
          (async/merge)             ; merge into single channel
          (vector)                  ; put channel into vector for mapping
          (async/map first)         ; only get the first person from each result if multiple
          (async/reduce merge {})   ; merge results
          (async/into [])           ; conj results into vector
          (async/<!!)))))
