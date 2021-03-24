#!/bin/sh
wget --output-document=100features_40minwords_20context_bigram "https://docs.google.com/uc?export=download&id=1giIEQ6Owdw5qBrPBP3rd6DQXkBUdDWQt"
wget --output-document=model_bigram.h5 "https://docs.google.com/uc?export=download&id=1GkbdFzSBWEil1e08L0CFpVLLnHwxx_A6"
wget --output-document=model_bigram.json "https://docs.google.com/uc?export=download&id=17kd-FXQ4qHwGaPaDErqRXFYZVr0aeXZg"
# wget --output-document=camemBERT_38000_state_dict.pt "https://docs.google.com/uc?export=download&id=1vXm4DPK1RPZFTItEbg39Ep6WiuZAc_vU"
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1vXm4DPK1RPZFTItEbg39Ep6WiuZAc_vU' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1vXm4DPK1RPZFTItEbg39Ep6WiuZAc_vU" --output-document=camemBERT_38000_state_dict.pt
