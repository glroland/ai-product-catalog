FROM registry.access.redhat.com/ubi9/openjdk-21-runtime:1.17-2
EXPOSE 8080
WORKDIR /deployments
COPY target/ai-product-catalog-svc-1.0.0.jar /deployments
ENTRYPOINT ["java","-jar","ai-product-catalog-svc-1.0.0.jar"]
