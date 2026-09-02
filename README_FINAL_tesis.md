# Workflow bioinformático de RNA-seq en Python

## Descripción

Este repositorio contiene el workflow desarrollado para el proyecto:

**"Workflow bioinformático de RNASeq en Python: Optimización de
herramientas disponibles y retos para el análisis de datos
bioinformáticos de RNASeq".**

El pipeline está orientado al procesamiento de datos de RNA-seq
paired-end en Linux mediante Python y herramientas bioinformáticas
externas. El flujo incluye recuperación de metadatos, descarga de
lecturas, control de calidad, trimming, alineamiento, procesamiento de
BAM, anotación, cuantificación génica y preparación de los conteos para
análisis estadístico con PyDESeq2.

Debido a las limitaciones de almacenamiento y memoria RAM del entorno
computacional, las etapas de mayor demanda se han planteado para
validación computacional utilizando las dos primeras corridas del
conjunto de datos y procesándolas secuencialmente. Esta estrategia
permite comprobar la integración del workflow sin considerar el
subconjunto como sustituto del conjunto completo para inferencia
biológica.

------------------------------------------------------------------------

## 1. Arquitectura del proyecto

``` text
tesis_2025/
├── data/
│   ├── annotation/
│   ├── raw/
│   ├── reference_genome/
│   └── processed/
│       ├── 01.quality_control/
│       ├── 02.trimmed/
│       └── 03.alignment/
├── code/
│   └── tesis.ipynb
├── results/
├── tmp/
├── environment.yml
├── README.md
└── METADATA.txt
```

### Directorios principales

-   `data/raw/`: archivos FASTQ originales.
-   `data/processed/01.quality_control/`: informes de control de
    calidad.
-   `data/processed/02.trimmed/`: FASTQ después del trimming.
-   `data/processed/03.alignment/`: BAM y archivos asociados al
    alineamiento.
-   `data/reference_genome/`: genoma de referencia e índices.
-   `data/annotation/`: anotación génica GTF.
-   `code/`: notebook y código del workflow.
-   `results/`: matrices, tablas y resultados derivados.
-   `tmp/`: archivos temporales generados durante etapas de
    procesamiento.

> Los nombres de los directorios deben mantenerse consistentes con las
> rutas utilizadas en el notebook.

------------------------------------------------------------------------

## 2. Entorno computacional

El workflow se ejecuta en Linux utilizando un entorno Conda denominado
`env_tesis`.

### Crear el entorno desde el archivo YAML

``` bash
conda env create -f environment.yml
```

### Activar el entorno

``` bash
conda activate env_tesis
```

### Comprobar Python

``` bash
which python
python --version
```

La versión utilizada durante el desarrollo es Python 3.11.13.

### Inspeccionar el entorno

``` bash
conda env list
conda list
```

### Comprobar dependencias instaladas mediante pip

``` bash
python -m pip --version
python -m pip check
```

Si `pip check` informa dependencias faltantes o incompatibles, se
recomienda resolverlas antes de incorporar nuevas herramientas al
entorno.

------------------------------------------------------------------------

## 3. Gestión y optimización del almacenamiento

La disponibilidad de almacenamiento debe comprobarse especialmente
después de instalar o actualizar el entorno y antes de iniciar etapas
que generen archivos FASTQ o BAM de gran tamaño.

### Comprobar espacio disponible

``` bash
df -h /home/paula.chaparro
```

### Comprobar tamaño de la caché de Conda

``` bash
du -sh /home/paula.chaparro/miniconda3/pkgs
```

### Simular la limpieza de Conda

Antes de eliminar archivos se recomienda realizar una simulación:

``` bash
conda clean --all --dry-run
```

### Limpiar la caché

Una vez verificado que el entorno funciona:

``` bash
conda clean --all
```

La limpieza de la caché debe considerarse una operación de mantenimiento
y no una etapa automática del análisis. No se recomienda borrar
manualmente `miniconda3/pkgs`.

### Momentos recomendados para comprobar recursos

1.  Después de crear y verificar el entorno desde `environment.yml`.
2.  Antes de descargar grandes volúmenes de FASTQ.
3.  Antes del alineamiento y procesamiento de BAM.
4.  Cuando una instalación falle y exista sospecha de falta de
    almacenamiento.
5.  Después de finalizar etapas que generen archivos temporales o
    intermediarios grandes.

Durante el desarrollo se observó que la caché de Conda podía ocupar una
fracción considerable del almacenamiento disponible, por lo que su
monitorización forma parte de la estrategia de optimización de recursos.

------------------------------------------------------------------------

## 4. Datos utilizados para la validación del workflow

El conjunto de datos seleccionado corresponde al estudio:

-   GEO: `GSE173955`
-   BioProject: `PRJNA727602`
-   SRA Study: `SRP318632`
-   Organismo: *Homo sapiens*
-   Plataforma: Illumina HiSeq 1500
-   Diseño de biblioteca: paired-end, TruSeq Stranded mRNA

El estudio contiene muestras de enfermedad de Alzheimer (AD) y controles
non-AD.

### Subconjunto de validación

Para las etapas de mayor demanda computacional se utilizan las dos
primeras corridas:

``` python
test_srr_list = srr_list[:2]
```

Las corridas deben procesarse secuencialmente para limitar el uso
simultáneo de RAM y almacenamiento.

> Este subconjunto se utiliza para validar técnicamente el pipeline. No
> debe interpretarse como un diseño suficiente para realizar inferencia
> estadística robusta de expresión diferencial.

------------------------------------------------------------------------

## 5. Recuperación de metadatos

Los metadatos del estudio SRA se recuperan mediante `pysradb`.

Ejemplo:

