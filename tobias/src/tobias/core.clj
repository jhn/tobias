(ns tobias.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.multipart-params :refer [wrap-multipart-params]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.middleware.cors :refer [wrap-cors]]
            [ring.util.response :refer [response]]
            [ring.adapter.jetty :refer [run-jetty]]
            [tobias.cv :refer [get-features]]
            [tobias.util :refer [timed]])
  (:gen-class))

(def ads->features (atom {}))

(def features
  "A map that holds features and their possible values"
  {:ethnicity [:asian :black :hispanic :white]
   :location  [:prime :average]
   :gender    [:male :female]
   :age       [:young :mid :old]
   :weather   [:sunny :rainy]})

(def ads->features-example
  "An example of a map that holds each ad and its preferred features"
  [{:id :one
    :ethnicity :asian
    :weather   :rainy
    :location  :prime
    :age       :mid
    :gender    :male
    :url       "http://example.com/1.jpg"}
   {:id        :two
    :age       :mid
    :gender    :female
    :location  :average
    :url       "http://example.com/2.jpg"}
   {:id        :three
    :weather   :sunny
    :gender    :male
    :url       "http://example.com/3.jpg"}
   {:id        :four
    :gender    :male
    :age       :old
    :location  :prime
    :url       "http://example.com/4.jpg"}])

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
    (map #(score-feature-set (set %) result-set)
         current-ad->features)))

(defn get-winning-ad [current-features resulting-features]
  (let [results (get-scored-ads current-features resulting-features)]
    (->> results
         (sort-by :score)
         (last)
         (assoc {} :winner)
         (merge {:features resulting-features}))))

(defn run-auction [image env-features]
  (->> image
       (get-features)
       (first) ; select only one feature (possibly the one with highest confidence), should be more clever
       (merge env-features)
       (get-winning-ad ads->features-example)))

(defn run-auction2 [image env-features]
  (let [res {:foo :bar
            :gender "M"
            :url "http://cdn.playbuzz.com/cdn/0079c830-3406-4c05-a5c1-bc43e8f01479/7dd84d70-768b-492b-88f7-a6c70f2db2e9.jpg"}] res))

(defroutes app-routes
  (POST "/auction/new"
        {{{image :tempfile} :file} :params} (response (run-auction2 image {:location :prime :weather :sunny})))
  (route/resources "/")
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)
      (wrap-multipart-params)
      (wrap-cors :access-control-allow-origin [#".*"]
                 :access-control-allow-methods [:post])))

(defn -main [& args]
  (run-jetty app {:port 3000}))
