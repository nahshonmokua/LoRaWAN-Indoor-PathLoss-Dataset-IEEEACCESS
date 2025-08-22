# 🛰️ LoRaWAN Indoor Path Loss Modeling with Environmental Factors 📡

This repository provides data and models for understanding **LoRaWAN signal behavior in indoor environments**, focusing on how factors like relative humidity, temperature, particulate matter, barometric pressure and CO₂ levels impact path loss and shadowing. The main goal is to optimize indoor LoRaWAN networks for smart IoT applications, enhancing both **signal reliability and network planning**.

<div align="center">
    <img src="sensor network design.png" alt="LoRaWAN Indoor Network Deployment Overview" width="70%">
</div>

---
## 🌐 Project Overview
Indoor environments present unique challenges for **LoRaWAN network performance** due to various obstacles such as walls, human activity, and environmental changes. This project provides a detailed dataset and proposes two models for predicting **path loss**:
1. **Log-Distance Path Loss Model with Multi-Wall (LDPLM-MW)**: Incorporates structural obstacles like walls for predicting signal degradation.
2. **Enhanced Log-Distance Path Loss Model with Multi-Wall and Environmental Parameters (LDPLM-MW-EP)**: Adds environmental factors (e.g., humidity, CO₂, PM2.5) to improve prediction accuracy.

These models help address **signal attenuation** in complex indoor settings, offering practical insights for IoT developers and network planners.

---

## 📊 Dataset
The dataset includes measurements of:
- **Environmental Parameters**: Temperature, humidity, CO₂, PM2.5, and pressure.
- **Signal Characteristics**: RSSI, SNR, Spreading Factor, and Time on Air.
- **Deployment Conditions**: Distance to the gateway, wall types, and transmitter power.

---

## 🛠️ Methodology
### 1. **Data Collection**
   - **Sensor Deployment**: Six end devices were strategically placed on the University of Siegen campus to capture a wide range of conditions.  
   - **Environmental Monitoring**: Measurements include CO₂ levels, humidity, temperature, and PM2.5 concentrations.
   - **Data Transmission**: The data was collected using a LoRaWAN network with transmissions to an InfluxDB database via MQTT.

### 2. **Path Loss Models**
   - **LDPLM-MW**: Considers structural walls, providing a baseline for understanding indoor signal behavior.
   - **LDPLM-MW-EP**: Enhances the baseline model by integrating **dynamic environmental factors** to account for real-time variations, significantly improving prediction accuracy in fluctuating conditions.

### 3. **Data Analysis**
   - Models are trained and validated using the dataset, with performance metrics such as **RMSE)** and **R²** to evaluate accuracy. 
   - Comparative analysis between LDPLM-MW and LDPLM-MW-EP is performed to demonstrate the improvement.

---

## 📈 Results
The results of this work have been primarily published in:

Nahshon Mokua Obiri and Kristof Van Laerhoven, [“A Comprehensive Data Description for LoRaWAN Path Loss Measurements in an Indoor Office Setting: Effects of Environmental Factors”](https://doi.org/10.1109/ACCESS.2025.3569164), *IEEE Access*, vol. 13, pp. 83148–83170, 2025.



---

## 🔍 Other Publications and Talks
- <a href="https://doi.org/10.1109/OJCOMS.2024.3484002" target="_blank">A Survey of LoRaWAN-integrated Wearable Sensor Networks for Human Activity Recognition: Applications, Challenges and Possible Solutions</a>
- Presented a light talk at the <a href="https://www.uni-siegen.de/zess/kombibox/zess_phd_forum_2024.html" target="_blank"><strong>ZESS PhD Forum 2024</strong></a>: "LoRaWAN Path Loss Measurements in an Indoor Setting, including Human and Environmental Effects."

---

## 🤝 Get Involved
🚀 **Want to collaborate?** Whether you're an IoT enthusiast, network planner, or researcher, let's connect and explore sustainable tech innovations! Connect with me <a href="https://nahshonmokua.github.io/" target="_blank">here</a>!

---

## 📝 How to Use This Repository
1. **Clone the repository**:  
   ```bash
   git clone https://github.com/nahshonmokua/LoRaWAN-Indoor-PathLoss-Dataset-IEEEACCESS.git
2. **Download the dataset** and explore the data.
3. **Run the analysis scripts** to replicate the model results or modify them for your scenarios.
4. **Contribute**: Submit pull requests to suggest improvements or new features.

---

## 📜 License
© 2025 Nahshon Mokua Obiri and Kristof Van Laerhoven. This dataset is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).

---