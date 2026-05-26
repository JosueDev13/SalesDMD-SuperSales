


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


# Dimensión Producto

    CREATE TABLE dim_producto AS
    SELECT DISTINCT "Product" as producto_id, "Product" as nombre_producto
    FROM ventas;

# Dimensión Cliente/Segmento
    CREATE TABLE dim_segmento AS
    SELECT DISTINCT "Segment" as segmento_id, "Segment" as nombre_segmento
    FROM ventas;

# Dimensión País
    CREATE TABLE dim_pais AS
    SELECT DISTINCT "Country" as pais_id, "Country" as nombre_pais
    FROM ventas;

# Dimensión Tiempo (muy importante para OLAP)
    CREATE TABLE dim_tiempo AS
    SELECT DISTINCT 
        "Date" as fecha,
        "Month Number" as mes_numero,
        "Month Name" as mes_nombre,
        "Year" as año
    FROM ventas
    ORDER BY fecha;

# Tabla de Hechos (fact_ventas)
    CREATE TABLE fact_ventas AS
    SELECT 
        ROW_NUMBER() OVER () as venta_id,
        "Date" as fecha,
        "Product" as producto_id,
        "Segment" as segmento_id,
        "Country" as pais_id,
        "Units Sold" as unidades_vendidas,
        "Manufacturing Price" as precio_fabricacion,
        "Sale Price" as precio_venta,
        "Gross Sales" as ventas_brutas,
        "Discounts" as descuentos,
        "Sales" as ventas_netas,
        "COGS" as costo_ventas,
        "Profit" as ganancia
    FROM ventas;

