(defproject tobias "0.1.0-SNAPSHOT"
  :description "Tobias CV"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.8.0-RC3"]
                 [ring/ring-jetty-adapter "1.4.0"]
                 [ring/ring-defaults "0.1.5"]
                 [ring/ring-json "0.4.0"]
                 [compojure "1.4.0"]
                 [clj-http "2.0.0"]
                 [org.clojure/core.async "0.2.374"]
                 [org.clojure/data.json "0.2.6"]
                 [ring-cors "0.1.7"]]
  :plugins [[lein-ring "0.9.7"]]
  :global-vars {*warn-on-reflection* true}
  :ring {:handler tobias.core/app
         :nrepl {:start? true :port 3001}}
  :profiles {:dev {:jvm-opts ["-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5005"]}}
  :main tobias.core
  :aot [tobias.core])
