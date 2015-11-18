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

(defroutes app-routes
  (GET "/status" [] "OMG HI!")
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-json-body {:keywords? true})
      (wrap-json-response)))
