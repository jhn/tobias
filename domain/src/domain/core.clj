(ns domain.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.util.response :refer [response]]
            [clojure.java.io :as io]
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

(defn get-scored-ads [current-ad->features resulting-features]
  "Given a map of resulting features, computes the score for each ad feature"
  ; convert the resulting feature map into a set for easy operation
  (let [result-set (set resulting-features)]
    ; updated-ad-features is the resulting map. ad is the ad id, feature-preferences is the feature-map
    (reduce (fn [updated-ad-features [ad feature-preferences]]
              ; do a set intersection between the result set and this ad's feature set to get matches
              (let [matching-features (->> (clojure.set/intersection result-set (set feature-preferences))
                                           (into {}))] ; back into a map for friendly display
                ; update ads->features with matches and scores
                (assoc updated-ad-features
                  ad
                  (assoc feature-preferences
                    :matches matching-features
                    :score (count matching-features)))))
            ; a new map to put everything in
            {}
            ; the map we want to reduce over
            current-ad->features)))

(defn get-winning-ad [current-features resulting-features]
  (let [results (get-scored-ads current-features resulting-features)]
    (->> results
         (sort-by (comp :score second))
         last)))

(defn query-cv [file-name file-path]
  (http/post "http://example.org" {:multipart [{:name file-name
                                                :content (clojure.java.io/file file-path)}]}))

(defroutes app-routes
  (GET "/" [] "OMG HI!")
  (POST "/auction/new"
    {{{tempfile :tempfile filename :filename} :img} :params :as params}
      (io/copy tempfile (io/file filename)))
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)))
