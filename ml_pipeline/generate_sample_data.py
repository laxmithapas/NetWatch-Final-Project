import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_sample_data(num_samples=5000, output_path="sample_dataset.csv"):
    np.random.seed(42)
    random.seed(42)
    
    protocols = [6, 17] # TCP, UDP
    labels = ['Benign', 'Benign', 'Benign', 'Benign', 'DDoS', 'Bot', 'Infiltration']
    
    data = []
    base_time = datetime.now() - timedelta(days=1)
    
    for i in range(num_samples):
        label = random.choice(labels)
        
        # Base benign stats
        flow_duration = int(np.random.exponential(10000))
        tot_fwd_pkts = int(np.random.lognormal(mean=1.0, sigma=0.5)) + 1
        tot_bwd_pkts = int(np.random.lognormal(mean=1.0, sigma=0.5)) + 1
        fwd_pkt_len_max = int(np.random.normal(150, 50))
        bwd_pkt_len_max = int(np.random.normal(500, 200))
        fwd_header_len = tot_fwd_pkts * 20
        bwd_header_len = tot_bwd_pkts * 20
        
        # Modify stats based on attack type to make it learnable
        if label == 'DDoS':
            tot_fwd_pkts *= 50
            fwd_pkt_len_max += 1000
            flow_duration = int(np.random.uniform(50000, 200000))
        elif label == 'Bot':
            flow_duration = int(np.random.uniform(1000, 3000))
            tot_bwd_pkts *= 10
            bwd_pkt_len_max += 500
        
        fwd_pkt_len_max = max(0, fwd_pkt_len_max)
        bwd_pkt_len_max = max(0, bwd_pkt_len_max)
            
        row = {
            'Timestamp': (base_time + timedelta(seconds=i*0.5)).strftime("%d/%m/%Y %H:%M:%S"),
            'Source IP': f"192.168.1.{random.randint(2, 254)}",
            'Destination IP': f"10.0.0.{random.randint(2, 254)}",
            'Protocol': random.choice(protocols),
            'Flow Duration': flow_duration,
            'Total Fwd Packets': tot_fwd_pkts,
            'Total Backward Packets': tot_bwd_pkts,
            'Fwd Packet Length Max': fwd_pkt_len_max,
            'Bwd Packet Length Max': bwd_pkt_len_max,
            'Fwd Header Length': fwd_header_len,
            'Bwd Header Length': bwd_header_len,
            'Label': label
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} rows in {output_path}")

if __name__ == "__main__":
    generate_sample_data(5000, os.path.join(os.path.dirname(__file__), "sample_dataset.csv"))
