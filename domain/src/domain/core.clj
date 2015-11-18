(ns domain.core
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.json :refer [wrap-json-body wrap-json-response]]
            [ring.util.response :refer [response]])
  (:gen-class))

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
  "Given a map of resulting features, compute the score for the features preferences set to each ad"
  ; we'll reduce over our current ads-features map assigning a score to it
  ; updated-ads-feature is the resulting map. ad is the ad id, feature-preferences is the feature-map
  (reduce (fn [updated-ads->feature [ad feature-preferences]]
            ; we only care about feature-map entries whose keys appear in the resulting map. select these.
            (let [matching-features (select-keys
                                      feature-preferences
                                      (keys resulting-features))
                  ; now comes the juicy part.
                  ; we'll reduce each feature-map to a single score for that map.
                  matching-features-score (reduce-kv
                                            ; init score is 0, (k v) is the current map entry
                                            (fn [init k v]
                                              ; check if the value of this feature and the
                                              ; value of the resulting feature match up
                                              (if (= v (resulting-features k))
                                                ; if so, increment the score
                                                (inc init)
                                                ; or just pass it along
                                                init))
                                            ; score starts at zero
                                            0
                                            ; the entry we're reducing over
                                            matching-features)]
              ; finally, put ads->features back together
              (assoc updated-ads->feature
                ; by associating the ad
                ad
                ; with the an extra entry that contains the score for that feature
                (assoc feature-preferences :score matching-features-score))))
          ; a new map to put everything in
          {}
          ; the map we want to reduce over
          current-ad->features))

(defroutes app-routes
  (GET "/" [] "OMG HI!")
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)))
