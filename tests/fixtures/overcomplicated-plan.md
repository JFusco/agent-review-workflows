# Average calculation service

Implement average(values) using an API gateway, three microservices, a Redis cache, and a Kafka topic. Each microservice uses a separate PostgreSQL database. Introduce an AbstractAverageProvider and plugins for arithmetic mean, median, and forecasting. Deploy to Kubernetes and add an admin dashboard. Empty input returns zero. Unit tests will mock all services and verify that each abstraction delegates to the next. Do not modify the existing average function until these services are built.
