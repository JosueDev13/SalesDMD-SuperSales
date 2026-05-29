# exportar_reportes.py
import duckdb

conn = duckdb.connect('ventas.db')

# Lista de tus consultas
reportes = [
    ("VENTAS_POR_MES", """
        SELECT t.año, t.mes_nombre, 
               SUM(f.ventas_netas) as ventas_totales,
               SUM(f.ganancia) as ganancia_total
        FROM fact_ventas f
        JOIN dim_tiempo t ON f.fecha = t.fecha
        GROUP BY t.año, t.mes_nombre, t.mes_numero
        ORDER BY t.año, t.mes_numero
    """),
    
    ("TOP_5_PRODUCTOS", """
        SELECT p.nombre_producto, 
               SUM(f.ganancia) as ganancia_total,
               SUM(f.unidades_vendidas) as unidades_vendidas
        FROM fact_ventas f 
        JOIN dim_producto p ON f.producto_id = p.producto_id
        GROUP BY p.nombre_producto 
        ORDER BY ganancia_total DESC 
        LIMIT 5
    """)
]

# Unir todos en un solo DataFrame
import pandas as pd
df_final = pd.DataFrame()

for nombre, consulta in reportes:
    df = conn.execute(consulta).fetchdf()
    df.insert(0, 'reporte', nombre)
    df_final = pd.concat([df_final, df, pd.DataFrame([['---'] * len(df.columns)], columns=df.columns)])

# Exportar a CSV
df_final.to_csv('todos_reportes.csv', index=False)
print("✅ Exportado a 'todos_reportes.csv'")

conn.close()