Pequeña aplicación de escritorio para encriptar archivos PDFs.
La misma se creó por la necesidad de automatizar el encriptado de las nóminas de las empresas con una contraseña fija. 
Se debe tomar en cuenta que para la asignación de las contraseñas, se toma en cuenta dos filas de un fichero CSV, la primera será el nombre del documento, y la segunda la contraseña que tendrá asignada. 
Esto se asignará con un mínimo de 70% de concordancia con el nombre que tenga el fichero y el que haya en el listado. 
Primeramente, se selecciona la ruta de entrada dónde se encuentren los ficheros PDFs a encriptar, seguidamente, la de salidad dónde se guardarán los ficheros que se encripten, y por último, el fichero CSV que se cargará con el listado de nombres y contraseñas. 
Una vez finalizado el proceso, se mostrará una ventana con el resultado, indicándose los documentos que han sido encriptados junto con la contraseña asignada. En caso de que hubiese algún documento que no se pudiera encriptar, se avisará también mediante una alerta por pantalla.
El fichero es posible visualizarlo y editarlo mismamente desde la propia aplicación. 
Para la interfaz gráfica se utilizado la librería de Tkinter. 
