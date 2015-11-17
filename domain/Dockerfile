FROM java:8

RUN apt-get update

ADD target/domain-0.1.0-SNAPSHOT-standalone.jar /srv/domain.jar

CMD ["java", "-jar", "/srv/domain.jar"]

