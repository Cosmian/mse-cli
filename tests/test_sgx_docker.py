"""Test model/docker.py."""


from mse_cli.core.sgx_docker import SgxDockerConfig


def test_load():
    """Test `load` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    conf = SgxDockerConfig.load(
        docker_labels={"healthcheck_endpoint": "/health", "mse-home": "1"},
        docker_attrs={
            "HostConfig": {
                "PortBindings": {
                    "443/tcp": [{"HostIp": "127.0.0.1", "HostPort": "7788"}]
                },
            },
            "Config": {
                "Cmd": [
                    "--size",
                    "4096M",
                    "--subject",
                    "CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
                    "--san",
                    "myapp.fr",
                    "--id",
                    "4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
                    "--application",
                    "app:app",
                    "--expiration",
                    "1714639412",
                ],
            },
            "Mounts": [
                {
                    "Type": "bind",
                    "Source": "/opt/cosmian-internal/cosmian-signer-key.pem",
                    "Destination": "/root/.config/gramine/enclave-key.pem",
                    "Mode": "rw",
                    "RW": True,
                    "Propagation": "rprivate",
                },
                {
                    "Type": "bind",
                    "Source": "/home/cosmian/workspace/sgx_operator/",
                    "Destination": "/opt/input",
                    "Mode": "rw",
                    "RW": True,
                    "Propagation": "rprivate",
                },
                {
                    "Type": "bind",
                    "Source": "/var/run/aesmd",
                    "Destination": "/var/run/aesmd",
                    "Mode": "rw",
                    "RW": True,
                    "Propagation": "rprivate",
                },
            ],
        },
    )

    assert conf == ref_conf


def test_labels():
    """Test `labels` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    assert ref_conf.labels() == {"mse-home": "1", "healthcheck_endpoint": "/health"}


def test_devices():
    """Test `devices` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    assert ref_conf.devices() == [
        "/dev/sgx_enclave:/dev/sgx_enclave:rw",
        "/dev/sgx_provision:/dev/sgx_provision:rw",
        "/dev/sgx/enclave:/dev/sgx/enclave:rw",
        "/dev/sgx/provision:/dev/sgx/provision:rw",
    ]


def test_ports():
    """Test `ports` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/code.tar",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    assert ref_conf.ports() == {"443/tcp": ("127.0.0.1", "7788")}


def test_volumes():
    """Test `volumes` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    assert ref_conf.volumes() == {
        "/opt/cosmian-internal/cosmian-signer-key.pem": {
            "bind": "/root/.config/gramine/enclave-key.pem",
            "mode": "rw",
        },
        "/home/cosmian/workspace/sgx_operator": {
            "bind": "/opt/input",
            "mode": "rw",
        },
        "/var/run/aesmd": {
            "bind": "/var/run/aesmd",
            "mode": "rw",
        },
    }


def test_cmd():
    """Test `cmd` function."""
    ref_conf = SgxDockerConfig(
        size=4096,
        host="127.0.0.1",
        port=7788,
        subject="CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        subject_alternative_name="myapp.fr",
        app_id="4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        expiration_date=1714639412,
        app_dir="/home/cosmian/workspace/sgx_operator/",
        application="app:app",
        healthcheck="/health",
        signer_key="/opt/cosmian-internal/cosmian-signer-key.pem",
    )

    assert ref_conf.cmd() == [
        "--size",
        "4096M",
        "--subject",
        "CN=myapp.fr,O=MyApp Company,C=FR,L=Paris,ST=Ile-de-France",
        "--san",
        "myapp.fr",
        "--id",
        "4141a3e6-1f2b-4ccf-8610-aa0891a1a210",
        "--application",
        "app:app",
        "--expiration",
        "1714639412",
    ]