``` bash
pysradb metadata SRP318632 --desc --expand
```

En el notebook, la salida se procesa con pandas y se conserva como
archivo CSV. La columna `run_accession` se utiliza para construir la
lista de corridas (`srr_list`).

Los metadatos también se utilizan posteriormente para relacionar las
corridas con las muestras biológicas y con las condiciones
experimentales AD y non-AD.

------------------------------------------------------------------------

## 6. Descarga de las lecturas

Las corridas de SRA se descargan mediante SRA Toolkit.

Herramientas principales:

``` bash
prefetch
fasterq-dump
```

Para datos paired-end, la conversión se realiza con:

``` bash
fasterq-dump --split-files
```

Los FASTQ resultantes se almacenan en:

``` text
data/raw/
```

Se utiliza un directorio temporal controlado cuando es necesario y se
eliminan archivos temporales o SRA intermedios después de comprobar la
generación correcta de los FASTQ.

------------------------------------------------------------------------

## 7. Control de calidad inicial

El control de calidad de las lecturas originales se realiza con FastQC.

Los informes se almacenan en:

``` text
data/processed/01.quality_control/
```

La presencia de un FASTQ no constituye por sí sola una comprobación de
calidad; los informes FastQC permiten evaluar características como
calidad por base, contenido de adaptadores y distribución de las
lecturas.

------------------------------------------------------------------------

## 8. Trimming

Las lecturas se procesan mediante `fastp`.

Los FASTQ resultantes se almacenan en:

``` text
data/processed/02.trimmed/
```

La nomenclatura utilizada es:

``` text
SRRXXXXXXX_1.trimmed.fastq
SRRXXXXXXX_2.trimmed.fastq
```

Después del trimming se ejecuta nuevamente FastQC sobre los archivos
procesados.

------------------------------------------------------------------------

## 9. Consolidación del control de calidad

Los informes FastQC posteriores al trimming se consolidan mediante
MultiQC.

Versión utilizada durante el desarrollo:

``` text
MultiQC 1.35
```

Se recomienda generar un informe MultiQC final centrado en los
resultados posteriores al trimming, evitando mezclar de manera no
controlada informes pre- y post-trimming.

Para verificar la instalación:

``` bash
multiqc --version
```

También puede comprobarse la consistencia de las dependencias Python
mediante:

``` bash
python -m pip check
```

------------------------------------------------------------------------

## 10. Genoma de referencia

El alineamiento se realiza contra el genoma humano GRCh38 utilizando un
índice preconstruido de HISAT2.

Directorio esperado:

``` text
data/reference_genome/grch38/
```

Prefijo utilizado por HISAT2:

``` text
data/reference_genome/grch38/genome
```

Antes del alineamiento se debe comprobar que los archivos del índice
están presentes.

------------------------------------------------------------------------

## 11. Alineamiento con HISAT2

Herramienta:

``` text
HISAT2 2.2.1
```

El alineamiento utiliza las lecturas paired-end procesadas.

Parámetros empleados en el workflow incluyen:

``` text
-k 1
--dta
-p 4
```

Cada corrida genera un resumen independiente de HISAT2.

Los alineamientos se transmiten directamente hacia Samtools mediante una
tubería (`pipe`), evitando generar un archivo SAM intermedio de gran
tamaño. Esta decisión reduce el consumo de almacenamiento.

------------------------------------------------------------------------

## 12. Conversión y ordenamiento con Samtools

Herramienta:

``` text
Samtools 1.22.1
```

La salida de HISAT2 se recibe directamente mediante `stdin` y se ordena
para generar:

``` text
SRRXXXXXXX.sorted.bam
```

Los BAM se almacenan en:

``` text
data/processed/03.alignment/
```

Debido a las restricciones de memoria, se recomienda limitar los hilos y
la memoria utilizada por `samtools sort`. Las corridas se procesan de
manera secuencial.

Cuando una tubería HISAT2 → Samtools falla, debe revisarse primero el
error producido por `samtools sort`, ya que un cierre de la tubería
puede provocar posteriormente un error `SIGPIPE` en HISAT2.

------------------------------------------------------------------------

## 13. Marcaje de posibles duplicados

Los posibles duplicados se procesan mediante Samtools siguiendo la
secuencia:

``` text
sort por nombre
      ↓
fixmate -m
      ↓
sort por coordenadas
      ↓
markdup
```

El workflow utiliza recursos limitados en las etapas de ordenamiento,
por ejemplo:

``` text
2 hilos
768 MB por hilo
```

Los duplicados se **marcan**, no se eliminan.

Archivo final:

``` text
SRRXXXXXXX.marked_duplicates.bam
```

Archivo de estadísticas:

``` text
SRRXXXXXXX.markdup_metrics.txt
```

Después de comprobar que el BAM final se generó correctamente, los BAM
temporales utilizados exclusivamente durante `fixmate` y `markdup`
pueden eliminarse para recuperar almacenamiento.

Los BAM originales producidos en la etapa anterior no deben eliminarse
automáticamente.

------------------------------------------------------------------------

## 14. Anotación genómica

La anotación seleccionada corresponde a:

``` text
GENCODE Human Release 50
GRCh38.p14
gencode.v50.annotation.gtf
```

El archivo se almacena en:

``` text
data/annotation/
```

El GTF se descarga comprimido desde GENCODE y posteriormente se
descomprime mediante Python.

Un único archivo GTF es compartido por todas las corridas analizadas.

------------------------------------------------------------------------

## 15. Compatibilidad BAM-GTF

Antes de cuantificar se comprueba la compatibilidad entre los nombres de
las secuencias presentes en los BAM y los cromosomas/contigs presentes
en la anotación GTF.

