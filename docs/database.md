RDS
===

* Input
  1. Type (PG13, PG12, MySQL5.7, MySQL8 etc)
  2. Instance type
  3. Storage
  4. Optionally, Bastion Host
  5. Optionally, read replica
  6. Optionally, proxy

* Output:
  1. RDS Instance
  2. Optionally, Bastion Host (with private key in SSM)
  3. Optionally, read replica
  4. 3 user/passwords (root, service, migration)
  5. Database URL
  6.

* Create multiple database users (one for service, one for migration)
* Create a bastion host, upload private key to SSM like CF
* CLI for accessing the database with different users
* Option to create a proxy
* Option to create a read replica

Migration
=========

When using lambda, use a custom event + custom DATABASE_URL
When using ECS, a custom job with a custom DATABASE_URL
For K8S, use a separate container (but not init) within the same deployment
