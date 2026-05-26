


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


# Ventas totales por año y mes
    SELECT 
        t.año,
        t.mes_nombre,
        SUM(f.ventas_netas) as ventas_totales,
        SUM(f.unidades_vendidas) as unidades_totales,
        SUM(f.ganancia) as ganancia_total
    FROM fact_ventas f
    JOIN dim_tiempo t ON f.fecha = t.fecha
    GROUP BY t.año, t.mes_nombre, t.mes_numero
    ORDER BY t.año, t.mes_numero;

# Top 5 productos con más ganancias

    SELECT 
        p.nombre_producto,
        SUM(f.ganancia) as ganancia_total,
        SUM(f.unidades_vendidas) as unidades_vendidas
    FROM fact_ventas f
    JOIN dim_producto p ON f.producto_id = p.producto_id
    GROUP BY p.nombre_producto
    ORDER BY ganancia_total DESC
    LIMIT 5;

# Ventas por segmento de cliente y país

    SELECT 
        COALESCE(s.nombre_segmento, 'TOTAL') as segmento,
        COALESCE(p.nombre_pais, 'TOTAL') as pais,
        SUM(f.ventas_netas) as ventas_totales,
        SUM(f.ganancia) as ganancia_total
    FROM fact_ventas f
    LEFT JOIN dim_segmento s ON f.segmento_id = s.segmento_id
    LEFT JOIN dim_pais p ON f.pais_id = p.pais_id
    GROUP BY ROLLUP(s.nombre_segmento, p.nombre_pais)
    ORDER BY segmento, pais;

# Análisis de rentabilidad (Profit Margin) por producto y año
    
    SELECT 
        p.nombre_producto,
        t.año,
        SUM(f.ventas_netas) as ventas,
        SUM(f.ganancia) as ganancia,
        ROUND(100.0 * SUM(f.ganancia) / NULLIF(SUM(f.ventas_netas), 0), 2) as margen_porcentaje
    FROM fact_ventas f
    JOIN dim_producto p ON f.producto_id = p.producto_id
    JOIN dim_tiempo t ON f.fecha = t.fecha
    GROUP BY p.nombre_producto, t.año
    ORDER BY t.año, margen_porcentaje DESC;

# Comparativa de descuentos vs ventas

    SELECT 
        CASE 
            WHEN f.descuentos = 0 THEN 'Sin descuento'
            WHEN f.descuentos < 1000 THEN 'Descuento bajo'
            ELSE 'Descuento alto'
        END as categoria_descuento,
        COUNT(*) as cantidad_transacciones,
        SUM(f.ventas_netas) as ventas_totales,
        AVG(f.ganancia / NULLIF(f.unidades_vendidas, 0)) as ganancia_promedio_por_unidad
    FROM fact_ventas f
    GROUP BY categoria_descuento;




# Adicional
    
      SELECT 'dim_producto' AS tabla, COUNT(*) AS filas FROM dim_producto
      UNION ALL SELECT 'dim_segmento', COUNT(*) FROM dim_segmento
      UNION ALL SELECT 'dim_pais', COUNT(*) FROM dim_pais
      UNION ALL SELECT 'dim_tiempo', COUNT(*) FROM dim_tiempo
      UNION ALL SELECT 'fact_ventas', COUNT(*) FROM fact_ventas;

# Como un select

    DESCRIBE fact_ventas;


# Vista más detallada

    SELECT 
        column_name,
        data_type,
        is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'fact_ventas'
    ORDER BY ordinal_position;



-- ============================================
-- SCRIPT DE EXPORTACIÓN COMPLETO
-- ============================================

-- 1. Esquema
COPY (
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name LIKE 'dim_%' OR table_name = 'fact_ventas'
) TO '00_esquema_completo.csv' WITH (HEADER);

-- 2. Dimensiones
COPY dim_producto TO '01_dim_producto.csv' WITH (HEADER);
COPY dim_segmento TO '02_dim_segmento.csv' WITH (HEADER);
COPY dim_pais TO '03_dim_pais.csv' WITH (HEADER);
COPY dim_tiempo TO '04_dim_tiempo.csv' WITH (HEADER);

-- 3. Hechos
COPY fact_ventas TO '05_fact_ventas.csv' WITH (HEADER);

-- 4. Resultados de análisis
COPY (
    SELECT t.año, t.mes_nombre, SUM(f.ventas) AS ventas, SUM(f.ganancia) AS ganancia
    FROM fact_ventas f JOIN dim_tiempo t ON f.fecha = t.fecha
    GROUP BY t.año, t.mes_nombre, t.mes_num ORDER BY t.año, t.mes_num
) TO '06_analisis_ventas_mensuales.csv' WITH (HEADER);

COPY (
    SELECT p.nombre_producto, SUM(f.ganancia) AS ganancia, SUM(f.unidades) AS unidades
    FROM fact_ventas f JOIN dim_producto p ON f.id_producto = p.id_producto
    GROUP BY p.nombre_producto ORDER BY ganancia DESC LIMIT 5
) TO '07_analisis_top5_productos.csv' WITH (HEADER);

SELECT '✅ Exportación completada. Revisa los archivos CSV en tu carpeta.' AS mensaje;