Esta comprobación permite detectar incompatibilidades de nomenclatura
antes de ejecutar featureCounts.

La coincidencia de nombres de secuencia no sustituye la verificación de
que genoma y anotación correspondan al ensamblaje de referencia
seleccionado.

------------------------------------------------------------------------

## 16. Cuantificación génica con featureCounts

La cuantificación se realiza sobre los BAM finales marcados mediante
`featureCounts`.

Configuración principal:

``` text
-t exon
-g gene_id
-p
--countReadPairs
-s 2
-T 4
```

La opción `-s 2` corresponde al tratamiento reverse-stranded utilizado
para las bibliotecas TruSeq Stranded mRNA del conjunto de datos.

Los duplicados marcados no se excluyen de la cuantificación; por tanto,
no se utiliza:

``` text
--ignoreDup
```

Salida principal:

``` text
results/featureCounts_counts.txt
```

featureCounts genera además un archivo de resumen de asignación:

``` text
results/featureCounts_counts.txt.summary
```

Los conteos se mantienen como valores enteros crudos.

------------------------------------------------------------------------

## 17. Construcción de la matriz de conteos

La salida de featureCounts contiene columnas de anotación y columnas de
conteos.

Las columnas:

``` text
Geneid
Chr
Start
End
Strand
Length
```

se separan de los conteos para construir una matriz:

``` text
genes × muestras
```

La matriz se guarda como:

``` text
results/raw_counts_matrix.csv
```

Los nombres de los BAM se simplifican para conservar el identificador de
la corrida como nombre de muestra.

------------------------------------------------------------------------

## 18. Filtrado de genes con baja expresión

Para la validación computacional con dos corridas se aplica un filtro
permisivo:

``` text
≥ 10 conteos en al menos una corrida
```

La matriz filtrada se conserva como:

``` text
results/filtered_counts_matrix.csv
```

Este criterio está diseñado para la validación técnica con un
subconjunto pequeño y deberá revisarse cuando se realice el análisis
sobre el conjunto completo de muestras biológicas.

------------------------------------------------------------------------

## 19. Preparación de metadatos

Las muestras presentes en la matriz de conteos se relacionan con los
metadatos recuperados previamente mediante `run_accession`.

Antes del análisis estadístico debe comprobarse que:

-   todas las muestras de la matriz tienen metadatos;
-   el orden de las muestras es consistente;
-   cada corrida está correctamente relacionada con su muestra
    biológica;
-   la condición experimental está correctamente identificada.

Las condiciones utilizadas son:

``` text
AD
non_AD
```

No deben asignarse condiciones experimentales manualmente sin verificar
previamente los metadatos.

### Corridas técnicas

El conjunto completo puede contener más corridas SRA que muestras
biológicas debido a secuenciaciones repetidas de determinadas muestras.
Las corridas técnicas correspondientes a una misma muestra biológica no
deben tratarse como réplicas biológicas independientes en el análisis
diferencial.

------------------------------------------------------------------------

## 20. Preparación para PyDESeq2

PyDESeq2 requiere una matriz con orientación:

``` text
muestras × genes
```

Por este motivo, la matriz filtrada se transpone antes del análisis.

También se comprueba que:

-   los conteos sean enteros;
-   no existan valores negativos;
-   las muestras coincidan exactamente con los metadatos;
-   exista la variable experimental `condition`;
-   las condiciones esperadas sean `AD` y `non_AD`.

Variables previstas en el notebook:

``` python
counts_pydeseq2
metadata_pydeseq2
```

Los datos introducidos en PyDESeq2 deben ser **conteos crudos enteros**.
No deben transformarse previamente a TPM, FPKM, CPM, TMM ni log2.

------------------------------------------------------------------------

## 21. Instalación y comprobación de PyDESeq2

Antes de instalar nuevas dependencias se recomienda comprobar:

``` bash
python --version
python -m pip --version
python -m pip check
```

También puede inspeccionarse la presencia y versión de paquetes
relevantes:

``` bash
conda list anndata
conda list numpy
conda list pandas
conda list scipy
conda list scikit-learn
conda list matplotlib
conda list h5py
```

Si Conda informa conflictos de resolución, no se recomienda utilizar
opciones como `--no-deps` para forzar la instalación.

La instalación de PyDESeq2 debe completarse únicamente cuando las
dependencias del entorno hayan sido revisadas y resueltas.

Una vez instalado:

``` bash
python -c "import pydeseq2; print(pydeseq2.__version__)"
python -c "import pydeseq2; print(pydeseq2.__file__)"
```

------------------------------------------------------------------------

## 22. Análisis con PyDESeq2

El diseño previsto es:

``` text
~condition
```

y el contraste:

``` text
AD vs non_AD
```

PyDESeq2 utiliza su propia estimación de factores de tamaño y modelo
estadístico basado en DESeq2. No debe describirse esta normalización
como TMM.

Los resultados esperados incluyen, entre otras variables:

``` text
log2FoldChange
pvalue
padj
```

### Limitación del subconjunto de validación

La ejecución con únicamente dos corridas tiene como objetivo comprobar
que la matriz, los metadatos y las funciones del pipeline se integran
correctamente.

No deben interpretarse los valores de expresión diferencial obtenidos
con este subconjunto como evidencia biológica robusta. Para el análisis
inferencial deben utilizarse las muestras biológicas correspondientes al
diseño experimental completo y tratar adecuadamente las corridas
técnicas.

------------------------------------------------------------------------

## 23. Estrategias generales de optimización

El workflow incorpora varias estrategias para reducir la demanda de
recursos:

