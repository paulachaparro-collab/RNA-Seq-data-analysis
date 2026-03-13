def descargar_metadatos_srp(srp_id: str, ruta_salida: str) -> pd.DataFrame:
    """
    Descarga los metadatos de un SRP usando pysradb y los guarda como CSV.

    Parámetros:
        srp_id (str): ID del proyecto, ej. "SRP318632"
        ruta_salida (str): Ruta absoluta o relativa del archivo CSV a guardar

    Devuelve:
        df (pd.DataFrame): DataFrame con los metadatos obtenidos
    """
    import subprocess
    import pandas as pd
    from io import StringIO

    comando = ["pysradb", "metadata", srp_id, "--desc", "--expand"]
    result = subprocess.run(comando, stdout=subprocess.PIPE, text=True)

    if result.stdout:
        output = StringIO(result.stdout)
        df = pd.read_csv(output, sep="\t")
        df.to_csv(ruta_salida, index=False)
        print(f"✅ Metadatos guardados en: {ruta_salida}")
        return df
    else:
        raise RuntimeError(f"❌ No se pudo obtener metadatos para el proyecto {srp_id}")


#en el notebook:
# Llamada a la función para descargar y guardar los metadatos
df_sra = descargar_metadatos_srp(
    srp_id="SRP318632",
    ruta_salida="/home/paula.chaparro/Documentos/tesis_2025/SRP318632_metadata.csv"
)

# Extraer lista de SRRs si lo necesitas
srr_list = df_sra["run_accession"].tolist()
display(df_sra.head())

