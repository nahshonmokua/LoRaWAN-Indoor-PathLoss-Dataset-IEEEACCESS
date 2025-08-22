/*
 * Decoder Function for Sensor Data Payload
 *
 * This function decodes sensor data from a byte array payload received on a specific port.
 * It extracts and converts sensor values such as pressure, CO2 concentration, temperature,
 * humidity, and PM2.5 concentration, as well as a packet count for tracking message sequence.
 *
 * Parameters:
 * - bytes (Array): Array of bytes representing the sensor data payload.
 * - port (Number): The port number on which the payload was received (unused in this decoder).
 *
 * Returns:
 * - Object: An object containing the decoded sensor values and packet count.
 */
function Decoder(bytes, port) {
    // Decode sensor data from payload

    // Combine two bytes for each sensor value using bitwise operations
    var pressureInt = ((bytes[0] << 8) | bytes[1]);  // Pressure (2 bytes)
    var co2Int = ((bytes[2] << 8) | bytes[3]);       // CO2 level (2 bytes)
    var tempInt = ((bytes[4] << 8) | bytes[5]);      // Temperature (2 bytes)
    var humInt = ((bytes[6] << 8) | bytes[7]);       // Humidity (2 bytes)
    var pm25Int = ((bytes[8] << 8) | bytes[9]);      // PM2.5 value (2 bytes)

    // Combine four bytes for packet count using bitwise operations
    var packetCount = (bytes[10] << 24) | (bytes[11] << 16) | (bytes[12] << 8) | bytes[13]; // Packet count (4 bytes)

    // Convert sensor values to proper formats and handle invalid data (0xFFFF means no data)
    var pressure = (pressureInt != 0xFFFF) ? parseFloat((pressureInt / 100).toFixed(2)) : 0; // Pressure in hPa
    var co2 = (co2Int != 0xFFFF) ? co2Int : 0;  // CO2 level in ppm (no conversion needed)
    var temperature = (tempInt != 0xFFFF) ? parseFloat((tempInt / 100).toFixed(2)) : 0; // Temperature in °C
    var humidity = (humInt != 0xFFFF) ? parseFloat((humInt / 100).toFixed(2)) : 0; // Humidity in %
    var pm25 = (pm25Int != 0xFFFF) ? parseFloat((pm25Int / 100).toFixed(2)) : 0; // PM2.5 concentration (µg/m³)

    // Create an object to store the decoded sensor data
    var decoded = {
        pressure: pressure,         // Atmospheric pressure in hPa
        co2: co2,                   // CO2 concentration in ppm
        temperature: temperature,   // Temperature in °C
        humidity: humidity,         // Relative humidity in %
        pm25: pm25,                 // PM2.5 concentration in µg/m³
        packetCount: packetCount    // Packet count to track message sequence
    };

    // Return the decoded data object
    return decoded;
}