-   validación inicial con un subconjunto de dos corridas;
-   procesamiento secuencial de las corridas;
-   transmisión HISAT2 → Samtools mediante `pipe`;
-   ausencia de un archivo SAM intermedio;
-   limitación explícita de hilos y memoria en operaciones de
    ordenamiento;
-   utilización de un directorio temporal controlado;
-   eliminación de intermediarios únicamente después de verificar el
    archivo final;
-   monitorización del almacenamiento mediante `df` y `du`;
-   evaluación de la caché de Conda mediante
    `conda clean --all --dry-run`;
-   limpieza de caché cuando sea necesario.

La optimización del almacenamiento y la optimización de RAM deben
documentarse como componentes diferentes de la gestión de recursos.

------------------------------------------------------------------------

## 24. Comprobaciones recomendadas antes de una etapa pesada

Antes de iniciar alineamiento o procesamiento intensivo:

``` bash
conda activate env_tesis

df -h /home/paula.chaparro
du -sh /home/paula.chaparro/miniconda3/pkgs

which hisat2
which samtools
hisat2 --version
samtools --version
```

Si el almacenamiento es limitado:

``` bash
conda clean --all --dry-run
```

y solo cuando sea necesario:

``` bash
conda clean --all
```

------------------------------------------------------------------------

## 25. Reproducibilidad

Para facilitar la reproducción del workflow se recomienda conservar
junto con el proyecto:

``` text
environment.yml
README.md
METADATA.txt
code/tesis.ipynb
```

El archivo `environment.yml` documenta el entorno de software, mientras
que este README documenta el orden de ejecución, la arquitectura y las
comprobaciones operativas necesarias.

Los archivos de datos de gran tamaño no deben duplicarse
innecesariamente dentro de la arquitectura del proyecto.

------------------------------------------------------------------------

## 26. Orden general del pipeline

``` text
Configuración del entorno
        ↓
Verificación y optimización de recursos
        ↓
Recuperación de metadatos
        ↓
Descarga FASTQ
        ↓
FastQC inicial
        ↓
Trimming
        ↓
FastQC post-trimming + MultiQC
        ↓
Preparación del genoma GRCh38
        ↓
Alineamiento HISAT2
        ↓
Samtools sort
        ↓
Marcaje de posibles duplicados
        ↓
Preparación GENCODE v50
        ↓
Comprobación BAM-GTF
        ↓
featureCounts
        ↓
Matriz de conteos crudos
        ↓
Filtrado de baja expresión
        ↓
Preparación/verificación de metadatos
        ↓
AD vs non-AD
        ↓
Preparación para PyDESeq2
        ↓
PyDESeq2
        ↓
Organización e interpretación de resultados
```

------------------------------------------------------------------------

## 27. Nota sobre el estado del workflow

Este README documenta tanto las etapas ya definidas como las
comprobaciones previstas para la ejecución completa del pipeline. La
correcta generación de un archivo o resultado debe verificarse durante
la ejecución antes de eliminar archivos intermedios o avanzar a una
etapa dependiente.

Los parámetros y criterios estadísticos utilizados durante la validación
con dos corridas deberán revisarse antes del análisis final con el
conjunto completo.

------------------------------------------------------------------------

## 28. Versiones verificadas del entorno para el análisis estadístico y funcional

Durante la preparación de las etapas estadísticas y funcionales se
verificaron las siguientes versiones en el entorno `env_tesis`:

``` text
Python 3.11.13
NumPy 2.3.1
pandas 2.3.0
matplotlib 3.10.3
SciPy 1.17.1
scikit-learn 1.9.0
h5py 3.16.0
anndata 0.12.19
PyDESeq2 0.5.4
GSEApy 1.3.1
boto3 1.43.83
pyarrow 25.0.0
```

`boto3` y `pyarrow` se incorporaron para resolver dependencias
requeridas por MultiQC 1.35. Tras su instalación se comprobó la
consistencia de las dependencias Python mediante:

``` bash
python -m pip check
```

La instalación de MultiQC se verifica mediante:

``` bash
multiqc --version
```

------------------------------------------------------------------------

## 29. Transformación VST y análisis de componentes principales

Después del ajuste del modelo con PyDESeq2, la variabilidad entre
muestras puede explorarse mediante una transformación estabilizadora de
la varianza (VST) y un análisis de componentes principales (PCA).

La transformación VST se obtiene desde el objeto `DeseqDataSet` y se
utiliza exclusivamente con fines exploratorios y de visualización. El
PCA se calcula mediante `scikit-learn`.

Variables previstas en el notebook:

``` python
vst_df
pca_df
```

Las coordenadas del PCA se conservan en:

``` text
results/PCA_coordinates.csv
```

El PCA realizado sobre el subconjunto de dos corridas constituye
únicamente una comprobación técnica del workflow y no debe interpretarse
como evidencia de separación biológica robusta entre condiciones.

------------------------------------------------------------------------

## 30. Identificación y clasificación de genes diferencialmente expresados

Los resultados producidos por PyDESeq2 se utilizan para identificar
genes diferencialmente expresados (DEGs).

Durante la validación se han definido como criterios configurables:

``` text
padj < 0.05
|log2FoldChange| >= 1
```

Dado que el contraste se define como `AD vs non_AD`:

-   valores positivos de `log2FoldChange` indican mayor expresión
    estimada en AD;
-   valores negativos indican mayor expresión estimada en non-AD.

Los genes se clasifican en:

``` text
Mayor expresión en AD
Mayor expresión en non_AD
No significativo
```

Los resultados completos y la tabla de DEGs se conservan en `results/`.

Estos criterios deberán revisarse junto con el diseño estadístico cuando
se realice el análisis con el conjunto completo de muestras biológicas.

