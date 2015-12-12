(ns tobias.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.multipart-params :refer [wrap-multipart-params]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.util.response :refer [response resource-response content-type]]
            [ring.adapter.jetty :refer [run-jetty]]
            [tobias.cv :refer [get-features]]
            [tobias.util :refer [load-config map-values]])
  (:gen-class))

(defn- hex-stream []
  (repeatedly #(format "#%06X" (rand-int 16581376))))

(defn features []
  "A map that holds features and their possible values"
  {:ethnicity [:asian :black :hispanic :white]
   :location  [:prime :average]
   :gender    [:male :female]
   :age       [:young :mid :elder]
   :weather   [:sunny :rainy]
   :clothing  (conj [] (into [] (take 3 (hex-stream))))})

(defn score-feature-set [feature-set result-set]
  "Returns an ad's feature set scored"
  ; do a set intersection between the result set and this ad's feature set to get matches
  (let [matching-features (->> (clojure.set/intersection result-set feature-set)
                               (into {}))]
    (assoc (into {} feature-set)
      :matches matching-features
      :score (count matching-features))))

(defn get-scored-ads [ads resulting-features]
  "Given a map of resulting features, computes the score for each ad feature"
  (let [result-set (set resulting-features)] ; convert to set for easy operation
    (map #(score-feature-set (set %) result-set)
         ads)))

(defn get-winning-ad [ads resulting-features]
  (let [results (get-scored-ads ads resulting-features)]
    (->> results
         (group-by :score)
         (sort)
         (last)                                             ; get the highest-scored maps
         (second)                                           ; discard score
         (rand-nth)                                         ; a random one from the group
         (assoc {} :winner)                                 ; make that the winner
         (merge {:features resulting-features}))))          ; also include the image's features

(def ads (load-config (clojure.java.io/resource "ads.edn")))

(defn run-auction [image env-features]
  (->> image
       (get-features)
       (first) ; select only one feature (possibly the one with highest confidence), should be more clever
       (merge env-features)
       (get-winning-ad ads)))

(defn random-features []
  (map-values (features) rand-nth))

(defn run-simulation [env-features]
  (let [simulated-result (merge env-features (random-features))]
    (get-winning-ad ads simulated-result)))

(defroutes app-routes
  (GET "/" [] (content-type (resource-response "index.html" {:root "public"}) "text/html"))
  (POST "/auction/new"
        {{{image :tempfile} :file} :params} (response (run-auction image {:location :prime :weather :sunny})))
  (POST "/simulation/new"
        {{{image :tempfile} :file} :params} (response (run-simulation {:location :prime :weather :sunny})))
  (route/resources "/")
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)
      (wrap-multipart-params)))

(defn -main [& args]
  (run-jetty app {:port 3000}))
