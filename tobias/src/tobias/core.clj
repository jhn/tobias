(ns tobias.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.multipart-params :refer [wrap-multipart-params]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.middleware.cors :refer [wrap-cors]]
            [ring.util.response :refer [response resource-response content-type]]
            [ring.adapter.jetty :refer [run-jetty]]
            [tobias.cv :refer [get-features]]
            [tobias.util :refer [timed load-config]])
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
    :url       "http://www.zillowstatic.com/static/images/ad_gallery/chevy-300x250.jpg"}
   {:id        :two
    :age       :mid
    :gender    :female
    :location  :average
    :url       "http://www.fashionadexplorer.com/l-yE0JkxpIlKdLO9ot.jpg"}
   {:id        :three
    :weather   :sunny
    :gender    :male
    :age       :mid
    :url       "https://webtoolfeed.files.wordpress.com/2012/04/4bd863d620bf61.jpg"}
   {:id        :four
    :gender    :male
    :age       :old
    :location  :prime
    :url       "http://files2.coloribus.com/files/adsarchive/part_944/9449805/file/life-insurance-deck-chair-small-69163.jpg"}])

(def result-features-example
  "An example of a resulting map obtained from Tobiaz' UI and CV"
  {:location  :prime
   :ethnicity :asian
   :weather   :sunny
   :gender    :male})

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

(def ads (load-config (clojure.java.io/resource "ads.edn")))

(defn run-simulation [image env-features] (rand-nth ads))

(defroutes app-routes
  (GET "/" [] (content-type (resource-response "index.html" {:root "public"}) "text/html"))
  (POST "/auction/new"
        {{{image :tempfile} :file} :params} (response (run-auction image {:location :prime :weather :sunny})))
  (POST "/simulation/new"
        {{{image :tempfile} :file} :params} (response (run-simulation image {:location :prime :weather :sunny})))
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