------------------------------------------------------------------------

## 31. Visualización de la expresión diferencial

Los resultados de expresión diferencial pueden representarse mediante un
volcano plot construido con NumPy y matplotlib.

La figura utiliza:

``` text
Eje X: log2FoldChange
Eje Y: -log10(padj)
```

Las líneas de referencia corresponden a los mismos criterios utilizados
para clasificar los DEGs.

Salida prevista:

``` text
results/volcano_plot_AD_vs_non_AD.png
```

------------------------------------------------------------------------

## 32. Heatmap de genes diferencialmente expresados

Los patrones de expresión de los DEGs se visualizan utilizando los
valores transformados mediante VST y no los conteos crudos.

Para facilitar la comparación entre genes, los valores pueden
estandarizarse por gen mediante Z-score. Esta estandarización se utiliza
únicamente para visualización y no modifica los resultados del análisis
diferencial realizado con PyDESeq2.

Cuando el número de genes es elevado, puede limitarse la figura a los
DEGs con menor `padj` para mantener una representación interpretable.

------------------------------------------------------------------------

## 33. Clustering jerárquico opcional

Como análisis exploratorio adicional, el workflow contempla un módulo
opcional de heatmap con clustering jerárquico de genes y muestras.

La configuración prevista utiliza:

``` text
distancia euclidiana
enlace promedio (average linkage)
```

El clustering se calcula sobre valores VST estandarizados mediante
Z-score.

Este módulo resulta especialmente informativo cuando existen múltiples
réplicas biológicas. Con únicamente dos corridas de validación, el
agrupamiento debe considerarse una comprobación técnica y no una
conclusión biológica.

------------------------------------------------------------------------

## 34. Anotación de identificadores génicos

La cuantificación con featureCounts utiliza `gene_id` como identificador
principal. Para facilitar la interpretación biológica y las etapas
funcionales posteriores, el workflow construye una correspondencia:

``` text
gene_id → gene_name
```

La correspondencia se obtiene directamente del mismo archivo GENCODE v50
utilizado durante la cuantificación, evitando introducir una fuente de
anotación diferente.

Cuando los identificadores Ensembl contienen un sufijo de versión, este
se elimina para realizar la correspondencia, conservándose también el
identificador original en los resultados.

La tabla de correspondencia se almacena como:

``` text
results/GENCODE_gene_id_gene_name.csv
```

Los resultados de PyDESeq2 anotados se almacenan como:

``` text
results/pydeseq2_AD_vs_non_AD_annotated.csv
```

------------------------------------------------------------------------

## 35. Análisis funcional mediante Gene Ontology

El análisis funcional de los DEGs se plantea mediante GSEApy 1.3.1 y el
servicio Enrichr.

Antes del enriquecimiento, los identificadores génicos se convierten a
símbolos génicos utilizando la correspondencia construida a partir de
GENCODE.

Los genes se separan según la dirección del cambio de expresión:

``` text
Mayor expresión en AD
Mayor expresión en non_AD
```

El enriquecimiento se evalúa de manera independiente para cada grupo
utilizando las tres ramas principales de Gene Ontology:

``` text
Biological Process (BP)
Molecular Function (MF)
Cellular Component (CC)
```

Los términos enriquecidos se filtran mediante el valor de significancia
ajustado (`Adjusted P-value < 0.05`). Se conservan tanto las tablas
completas como las tablas de términos significativos en `results/`.

La ejecución de `gseapy.enrichr()` requiere acceso a internet para
consultar el servicio Enrichr.

Cuando una lista contiene un número muy reducido de genes, el
enriquecimiento se omite para evitar interpretar resultados poco
informativos. Al igual que el análisis diferencial, los resultados
obtenidos a partir del subconjunto de dos corridas deben considerarse
únicamente parte de la validación computacional del workflow.

------------------------------------------------------------------------

## 36. Orden actualizado de las etapas estadísticas y funcionales

``` text
Matriz de conteos crudos
        ↓
Filtrado de genes con baja expresión
        ↓
Preparación y verificación de metadatos
        ↓
Preparación para PyDESeq2
        ↓
PyDESeq2
        ↓
VST + PCA
        ↓
Identificación y clasificación de DEGs
        ↓
Volcano plot
        ↓
Heatmap de DEGs
        ↓
Heatmap + clustering jerárquico (opcional)
        ↓
Anotación gene_id → gene_name
        ↓
Enriquecimiento Gene Ontology con GSEApy / Enrichr
```

Las transformaciones utilizadas para PCA, heatmaps y clustering tienen
fines exploratorios y de visualización. El análisis diferencial se
realiza a partir de conteos crudos enteros mediante PyDESeq2.

------------------------------------------------------------------------

## 37. Diagnóstico y optimización del almacenamiento en Linux

Durante la ejecución del módulo de alineamiento y ordenamiento se
realizó un diagnóstico de recursos del sistema para evaluar la
disponibilidad de memoria y almacenamiento. Estas comprobaciones se
ejecutaron desde Linux y se incorporaron como parte de la estrategia de
monitorización del workflow.

### Comprobación de memoria y carga del sistema

``` bash
uptime
free -h
```

`uptime` permite revisar la carga del sistema y `free -h` muestra la
memoria RAM y swap disponibles. La evaluación de RAM y almacenamiento se
mantiene separada, ya que la liberación de espacio en disco no implica
una reducción directa del consumo de memoria RAM.

### Comprobación del almacenamiento

``` bash
df -h /home/paula.chaparro
```

Para localizar los directorios con mayor ocupación pueden utilizarse
comandos `du`, por ejemplo:

