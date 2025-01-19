# :book: FanFicEpubGenerator

A Python app to automatically generate Epub files for your favorite web novels, designed to work with [calibre-web-automated](https://github.com/crocodilestick/Calibre-Web-Automated). This project can automatically download and manage your web novels in Calibre, updating them automatically as they update on your favorite site. This project can automatically download and manage your web novels in Calibre, updating them automatically as they update on your favorite site.

Currently only supports RoyalRoad.

## :rocket: Quick Start

### Prerequisites

- Docker
- Docker Compose
- A running instance of [Calibre-Web-Automated](https://github.com/crocodilestick/Calibre-Web-Automated) (recommended)

### Installation Steps

1. Get the docker-compose.yml:

   ```bash
   curl -O https://raw.githubusercontent.com/CalvesGEH/FanFicEpubGenerator/refs/heads/main/docker-compose.yml
   ```

2. Configure the downloaded `docker-compose.yml` file following the [Configuration](#:wrench:-Configuration) section.

3. Start the service:

   ```bash
   docker compose up -d
   ```

## :wrench: Configuration

### Environment Variables

#### Logging Settings

| Variable | Description | Default Value |
| --- | --- | --- |
| `LOG_LEVEL` | The level of logging in the application. See [Python Docs](https://docs.python.org/3/library/logging.html#logging-levels). | `INFO` |

#### Download Settings

| Variable | Description | Default Value |
| --- | --- | --- |
| `UPDATE_INTERVAL_MINUTES` | How often to check websites and download new chapters/follows. | `1440 (24 hrs)` |
| `MAX_NUM_THREADS` | How many threads should be used to download book chapters in parallel. This should be kept low to avoid throttling and violating terms of service. | `1` |


#### Royal Road Settings

| Variable | Description | Default Value |
| --- | --- | --- |
| `ROYAL_ROAD_DOWNLOAD_FILE` | A comma or new-line separated file of RoyalRoad fiction IDs to download. | `None` |
| `ROYAL_ROAD_DOWNLOAD_FOLLOWS` | Whether or not to login as the given user and download all followed books. | `False` |
| `ROYAL_ROAD_EMAIL`     | Your RoyalRoad email if downloading followed books. | `None` |
| `ROYAL_ROAD_PASSWORD`  | Your password for the account specified above. | `None` |

`CLOUDFLARE_PROXY_URL` is ignored if `USE_CF_BYPASS` is set to `false`

### Volume Configuration

```yaml
volumes:
  - /your/local/path:/cwa-book-ingest
```

Mount should align with your Calibre-Web-Automated ingest folder.

## :warning: Disclaimer

While it is not against RoyalRoad's terms of service to download content, it must be limited to less requests than a human would be able to do by themselves, therefore I recommend keeping the `MAX_NUM_THREADS` environment variable to one.

**I only recommend using this if you are already paying the website of your choice a premium subscription and they allow downloading. I do not condone using this app as your only way of consuming these websites since their content since most of them make their money off of ADs. Please use at your own risk and keep the artists in mind**.