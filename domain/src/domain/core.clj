(ns domain.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.multipart-params :refer [wrap-multipart-params]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.util.response :refer [response]]
            [clj-http.client :as http])
  (:gen-class))

(def ads->features (atom {}))

(def features
  "A map that holds features and their possible values"
  {:ethnicity [:asian :black :hispanic :white]
   :location  [:prime :average]
   :gender    [:male :female]
   :age       [:young :mid :old]
   :weather   [:sunny :rainny]})

(def ads->features-example
  "An example of a map that holds each ad and its preferred features"
  {:ad1 {:ethnicity :asian
         :weather   :sunny
         :location  :prime
         :url       "http://example.com/1.jpg"}
   :ad2 {:age       :mid
         :location  :average
         :url       "http://example.com/2.jpg"}
   :ad3 {:weather   :sunny
         :url       "http://example.com/3.jpg"}
   :ad4 {:gender    :male
         :age       :old
         :location :prime
         :url       "http://example.com/4.jpg"}})

(def result-features-example
  "An example of a resulting map obtained from Tobiaz' UI and CV"
  {:location  :prime
   :ethnicity :asian
   :weather   :sunny
   :gender    :male})

; Maybe we can add this information to the resulting response
(def advertisers->ads
  "A map that holds ads per advertiser"
  {:advertiser1 #{:ad1 :ad2}
   :advertiser2 #{:ad3}
   :advertiser3 #{:ad4}})

(defn score-feature-set [feature-set result-set]
  "Returns an ad's feature set scored"
  ; do a set intersection between the result set and this ad's feature set to get matches
  (let [matching-features (->> (clojure.set/intersection result-set feature-set)
                               (into {}))]
    (assoc (into {} feature-set)
      :matches matching-features
      :score (count matching-features))))

(defn get-scored-ads [current-ad->features resulting-features]
  "Given a map of resulting features, computes the score for each ad feature"
  (let [result-set (set resulting-features)] ; convert to set for easy operation
    (reduce (fn [scored-ad-features [ad ad-features]]
              (let [scored-features (score-feature-set (set ad-features) result-set)]
                (assoc scored-ad-features ad scored-features)))
            {}
            current-ad->features)))

(defn get-winning-ad [current-features resulting-features]
  (let [results (get-scored-ads current-features resulting-features)]
    (->> results
         (sort-by (comp :score second))
         last)))

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


(defroutes app-routes
  (GET "/" [] "OMG HI!")
  (POST "/auction/new"
        {{{tempfile :tempfile} :file} :params} (handle-file-microsoft tempfile microsoft-creds))
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)
      (wrap-multipart-params)))
