(ns tobias.util
  (:require [clojure.edn :as edn]))

; from http://aan.io/timing-clojure-macros/
(defmacro timed [name expr]
  (let [sym (= (type expr) clojure.lang.Symbol)]
    `(let [start# (. System (nanoTime))
           return# ~expr
           res# (if ~sym
                  (resolve '~expr)
                  (resolve (first '~expr)))]
       (prn (str "Timed "
                 (or ~name (:name (meta res#)))
                 ": " (/ (double (- (. System (nanoTime)) start#)) 1000000.0) " msecs"))
       return#)))

(defn map-values [m f]
  (reduce (fn [m' [k v]] (assoc m' k (f v))) {} m))

(defn load-config [filename]
  (edn/read-string (slurp filename)))
