
for j in suricata-industroyer-attackchain suricata-control-freeze-attackchain suricata-voltage-drift-off-attackchain suricata-disrupt-communication-attackchain suricata-recon-attackchain suricata-manipulate-grid-attackchain
do

    for i in {1..40}
    do
        echo starting ${j}
        filename="${j}${i}"
        mkdir -p /home/wattson/Documents/code/data/${filename}


        echo cleaning wattson
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;

        echo starting wattson
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ &

        sleep 120s
        echo starting IDS
        rm -rf /home/wattson/syslink/suricata
        ln -s /home/wattson/Documents/code/data/${filename} /home/wattson/syslink/suricata
        sudo systemctl start suricata.service

        sleep 300s
        
        echo starting eval
        sudo -E ip netns exec w_windows /bin/bash -c "sudo /home/wattson/wattson-new/bin/python3 /home/wattson/Documents/code/main.py -n ${filename} -t 120 -p attack -i suricata";
        echo finished eval
        
        echo closing IDS
        sudo systemctl stop suricata.service
        rm -rf /home/wattson/syslink/suricata
        ln -s /home/wattson/Documents/code /home/wattson/syslink/suricata

        echo stopping wattson
        kill $(jobs -p)
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;
        echo done with ${j}${i}
    done

done

sudo -E bash ./build-visualization-suricata.sh
