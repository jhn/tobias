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

(def features
  "A map that holds features and their possible values"
  {:ethnicity [:asian :black :hispanic :white]
   :location  [:prime :average]
   :gender    [:male :female]
   :age       [:young :mid :old]
   :weather   [:sunny :rainy]})

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
         (group-by :score)
         (sort)
         (last)
         (second)
         (rand-nth)
         (assoc {} :winner)
         (merge {:features resulting-features}))))

(def ads (load-config (clojure.java.io/resource "ads.edn")))

(defn run-auction [image env-features]
  (->> image
       (get-features)
       (first) ; select only one feature (possibly the one with highest confidence), should be more clever
       (merge env-features)
       (get-winning-ad ads)))

(defn map-values [m f]
  (reduce (fn [m' [k v]] (assoc m' k (f v))) {} m))

(defn run-simulation []
  (let [winner-ad (rand-nth ads)]
    {:winner winner-ad
     :features (->> (map-values features rand-nth)
                    (merge (select-keys winner-ad [:age :gender])))})) ; merge with winner's age/gender

(defroutes app-routes
  (GET "/" [] (content-type (resource-response "index.html" {:root "public"}) "text/html"))
  (POST "/auction/new"
        {{{image :tempfile} :file} :params} (response (run-auction image {:location :prime :weather :sunny})))
  (POST "/simulation/new"
        {{{image :tempfile} :file} :params} (response (run-simulation)))
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
