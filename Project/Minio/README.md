# Minio

Installing Minio is quite straight forward. The following steps are based on the [Minio Quickstart Guide](https://docs.min.io/docs/minio-quickstart-guide.html).

## 📦 Installation

```  bash
wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20230923034750.0.0_amd64.deb -O minio.deb
sudo dpkg -i minio.deb
```

## 🏃‍♀️ Running Minio

Minio can manually be started with the following command:


```  bash
minio server /mnt/pachyderm/minio --console-address :9001
```

As long as the terminal is open and the defined folder exists, Minio will be running.
But to run Minio as a service, the following steps are required:

## 🚀 Running as a Systemd Service

Create a new user for Minio:

```  bash
sudo useradd -r minio-user -s /sbin/nologin
```

Create the folder for the Minio data:

``` bash
sudo mkdir -p /mnt/pachyderm/minio
```

We then create a new service file:

```  bash
sudo nano /etc/systemd/system/minio.service
```

and paste the following content:

```  bash
[Unit]
Description=Minio
Documentation=https://docs.minio.io
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
WorkingDirectory=/usr/local/

User=minio-user
Group=minio-user

ExecStart=/usr/local/bin/minio server /mnt/pachyderm/minio --console-address :9001

Restart=always
RestartSec=3
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
```

To make the service start on boot, run:

```  bash
sudo systemctl enable minio
```

To start the service, run:

```  bash
sudo systemctl start minio
```

To check the status of the service, run:

```  bash
sudo systemctl status minio
```