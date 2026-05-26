


# Instalar una herramienta para conversión

    brew install csvkit

#  Convertir el archivo XLSX a CSV

    in2csv "Supersales DMD941.xlsx" > ventas12.csv

# Verificar el documento
    head -5 ventas.csv


# Instalamos DuckDB

    brew install duckdb

# Crear carpeta del proyecto

    mkdir desafio-olap-dmd941
    cd desafio-olap-dmd941
    
# Ejecutamos duckdb 
    
    duckdb ventas.db

# Crear la tabla de hechos

    CREATE OR REPLACE TABLE ventas AS 
    SELECT * FROM read_csv_auto('Supersales_DMD941.csv');

# Verificar que se cargó bien

    SELECT COUNT(*) FROM ventas;
    SELECT * FROM ventas LIMIT 10;
