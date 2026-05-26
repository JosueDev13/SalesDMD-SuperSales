


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


# Extraer y cargar los datos (ETL)

# Verificar datos nulos
    SELECT 
        SUM(CASE WHEN "Units Sold" IS NULL THEN 1 ELSE 0 END) as null_units,
        SUM(CASE WHEN "Sales" IS NULL THEN 1 ELSE 0 END) as null_sales,
        SUM(CASE WHEN "Profit" IS NULL THEN 1 ELSE 0 END) as null_profit
    FROM ventas;

# Verificar el rango de fechas

    SELECT MIN(Date) as fecha_inicio, MAX(Date) as fecha_fin FROM ventas;

# Verificar si hay profits negativos.

    SELECT COUNT(*) as perdidas FROM ventas WHERE "Profit" < 0;