``` bash
du -sh /home/paula.chaparro/* 2>/dev/null
du -sh /home/paula.chaparro/Documentos/tesis_2025/* 2>/dev/null
```

Estas comprobaciones permiten diferenciar el espacio ocupado por el
proyecto del utilizado por otros directorios del sistema o del usuario.

### Comprobación de procesos después de una interrupción

Después de una interrupción o reinicio de la instancia puede comprobarse
si permanecen procesos relacionados con el alineamiento:

``` bash
ps aux | grep -E 'hisat2|samtools' | grep -v grep
```

La ausencia de estos procesos confirma únicamente que no continúan
activos en el momento de la comprobación; no permite establecer por sí
sola la causa de una interrupción previa.

### Revisión de registros del sistema

Cuando los permisos del usuario lo permiten, pueden revisarse los
arranques y registros disponibles mediante:

``` bash
journalctl --list-boots
journalctl -b -1
```

El acceso a determinados mensajes del kernel o del journal puede estar
restringido según los permisos de la instancia. Por ello, la ausencia de
mensajes visibles de OOM no debe interpretarse como evidencia
concluyente de que no se produjo un problema de memoria.

------------------------------------------------------------------------

## 38. Limpieza de la papelera del usuario

Durante el diagnóstico se identificó que una fracción importante del
almacenamiento permanecía ocupada por archivos previamente eliminados
que todavía se encontraban en la papelera de Linux.

El tamaño puede comprobarse mediante:

``` bash
du -sh /home/paula.chaparro/.local/share/Trash
du -sh /home/paula.chaparro/.local/share/Trash/files
du -sh /home/paula.chaparro/.local/share/Trash/info
```

Después de verificar su contenido, la papelera puede vaciarse eliminando
los archivos y sus metadatos asociados:

``` bash
rm -rf /home/paula.chaparro/.local/share/Trash/files/*
rm -rf /home/paula.chaparro/.local/share/Trash/info/*
```

Tras la limpieza debe volver a comprobarse el almacenamiento:

``` bash
df -h /home/paula.chaparro
du -sh /home/paula.chaparro/.local/share/Trash
```

Durante la ejecución documentada del workflow, esta intervención redujo
el contenido de la papelera de aproximadamente **24 GB a 36 KB**. El
espacio disponible en `/home` aumentó de **8.8 GB a 33 GB**, mientras
que la ocupación disminuyó del **92 % al 68 %**. El tamaño del proyecto
permaneció en aproximadamente **28 GB**, permitiendo distinguir la
recuperación de almacenamiento del borrado de archivos propios del
workflow.

> La limpieza de la papelera constituye una operación de mantenimiento
> del entorno y no una etapa bioinformática del pipeline. Debe
> realizarse únicamente después de comprobar que los archivos eliminados
> previamente ya no son necesarios.

------------------------------------------------------------------------

## 39. Limpieza controlada de archivos intermedios antes de HISAT2

Además del mantenimiento general del sistema, se incorporó al workflow
una estrategia de limpieza controlada de archivos intermedios
reproducibles antes del alineamiento. Su objetivo es evitar que
permanezcan simultáneamente almacenadas múltiples representaciones de
gran tamaño de una misma corrida.

La eliminación se realiza únicamente cuando se han verificado
previamente los dos FASTQ posteriores al trimming correspondientes a la
corrida. Los archivos que pueden considerarse para eliminación son:

``` text
FASTQ originales de data/raw/
archivo SRA residual después de su conversión
```

Se conservan:

``` text
FASTQ posteriores al trimming
resultados de control de calidad
metadatos
índice HISAT2 del genoma de referencia
archivos de monitorización
resultados necesarios para las etapas posteriores
```

El criterio de seguridad aplicado es:

``` text
Verificar R1 trimmed + R2 trimmed
        ↓
Comprobar que existen y no están vacíos
        ↓
Identificar FASTQ raw y SRA reproducibles
        ↓
Eliminar únicamente los archivos identificados
        ↓
Medir nuevamente el espacio disponible
```

En la corrida `SRR14436589` se verificaron dos FASTQ trimmed de
aproximadamente **5.15 GB cada uno**. Posteriormente se eliminaron los
dos FASTQ originales, de aproximadamente **5.32 GB cada uno**, y un
archivo SRA residual de aproximadamente **2.27 GB**. La limpieza eliminó
**12.92 GB** y aumentó el espacio disponible de **32.30 GB a 45.21 GB**.

La corrida `SRR14436590` no fue modificada porque no se encontró el
primer FASTQ trimmed esperado. Este comportamiento constituye una medida
de seguridad: si los archivos requeridos para continuar el workflow no
están disponibles, los datos originales de esa corrida no se eliminan.

Los archivos eliminados en esta etapa corresponden a copias locales
reproducibles a partir de los datos depositados en SRA. Los
identificadores de acceso, metadatos y comandos de descarga deben
conservarse para mantener la trazabilidad y permitir su recuperación
cuando sea necesario.

------------------------------------------------------------------------

## 40. Secuencia recomendada de gestión de almacenamiento antes del alineamiento

Antes de ejecutar HISAT2 y Samtools se recomienda seguir el siguiente
orden:

``` text
Comprobar RAM y almacenamiento
        ↓
Revisar tamaño del proyecto y directorios principales
        ↓
Comprobar caché de Conda y papelera del usuario
        ↓
Realizar mantenimiento únicamente cuando sea necesario
        ↓
Verificar FASTQ posteriores al trimming
        ↓
Eliminar de forma controlada intermediarios reproducibles
        ↓
Volver a medir el espacio disponible
        ↓
Ejecutar HISAT2 → Samtools
```

