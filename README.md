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