[![Build Status](https://travis-ci.org/GoogleCloudPlatform/forseti-security.svg?branch=master)](https://travis-ci.org/GoogleCloudPlatform/forseti-security) [![codecov](https://codecov.io/gh/GoogleCloudPlatform/forseti-security/branch/master/graph/badge.svg)](https://codecov.io/gh/GoogleCloudPlatform/forseti-security)

# Forseti Security
A community-driven collection of open source tools to improve the security
of your Google Cloud Platform environments.

[Get Started](http://forsetisecurity.org/docs/quickstarts/forseti-security/)
with Forseti Security.

## Contributing
We are continually improving Forseti Security and invite you to submit feature
requests and bug reports under Issues. If you would like to contribute to our
development efforts, please review our
[contributing guidelines](/.github/CONTRIBUTING.md) and submit a pull request.

### forsetisecurity.org
If you would like to contribute to forsetisecurity.org, the website and its
content are contained in the `gh-pages` branch. Visit its
[README](https://github.com/GoogleCloudPlatform/forseti-security/tree/gh-pages)
for instructions on how to make changes.

## Community
Check out our [community page](http://forsetisecurity.org/community) for ways
to engage with the Forseti Community.

## CI/CD

The Forseti application is able to deploy to a Kubernetes cluster.

### Travis CI

The Travis CI configurations in `Settings tab` at travis-ci.org/Nordstrom/forseti-security:

| **ENV VARIABLE** | **VALUE** |
|---|---|
| CLOUD_PROJECT | nordforseti |
| CLUSTER | test-cluster |
| CLUSTER_ZONE | us-central1-a |
| GCLOUD_EMAIL | [STRING] - Deprecated |
| GCLOUD_KEY | [JSON] - Deprecated |

`gcloud-service-key.json.enc`, located at root level of project, is encrypted by the Travis CI CLI. This `gcloud key` is used to deploy Forseti to the **Google Container Registry** and launch the app on a **Kubernetes** cluster.

More info on encrypting keys with the Travis CI CLI and Google can be found [here](https://cloud.google.com/solutions/continuous-delivery-with-travis-ci).

### Kubernetes Configuration

You can find the kubernetes deploy configuration at `scripts/k8s/forseti.yml`.

The Forseti Container is executed as a Kubernetes Cron Job that runs every hour. The Cloud SQL Proxy container used by Forseti to connect to the Cloud SQL server is deployed as a Kubernetes Service.

You can find more info on Cron Job configurations, [here](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/).

**Get Pod IP addresses**

```bash
$ kubectl get pods -o yaml | grep -i podip
# podIP: 10.8.1.46
```

There is probably a better way to do this, but to get things working, you get the Pod IP address of the Cloud SQL Proxy service and add that to the forseti configuration file (`/scripts/k8s/forseti.yml`) for the following environmental variable, `CLOUD_SQL_DB_HOST`. This will allow the Forseti container to connect to the forseti-security SQL database. Once set, redeploy.

### Configure Cloud SQL Proxy Container on Kubernetes

This [resource](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine) provides comprehensive instructions on how to set up the Google Cloud SQL Proxy on Kubernetes. The necessary steps from this document is to create the **Service Account User** to access the Cloud SQL database and save the credentials in the Kubernetes configuration.

**Building Forseti Docker locally:**

```bash
$ docker build -t forseti/base -f scripts/docker/base .
$ docker build -t gcr.io/nordforseti/forseti -f scripts/docker/forseti --no-cache .
```

**Deploy Locally to the Cloud:**

```bash
$ gcloud auth login
$ gcloud config set project nordforseti
$ gcloud --quiet components update kubectl
$ gcloud docker -- push gcr.io/nordforseti/forseti
$ gcloud container clusters get-credentials test-cluster --zone us-central1-a
$ kubectl apply -f scripts/k8s/forseti.yml --insecure-skip-tls-verify=true
```

**Test running locally:**

```bash
$ /scripts/run_tests.sh
```