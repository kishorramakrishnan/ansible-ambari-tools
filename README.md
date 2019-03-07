Wire encryption for HDF/HDP
===========================


How To run
----------
1. Create an ini-like file: `Ambari.cfg`
    ```
    [default]
    url = http://{ambari_host}:8080
    user = admin
    password = admin
    ```
    **Note:** 
    The url cannot contain context-path/ingress, as it is not supported by underlying `python-ambariclient`.
    Neither should it contain a trailing slash as Ambari API calls seem to be picky about them.
    
2. Create a virtualenv and install the requirements into it.
    ```
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
    
3. Execute
    ```
    ansible-playbook  main.yaml --private-key  /path/to/private-key
    ```
    where `private-key` is the key you could use to ssh into the nodes of your cluster.


Inventory
---------
A dynamic inventory script is fetching hosts and component mappings from ambari. 
To target your playbook against hosts that belong to such groups, use: 

 
    ---
    - hosts: KAFKA_BROKER
    
Where the group name is the name of the component in Ambari. 
* METRICS_COLLECTOR
* METRICS_MONITOR
* NIFI_MASTER
* NIFI_CA
* INFRA_SOLR
* KAFKA_BROKER
* ZOOKEEPER_SERVER
* ZOOKEEPER_CLIENT
* REGISTRY_SERVER

To get a picture, what the hosts / mappings are like, run 

    inventory/ambari.py | jq .



How to wire encrypt a new component
-----------------------------------

Take a look at `component_accumulo.yaml` and `component_kafka.yaml` to get inspiration on how to set the generated certs/key/trust -stores onto your component's config.


#### How QAAS handles WE - SSL setup

- All service configurations for SSL setup is added in the blueprints (Except few components like Atlas)
- As part of pre-ambari-setup recipes trigger the setup of SSL certificates (Details in next section)
- Start deploys
- Any additional configurations / certificate generation (e.g Atlas) will be done as part of the post-install-recipes and do required service restarts

##### SSL certificate generation

- Setup a local root CA. Create a secure private directory for the same. You can copy the ca.crt file to all directories required. But ca.key should be kept secure
    ```
    openssl req -new -x509 -sha256 -newkey "rsa:2048" -subj "/C=US/ST=CA/L=Santa Clara/O=Hortonworks/OU=Engineering/CN=ctr-e139-1542663976389-78943-01-000004.hwx.site" -keyout ca.key -out ca.crt -days 365 -passin "pass:changeit" -passout "pass:changeit"
    ```
    - Outputs ca.crt (certificate) and ca.key(private key)
- Create keypair ( a private key and keystore for per service
    ``` 
    keytool -genkeypair
      -alias <hostname>
      -dname "CN=<hostname>"
      -keystore certs.jks
      -keypass changeit
      -storepass changeit
      -keyalg RSA
      -sigalg SHA256withRSA
      -keysize 2048
      -ext "SAN=dns:<hostname>"

    ```
- Create a certificate signing request for each service (CSR). This should be done for every host every service
    ```
     keytool -certreq
      -alias <certs_local_alias | hostname>
      -file certs.req
      -keystore certs.jks
      -keypass changeit
      -storepass changeit
      -ext "SAN=dns:<hostname>"

    ```
    - Create a config file for the csr (san_config.cnf)
    Example content
    ```
    [req]
    distinguished_name = req_distinguished_name
    req_extensions     = v3_req
    x509_extensions    = v3_req
    copy_extensions = copy
    default_md = sha256
    
    
    [req_distinguished_name]
    commonName       = <hostname>
    
    {% if OU is defined %}
    organizationalUnitName = Engineering
    {% endif %}
    
    {% if O is defined %}
    organizationName       = Hortonworks
    {% endif %}
    
    {% if L is defined %}
    localityName           = Santa Clara
    {% endif %}
    
    {% if ST is defined %}
    stateOrProvinceName    = CA
    {% endif %}
    
    {% if C is defined %}
    countryName      = US
    {% endif %}
    
    [v3_req]
    # The extentions to add to a self-signed cert
    subjectAltName       = @alt_names
    
    [alt_names]
    DNS.1 = <hostname>
    ```
- Sign the certificate using the self signed root CA cert. Make sure to sign all service certs generated using this step
    ```
     openssl x509
      -req
      -in certs.req
      -out certs.crt
      -days 365
      -CA ca.crt
      -CAkey ca.key
      -CAcreateserial
      -passin "pass:changeit"
      -extensions v3_req
      -extfile san_config.cnf
    ```
- Copy all .crt/.certs/.jks files to all hosts with right set of permissions

- Import CA cert and service cert to the truststore to your service certs.jks keystore
    ```
    keytool -import
      -keystore certs.jks
      -alias rootca
      -file ca.crt
      -keypass changeit
      -storepass changeit
      -noprompt
    ```
- Import CA cert to java cacerttrusstore as Ranger uses the that as the truststore. This is for Ambari and Ranger. You can find java_home from /etc/ambari-server/conf/ambari.properties
    ```
    keytool -import
      -keystore <java_home>/jre/lib/security/cacerts
      -alias rootca
      -file ca.crt
      -keypass changeit
      -storepass changeit
      -noprompt
    ```