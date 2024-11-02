client_A.tls_set(ca_certs=ca_cert_path,
                 certfile=cert_file_path,
                 keyfile=key_file_path,
                 tls_version=ssl.PROTOCOL_TLSv1_2)
client_A.connect(AWS_IOT_ENDPOINT, mqtt_port, 60)