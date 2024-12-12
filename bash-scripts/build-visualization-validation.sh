
for j in integration-validation-bruteforce integration-validation-dos integration-validation-mitm integration-validation-physical integration-validation-recon
do
    for i in {1..20}
    do
        filename="${j}${i}"
        sudo /home/wattson/wattson-new/bin/python3 /home/wattson/Documents/code/main.py -n ${filename} -t 120 -p eval -v -m all -i suricata;
        echo finished $filename

    done

    cd ../data-summary
    sudo -E /home/wattson/wattson-new/bin/python3 summary.py ${j} 1 20
    cd ../bash-scripts

done

cd ../data-summary

# get summarys of individual attacks
for j in integration-validation-bruteforce integration-validation-dos integration-validation-mitm integration-validation-physical integration-validation-recon
do
    for i in {0..5} #there are at most 5 attacks per attack chain
    do
        sudo -E /home/wattson/wattson-new/bin/python3 summary.py ${j} 1 20 attack${i}-
    done
    
done

