(defproject domain "0.1.0-SNAPSHOT"
  :description "CV + RTB"
  :url "http://example.com/OMGLOL"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.7.0"]
                 [ring/ring-jetty-adapter "1.4.0"]
                 [ring/ring-defaults "0.1.5"]
                 [ring/ring-json "0.4.0"]
                 [compojure "1.4.0"]
                 [clj-http "2.0.0"]
                 [org.clojure/core.async "0.2.374"]
                 [org.clojure/data.json "0.2.6"]
                 [ring-cors "0.1.7"]]
  :plugins [[lein-ring "0.9.7"]]
  :ring {:handler domain.core/app
         :nrepl {:start? true :port 3001}}
  :profiles {:dev {:jvm-opts ["-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005"]}}
  :aot [domain.core])