Esta estrategia separa tres tipos de intervención: mantenimiento del
entorno Linux, mantenimiento del entorno Conda y eliminación controlada
de archivos intermedios del workflow. Las modificaciones deben
documentarse junto con las mediciones anteriores y posteriores para
poder evaluar cuantitativamente su efecto sobre los recursos
disponibles.

------------------------------------------------------------------------

# 41. Estado final de la validación computacional

La validación final del workflow se realizó conservando el registro
histórico completo y seleccionando posteriormente las ejecuciones
representativas confirmadas para el análisis de rendimiento.

El archivo histórico se mantiene sin modificaciones:

``` text
results/monitorizacion_recursos.csv
```

Para el análisis final se generó:

``` text
results/monitorizacion_recursos_final.csv
```

El registro depurado contiene 24 ejecuciones seleccionadas, clasificadas
de la siguiente manera:

``` text
Módulos completados: 15
Etapas de preparación: 2
Ejecución detenida por falta de replicación: 1
Ejecuciones no completadas por dependencia de M16: 6
```

Las etapas de preparación y las ejecuciones que no completaron su
función principal se conservaron para trazabilidad, pero se excluyeron
de la comparación principal de rendimiento.

# 42. Adaptación del subconjunto para representar AD y non-AD

La matriz de conteos utilizada inicialmente contenía únicamente la
corrida `SRR14436589`, correspondiente a la condición AD. Esta situación
impedía comprobar la preparación de una comparación AD frente a non-AD.

Para extender la validación técnica se incorporó una segunda corrida
real, `SRR14436618`, correspondiente a la condición non-AD. La selección
priorizó una alternativa de menor tamaño entre las corridas non-AD
identificadas, con el objetivo de limitar la demanda computacional.

El subconjunto final quedó constituido por:

``` text
SRR14436589 → AD
SRR14436618 → non_AD
```

Para `SRR14436618`, el procesamiento adicional permitió completar la
descarga, conversión, trimming, alineamiento, procesamiento BAM y
cuantificación. El alineamiento se completó en aproximadamente 13.09
min, con una tasa global de alineamiento de 99.16 %. El procesamiento de
duplicados requirió aproximadamente 11.60 min y featureCounts asignó
8,853,248 alineamientos, equivalentes al 50.5 %.

La matriz conjunta resultante contenía 78,733 genes y dos muestras.
Después del filtro de baja expresión se conservaron 20,402 genes.

Los archivos correspondientes son:

``` text
results/raw_counts_matrix_AD_nonAD.csv
results/filtered_counts_matrix_AD_nonAD.csv
```

Las matrices anteriores se conservaron para mantener la trazabilidad.

# 43. Limitación estadística identificada en PyDESeq2

La preparación de los datos y metadatos para PyDESeq2 se completó
correctamente con las dos condiciones representadas. Sin embargo, el
módulo de expresión diferencial se detuvo al comprobar que existía
únicamente una muestra por condición.

La ausencia de replicación impide estimar adecuadamente la dispersión
requerida por el modelo de PyDESeq2. Por este motivo, la detención de
M16 se interpretó como una limitación del subconjunto de validación y no
como un error del código.

No se duplicaron muestras, no se generaron replicados artificiales y no
se modificó el modelo estadístico para forzar su ejecución.

Para completar técnicamente esta etapa se requiere, como mínimo, ampliar
el subconjunto a dos muestras biológicas independientes AD y dos non-AD.
Una replicación mayor sería necesaria para realizar inferencias
biológicas robustas.

El PCA (M17) sí pudo ejecutarse y generó:

``` text
results/PCA_coordinates.csv
```

Debido a que solo existen dos observaciones, este resultado se considera
exclusivamente una comprobación computacional.

Los módulos M18--M23 dependen de resultados válidos de expresión
diferencial y, por tanto, no completaron su función principal con el
subconjunto utilizado.

# 44. Resultados finales de monitorización

Para los 15 módulos clasificados como completados, el tiempo acumulado
registrado fue de aproximadamente:

``` text
3646.59 segundos
60.78 minutos
1.01 horas
```

Este valor corresponde a la suma de las ejecuciones representativas
completadas y no al tiempo total de desarrollo, pruebas, limpiezas,
reinicios o procesamiento auxiliar.

Los principales resultados de rendimiento fueron:

  Indicador                                Resultado
  ---------------------------------------- -----------------------
  Mayor duración                           M8: 17.95 min
  Mayor pico RSS                           M8: 5.580 GB
  Porcentaje de RAM física en M8           73.3 %
  Segundo mayor pico RSS                   M9: 3.883 GB (51.0 %)
  Mayor crecimiento del proyecto           M2: +12.916 GB
  Segundo mayor crecimiento                M4: +10.292 GB
  Contribución temporal conjunta M8 + M9   aproximadamente 53 %

M8 y M9 concentraron la mayor demanda de tiempo y memoria, mientras que
M2 y M4 generaron los mayores incrementos netos de almacenamiento. Por
tanto, los principales cuellos de botella dependen del recurso
computacional considerado.

# 45. Figuras finales de rendimiento

A partir del registro depurado se generaron las siguientes figuras:

``` text
results/figura_tiempo_ejecucion_modulos.png
results/figura_pico_memoria_modulos.png
results/figura_cambio_almacenamiento_modulos.png
results/figura_evolucion_espacio_disco.png
```

La figura de tiempo muestra que M8 y M9 representan conjuntamente
aproximadamente el 53 % del tiempo acumulado de los módulos completados.

La figura de memoria muestra un pico RSS de 5.580 GB para M8,
equivalente al 73.3 % de los 7.61 GB de RAM física registrados, seguido
por M9 con 3.883 GB (51.0 %).

