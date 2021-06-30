# Taller Internet de las Cosas

Este repositorio contiene los programas para el taller de **Internet de las Cosas** organizado en el contexto de JIT (Jóvenes, Innovación y Tecnología) el 28 de Junio de 2021 en Moreda (Asturias).

Los programas están preparados para placas **Pycom FiPy v1** y una base **PyTrack v1**.

> Ten en cuenta que las FiPy deben tener conectadas las antenas LoRa, ya que utilizan este protocolo para comunicación Pycom-a-Pycom.

Hay dos programas:

* **Sensor**: Envía de manera periódica datos leídos de su acelerómetro a través de LoRa.
* **Gateway**: Al inicializarse se conecta a una red WiFi y recibe los mensajes de _roll_ y _pitch_ que le envía el _Sensor_. El LED se ilumina con mayor o menor intensidad en función de los datos recibidos. Opcionalmente (cuando `ENABLE_WIFI=True`) las muestras recibidas de _roll_ se suben a un servicio InfluxDB a través de WiFi.
