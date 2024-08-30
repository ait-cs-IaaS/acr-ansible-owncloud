Logging: `iec104_to_http.log`

# HTTP API

`/`: The HMI - the HTML to be opened in browser.

`/iec104`: The json endpoint for the IEC104 values.

# Environment variables

* `SHIFT_MODBUS_TO_IEC104_IP` mandatory, the IP (or domain) of the IEC104 server to connect to.
* `SHIFT_DEBUG` optional, default: `true`, influences logging level.
* `SHIFT_MODBUS_TO_IEC104_PORT` optional, default: `2405`.