La figura de almacenamiento muestra que M2 (+12.916 GB) y M4 (+10.292
GB) produjeron los mayores incrementos del tamaño del proyecto.

La evolución del espacio libre evidencia además la necesidad de
gestionar archivos intermedios. Después de M6 se registraron 8.70 GB
libres, mientras que antes de M7 se registraron 45.21 GB después de las
acciones de limpieza realizadas entre ambas mediciones. Estas
discontinuidades no deben atribuirse automáticamente a un módulo
concreto.

# 46. Tabla definitiva de rendimiento

La tabla final incluye únicamente las 15 ejecuciones que completaron su
función principal.

Archivos:

``` text
results/tabla_rendimiento_workflow.csv
results/tabla_rendimiento_workflow.xlsx
```

Columnas:

``` text
Módulo
Etapa
Tiempo (min)
Pico RSS (GB)
RAM física (%)
Cambio proyecto (GB)
```

El tiempo se recalculó directamente a partir de `duracion_segundos`
antes del redondeo para evitar acumulación de errores derivados de
valores en minutos previamente redondeados.

Las etapas de preparación y las ejecuciones incompletas no se utilizaron
como métricas de rendimiento completo.

# 47. Gestión final de almacenamiento y recursos

La gestión del almacenamiento formó parte de la estrategia de ejecución.
Antes de eliminar intermediarios se verificó la disponibilidad de los
productos necesarios para continuar el análisis.

Entre las acciones documentadas se incluyen:

``` text
limpieza de la papelera del usuario
eliminación controlada de FASTQ originales ya procesados
eliminación de archivos SRA residuales
eliminación progresiva de intermediarios de samtools
verificación de espacio libre antes de HISAT2
procesamiento secuencial
reducción de hilos en etapas intensivas
uso de pipes para evitar archivos SAM de gran tamaño
```

La limpieza de archivos residuales de `SRR14436589`, realizada después
de verificar los FASTQ procesados, liberó aproximadamente 12.92 GiB y
aumentó el espacio disponible de aproximadamente 32.30 GB a 45.21 GB.

Los controles periódicos utilizados incluyen:

``` bash
free -h
df -h
uptime
```

y la comprobación de procesos bioinformáticos activos mediante:

``` bash
ps aux | grep -E "hisat2|hisat2-align|samtools|fastqc|fastp|multiqc|fasterq-dump|prefetch|featureCounts"
```

La presencia de un proceso debe verificarse antes de considerar
cualquier acción sobre él.

# 48. Archivos finales relevantes

Al cierre de la validación, los principales archivos de resultados
incluyen:

``` text
results/
├── diagnostico_inicial.csv
├── featureCounts_counts.txt
├── featureCounts_counts.txt.summary
├── SRR14436618_featureCounts.txt
├── SRR14436618_featureCounts.txt.summary
├── raw_counts_matrix.csv
├── filtered_counts_matrix.csv
├── raw_counts_matrix_AD_nonAD.csv
├── filtered_counts_matrix_AD_nonAD.csv
├── PCA_coordinates.csv
├── monitorizacion_recursos.csv
├── monitorizacion_recursos_final.csv
├── tabla_rendimiento_workflow.csv
├── tabla_rendimiento_workflow.xlsx
├── figura_tiempo_ejecucion_modulos.png
├── figura_pico_memoria_modulos.png
├── figura_cambio_almacenamiento_modulos.png
└── figura_evolucion_espacio_disco.png
```

`raw_counts_matrix.csv` y `filtered_counts_matrix.csv` corresponden a
una etapa anterior de la validación. Para la validación con las dos
condiciones experimentales deben utilizarse las matrices
`*_AD_nonAD.csv`.

# 49. Resultados no generados con el subconjunto reducido

Debido a la ausencia de replicación dentro de las condiciones, no se
generaron como resultados finales válidos:

``` text
resultado final de PyDESeq2 AD vs non-AD
clasificación final de DEGs
volcano plot basado en resultados diferenciales válidos
heatmaps de DEGs
anotación final de resultados diferenciales
análisis funcional de DEGs
```

Su ausencia es coherente con la detención controlada de M16 y con las
dependencias de los módulos posteriores.

# 50. Estado final del workflow

El estado de la validación puede resumirse como:

``` text
✓ obtención de metadatos
✓ descarga y conversión
✓ control de calidad
✓ trimming
✓ segundo control de calidad
✓ preparación del genoma de referencia
✓ alineamiento
✓ procesamiento BAM y marcaje de duplicados
✓ preparación de la anotación
✓ cuantificación
✓ construcción de la matriz de conteos
✓ filtrado de baja expresión
✓ representación de AD y non-AD en metadatos
✓ preparación de datos para PyDESeq2
✓ PCA
△ expresión diferencial: detenida por ausencia de replicación
△ M18–M23: no completados por dependencia de M16
```

Los análisis realizados con el subconjunto reducido constituyen una
**validación computacional del workflow** y no deben interpretarse como
inferencia biológica definitiva sobre la enfermedad de Alzheimer.

# 51. Recomendaciones para una extensión futura

Para completar la validación estadística se recomienda incorporar, como
mínimo, dos muestras biológicas independientes por condición y
posteriormente ampliar la replicación para aumentar la robustez del
análisis.

Una nueva evaluación debería mantener la misma estrategia de
monitorización para poder comparar objetivamente:

``` text
tiempo de ejecución
pico RSS
uso relativo de RAM
crecimiento del almacenamiento
espacio libre disponible
configuración de hilos y memoria
```

Las optimizaciones futuras deberían aplicarse después de establecer una
medición basal reproducible, modificando una configuración a la vez y
comparando posteriormente los resultados.
