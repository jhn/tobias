FROM java:8

RUN apt-get update

ADD target/tobias-0.1.0-SNAPSHOT-standalone.jar /srv/tobias.jar

CMD ["java", "-jar", "/srv/tobias.jar"]

