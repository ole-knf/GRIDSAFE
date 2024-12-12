
for j in integration-validation-bruteforce integration-validation-dos integration-validation-mitm integration-validation-physical integration-validation-recon 
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
        sudo -u wattson VBoxManage startvm "VBX1-New" --type headless;

        sleep 300s
        
        echo starting eval
        sudo -E ip netns exec w_windows /bin/bash -c "sudo /home/wattson/wattson-new/bin/python3 /home/wattson/Documents/code/main.py -n ${filename} -t 120 -p attack";
        echo finished eval
        
        echo closing IDS
        sudo -u wattson VBoxManage controlvm "VBX1-New" poweroff --type headless;
        
        echo stopping wattson
        kill $(jobs -p)
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;
        sudo /home/wattson/wattson-new/bin/python3 -m wattson /home/wattson/Documents/code/scenarios/powerowl_test/ -c;
        echo done with ${j}${i}
    done

done

sudo -E bash ./build-visualization-stationguard.sh
