#!/bin/bash -x
set -eEuo pipefail

sut=/shared-volume/system_under_test_definition.yaml


if [ -f ${sut} ]; then
    cat ${sut}
    AMBARI_HOST=$(yq read -j ${sut} | jq  --raw-output ' .["ambari"].host')
    if [ "null" == ${AMBARI_HOST} ]; then
        AMBARI_HOST=$(yq read -j ${sut} |  jq  --raw-output '.[] | .["ambari"].host' )
    fi
fi

sed -i -e "s|AMBARI_HOST|${AMBARI_HOST}|" "ambari.cfg"
sed -i -e "s|AMBARI_USER|${AMBARI_USER:-admin}|" "ambari.cfg"
sed -i -e "s|AMBARI_PASSWORD|${AMBARI_PASSWORD:-admin}|" "ambari.cfg"

source .venv/bin/activate
pip3 install -r requirements.txt

# run the playbook passed as an argument
ansible-playbook -vv $1