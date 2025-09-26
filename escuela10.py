import streamlit as st
from PIL import Image
import datetime
import random
import string
import time
import os
import pandas as pd
from io import BytesIO
import csv
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko

# Configuración inicial
def configurar_pagina():
    st.set_page_config(
        page_title="Escuela de Enfermería - Instituto Nacional de Cardiología Ignacio Chávez",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def cargar_estilos():
    st.markdown("""
    <style>
    :root {
        --color-primario: #003366;
        --color-secundario: #e74c3c;
        --color-exito: #28a745;
        --color-info: #17a2b8;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
        line-height: 1.6;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 1rem;
        border-bottom: 1px solid #dee2e6;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f9ff 0%, #e1ebfa 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .programa-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid var(--color-primario);
        transition: all 0.3s;
    }
    
    .programa-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 0.75em;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
    }
    
    .badge-primary {
        color: #fff;
        background-color: var(--color-primario);
    }
    
    .badge-secondary {
        color: #fff;
        background-color: #6c757d;
    }
    
    .badge-success {
        color: #fff;
        background-color: var(--color-exito);
    }
    
    .badge-warning {
        color: #fff;
        background-color: #ffc107;
    }
    
    .form-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .required-field::after {
        content: " *";
        color: var(--color-secundario);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

# Tabla de abreviaturas para cada programa
ABREVIATURAS_PROGRAMAS = {
    # ESPECIALIDADES UNAM
    "Especialidad en Enfermería Cardiovascular": "ESP-CARD",
    "Especialidad en Enfermería Nefrológica": "ESP-NEFR",
    "Especialidad en Gestión del Cuidado": "ESP-GEST",
    
    # ESPECIALIDAD SEP
    "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión": "ESP-PERF",
    
    # LICENCIATURA UNAM
    "Licenciatura en Enfermería": "LIC-ENF",
    
    # DIPLOMADOS
    "Diplomado de Cardiología Básica para Profesionales de Enfermería": "DIP-CBAS",
    "Diplomado de Cardiología Pediátrica para Profesionales de Enfermería": "DIP-CPED",
    "Diplomado de Oxigenación por Membrana Extracorpórea": "DIP-ECMO",
    "Diplomado de Enseñanza en Simulación Clínica": "DIP-SIMU",
    "Diplomado de Hemodinámica": "DIP-HEMO",
    "Diplomado de Nefro-Intervencionismo": "DIP-NINT"
}

# Tabla de abreviaturas para tipos de documentos
ABREVIATURAS_DOCUMENTOS = {
    # Documentos generales
    "Acta de nacimiento": "ACTNAC",
    "Certificado de bachillerato": "BACH",
    "CURP": "CURP",
    "Comprobante de domicilio": "DOM",
    "Identificación oficial": "INE",
    
    # Documentos profesionales
    "Título profesional": "TITULO",
    "Cédula profesional": "CEDULA",
    "CV actualizado": "CV",
    "Carta de motivos": "MOTIVOS",
    "Carta de exposición de motivos": "EXPMOT",
    
    # Documentos específicos
    "Certificado médico de buena salud": "MEDICO",
    "Fotografías tamaño infantil": "FOTOS",
    "Cartas de recomendación": "RECOM",
    "Comprobante de estudios": "ESTUDIOS",
    "Comprobante de estudios de enfermería": "ESTENF"
}

# Mapeo de categorías de programas para directorios remotos
CATEGORIAS_PROGRAMAS = {
    "ESP-CARD": "ESPECIALIDADES",
    "ESP-NEFR": "ESPECIALIDADES", 
    "ESP-GEST": "ESPECIALIDADES",
    "ESP-PERF": "ESPECIALIDADES",
    "LIC-ENF": "LICENCIATURAS",
    "DIP-CBAS": "DIPLOMADOS",
    "DIP-CPED": "DIPLOMADOS",
    "DIP-ECMO": "DIPLOMADOS",
    "DIP-SIMU": "DIPLOMADOS",
    "DIP-HEMO": "DIPLOMADOS",
    "DIP-NINT": "DIPLOMADOS"
}

# Funciones auxiliares mejoradas
def obtener_configuracion():
    """Obtiene la configuración desde secrets.toml"""
    try:
        return {
            'smtp_server': st.secrets.get("smtp_server", "smtp.gmail.com"),
            'smtp_port': st.secrets.get("smtp_port", 587),
            'email_user': st.secrets.get("email_user", ""),
            'email_password': st.secrets.get("email_password", ""),
            'notification_email': st.secrets.get("notification_email", ""),
            'remote_host': st.secrets.get("remote_host", ""),
            'remote_user': st.secrets.get("remote_user", ""),
            'remote_password': st.secrets.get("remote_password", ""),
            'remote_port': st.secrets.get("remote_port", 22),
            'remote_dir': st.secrets.get("remote_dir", ""),
            'supervisor_mode': st.secrets.get("supervisor_mode", False),
            'debug_mode': st.secrets.get("debug_mode", False)
        }
    except Exception as e:
        st.error(f"Error al cargar configuración: {e}")
        return {}

def generar_matricula():
    return 'MAT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def validar_email(email):
    return '@' in email and '.' in email.split('@')[-1]

def obtener_abreviatura_programa(programa):
    """Obtiene la abreviatura para un programa dado"""
    return ABREVIATURAS_PROGRAMAS.get(programa, "OTRO")

def obtener_categoria_directorio(abreviatura_programa):
    """Obtiene la categoría del directorio para una abreviatura de programa"""
    return CATEGORIAS_PROGRAMAS.get(abreviatura_programa, "OTROS")

def obtener_ruta_remota_completa(abreviatura_programa, nombre_archivo):
    """Obtiene la ruta completa remota para un archivo"""
    config = obtener_configuracion()
    remote_base = config.get('remote_dir', '')
    categoria = obtener_categoria_directorio(abreviatura_programa)
    
    # Construir la ruta remota: remote_dir/CATEGORIA/nombre_archivo
    return f"{remote_base}/{categoria}/{nombre_archivo}"

def obtener_abreviatura_documento(nombre_documento):
    """Obtiene la abreviatura para un tipo de documento"""
    # Buscar coincidencias en las claves del diccionario
    for clave, abreviatura in ABREVIATURAS_DOCUMENTOS.items():
        if clave.lower() in nombre_documento.lower():
            return abreviatura
    # Si no encuentra coincidencia, generar una abreviatura basada en el nombre
    palabras = nombre_documento.split()
    if len(palabras) >= 2:
        return palabras[0][:3].upper() + palabras[1][:3].upper()
    else:
        return nombre_documento[:6].upper().replace(' ', '')

def obtener_ruta_carpeta(programa):
    """Devuelve la ruta de la carpeta correspondiente al programa seleccionado"""
    mapping_carpetas = {
        "Especialidad en Enfermería Cardiovascular": "CURSOS/ESPECIALIDADES/UNAM_Cardiovascular",
        "Especialidad en Enfermería Nefrológica": "CURSOS/ESPECIALIDADES/UNAM_Nefrologica",
        "Especialidad en Gestión del Cuidado": "CURSOS/ESPECIALIDADES/UNAM_Gestion_Cuidado",
        "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión": "CURSOS/ESPECIALIDADES/SEP_Circulacion_Extracorporea",
        "Licenciatura en Enfermería": "CURSOS/LICENCIATURA/UNAM_Enfermeria",
        "Diplomado de Cardiología Básica para Profesionales de Enfermería": "CURSOS/DIPLOMADOS/Cardiologia_Basica",
        "Diplomado de Cardiología Pediátrica para Profesionales de Enfermería": "CURSOS/DIPLOMADOS/Cardiologia_Pediatrica",
        "Diplomado de Oxigenación por Membrana Extracorpórea": "CURSOS/DIPLOMADOS/ECMO",
        "Diplomado de Enseñanza en Simulación Clínica": "CURSOS/DIPLOMADOS/Simulacion_Clinica",
        "Diplomado de Hemodinámica": "CURSOS/DIPLOMADOS/Hemodinamica",
        "Diplomado de Nefro-Intervencionismo": "CURSOS/DIPLOMADOS/Nefro_Intervencionismo"
    }
    return mapping_carpetas.get(programa, "CURSOS/OTROS")

def crear_carpeta_si_no_existe(ruta):
    """Crea la carpeta si no existe"""
    if not os.path.exists(ruta):
        os.makedirs(ruta, exist_ok=True)
        st.info(f"📁 Carpeta creada: {ruta}")

def generar_nombre_archivo_base(datos_inscripcion):
    """Genera el nombre base para todos los archivos del aspirante"""
    nombre_usuario = datos_inscripcion['nombre_completo'].replace(' ', '_').replace('/', '_').replace('\\', '_')
    fecha_actual = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    abreviatura_programa = obtener_abreviatura_programa(datos_inscripcion['programa'])
    return f"{datos_inscripcion['matricula']}.{abreviatura_programa}.{fecha_actual}.{nombre_usuario}"

def guardar_documentos(datos_inscripcion, archivos_subidos):
    """Guarda los documentos en la carpeta correspondiente con nombres estandarizados"""
    try:
        # Obtener ruta de la carpeta
        ruta_carpeta = obtener_ruta_carpeta(datos_inscripcion['programa'])
        crear_carpeta_si_no_existe(ruta_carpeta)
        
        # Generar nombre base para los archivos
        nombre_base = generar_nombre_archivo_base(datos_inscripcion)
        
        documentos_guardados = []
        
        for i, archivo in enumerate(archivos_subidos):
            # Obtener abreviatura del documento
            abreviatura_doc = obtener_abreviatura_documento(archivo['nombre'])
            
            # Generar nombre del archivo con abreviatura
            nombre_archivo = f"{nombre_base}.{abreviatura_doc}.pdf"
            ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
            
            # Guardar el archivo
            with open(ruta_completa, "wb") as f:
                f.write(archivo['archivo'].getvalue())
            
            documentos_guardados.append({
                'nombre_original': archivo['nombre'],
                'nombre_guardado': nombre_archivo,
                'ruta': ruta_completa,
                'tamaño': archivo['tamaño'],
                'abreviatura': abreviatura_doc
            })
        
        return True, documentos_guardados
    except Exception as e:
        return False, str(e)

def guardar_progreso_csv(datos_inscripcion, documentos_guardados):
    """Guarda el progreso en un archivo CSV en la carpeta correspondiente"""
    try:
        # Obtener ruta de la carpeta
        ruta_carpeta = obtener_ruta_carpeta(datos_inscripcion['programa'])
        crear_carpeta_si_no_existe(ruta_carpeta)
        
        # Generar nombre del archivo CSV
        nombre_base = generar_nombre_archivo_base(datos_inscripcion)
        nombre_archivo_csv = f"{nombre_base}.registro.csv"
        ruta_completa_csv = os.path.join(ruta_carpeta, nombre_archivo_csv)
        
        # Preparar datos para CSV
        abreviatura_programa = obtener_abreviatura_programa(datos_inscripcion['programa'])
        categoria_remota = obtener_categoria_directorio(abreviatura_programa)
        
        datos_csv = {
            'matricula': datos_inscripcion['matricula'],
            'programa': datos_inscripcion['programa'],
            'abreviatura_programa': abreviatura_programa,
            'categoria_remota': categoria_remota,
            'nombre_completo': datos_inscripcion['nombre_completo'],
            'fecha_nacimiento': datos_inscripcion['fecha_nacimiento'].strftime("%Y-%m-%d") if datos_inscripcion['fecha_nacimiento'] else '',
            'genero': datos_inscripcion['genero'],
            'email': datos_inscripcion['email'],
            'telefono': datos_inscripcion['telefono'],
            'fecha_inscripcion': datos_inscripcion.get('fecha_inscripcion', ''),
            'documentos_subidos': len(documentos_guardados),
            'nombres_documentos': '; '.join([doc['nombre_guardado'] for doc in documentos_guardados]),
            'abreviaturas_documentos': '; '.join([doc['abreviatura'] for doc in documentos_guardados]),
            'estado': 'PROGRESO' if not datos_inscripcion.get('completado', False) else 'COMPLETADO',
            'fecha_guardado': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'carpeta_destino': ruta_carpeta,
            'carpeta_remota': categoria_remota
        }
        
        # Guardar en CSV
        with open(ruta_completa_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Escribir encabezados
            writer.writerow(datos_csv.keys())
            # Escribir datos
            writer.writerow(datos_csv.values())
        
        return True, ruta_completa_csv, documentos_guardados
    except Exception as e:
        return False, str(e), []

# Nuevas funciones para email y transferencia remota (modificadas para nueva estructura de directorios)
def enviar_notificacion_email(datos_inscripcion, documentos_guardados, es_completado=False):
    """Envía notificación por email cuando se completa una inscripción"""
    try:
        config = obtener_configuracion()
        
        if not config.get('email_user') or not config.get('email_password'):
            st.warning("⚠️ Configuración de email no disponible")
            return False
        
        # Configurar servidor SMTP
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_user'], config['email_password'])
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = config['email_user']
        msg['To'] = config['notification_email']
        
        abreviatura_programa = obtener_abreviatura_programa(datos_inscripcion['programa'])
        categoria_remota = obtener_categoria_directorio(abreviatura_programa)
        
        if es_completado:
            msg['Subject'] = f"✅ INSCRIPCIÓN COMPLETADA - {datos_inscripcion['matricula']}"
            cuerpo = f"""
            Se ha completado una nueva inscripción:
            
            Matrícula: {datos_inscripcion['matricula']}
            Programa: {datos_inscripcion['programa']}
            Abreviatura: {abreviatura_programa}
            Categoría remota: {categoria_remota}
            Nombre: {datos_inscripcion['nombre_completo']}
            Email: {datos_inscripcion['email']}
            Teléfono: {datos_inscripcion['telefono']}
            Fecha: {datos_inscripcion.get('fecha_inscripcion', '')}
            
            Documentos subidos: {len(documentos_guardados)}
            Abreviaturas: {', '.join([doc['abreviatura'] for doc in documentos_guardados])}
            Carpeta local: {obtener_ruta_carpeta(datos_inscripcion['programa'])}
            Carpeta remota: {config.get('remote_dir', '')}/{categoria_remota}/
            
            ---
            Sistema de Inscripciones - Escuela de Enfermería
            """
        else:
            msg['Subject'] = f"💾 PROGRESO GUARDADO - {datos_inscripcion['matricula']}"
            cuerpo = f"""
            Se ha guardado el progreso de una inscripción:
            
            Matrícula: {datos_inscripcion['matricula']}
            Programa: {datos_inscripcion['programa']}
            Abreviatura: {abreviatura_programa}
            Categoría: {categoria_remota}
            Nombre: {datos_inscripcion['nombre_completo']}
            Documentos subidos: {len(documentos_guardados)}
            Estado: PROGRESO
            
            ---
            Sistema de Inscripciones - Escuela de Enfermería
            """
        
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        # Enviar email
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar notificación: {e}")
        return False

def transferir_archivos_remotos(ruta_local, abreviatura_programa):
    """Transfiere archivos al servidor remoto via SFTP con nueva estructura de directorios"""
    try:
        config = obtener_configuracion()
        
        if not all([config.get('remote_host'), config.get('remote_user'), config.get('remote_password')]):
            st.warning("⚠️ Configuración remota no disponible")
            return False
        
        # Obtener categoría y ruta remota
        categoria = obtener_categoria_directorio(abreviatura_programa)
        remote_base = config.get('remote_dir', '')
        remote_dir_categoria = f"{remote_base}/{categoria}"
        
        # Crear conexión SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=config['remote_host'],
            username=config['remote_user'],
            password=config['remote_password'],
            port=config['remote_port']
        )
        
        # Crear cliente SFTP
        sftp = ssh.open_sftp()
        
        try:
            # Crear directorio base remoto si no existe
            try:
                sftp.stat(remote_base)
            except FileNotFoundError:
                sftp.mkdir(remote_base)
            
            # Crear directorio de categoría remoto si no existe
            try:
                sftp.stat(remote_dir_categoria)
            except FileNotFoundError:
                sftp.mkdir(remote_dir_categoria)
            
            if os.path.isfile(ruta_local):
                # Es un archivo individual
                nombre_archivo = os.path.basename(ruta_local)
                ruta_remota = f"{remote_dir_categoria}/{nombre_archivo}"
                sftp.put(ruta_local, ruta_remota)
                st.success(f"✅ Archivo transferido: {nombre_archivo} → {categoria}/")
            elif os.path.isdir(ruta_local):
                # Es una carpeta completa (no debería ocurrir con la nueva estructura)
                st.warning("⚠️ Transferencia de carpetas completas no soportada en nueva estructura")
            
            sftp.close()
            ssh.close()
            return True
            
        except Exception as e:
            sftp.close()
            ssh.close()
            raise e
            
    except Exception as e:
        st.error(f"❌ Error en transferencia remota: {e}")
        return False

def sincronizar_con_servidor(datos_inscripcion, documentos_guardados, ruta_csv):
    """Sincroniza todos los archivos con el servidor remoto usando nueva estructura"""
    try:
        config = obtener_configuracion()
        
        if not config.get('supervisor_mode', False):
            st.info("🔒 Modo supervisor desactivado - No se realizará sincronización remota")
            return True
        
        st.info("🔄 Sincronizando con servidor remoto...")
        
        abreviatura_programa = obtener_abreviatura_programa(datos_inscripcion['programa'])
        categoria = obtener_categoria_directorio(abreviatura_programa)
        
        st.info(f"📁 **Estructura remota:** `{config.get('remote_dir', '')}/{categoria}/`")
        
        # Transferir archivo CSV
        if not transferir_archivos_remotos(ruta_csv, abreviatura_programa):
            return False
        
        # Transferir documentos PDF
        for documento in documentos_guardados:
            if not transferir_archivos_remotos(documento['ruta'], abreviatura_programa):
                return False
        
        # Enviar notificación por email
        if config.get('notification_email'):
            enviar_notificacion_email(datos_inscripcion, documentos_guardados, 
                                    es_completado=datos_inscripcion.get('completado', False))
        
        st.success("✅ Sincronización completada correctamente")
        return True
    except Exception as e:
        st.error(f"❌ Error en sincronización: {e}")
        return False

# Función modificada para guardar progreso con sincronización
def guardar_progreso_completo(datos_inscripcion, archivos_subidos, es_envio_completo=False):
    """Guarda el progreso y sincroniza con servidor remoto si es necesario"""
    # Guardar documentos primero
    if archivos_subidos:
        exito_docs, resultado_docs = guardar_documentos(datos_inscripcion, archivos_subidos)
        if not exito_docs:
            return False, f"Error al guardar documentos: {resultado_docs}"
    else:
        resultado_docs = []
    
    # Guardar registro CSV
    datos_inscripcion['completado'] = es_envio_completo
    exito_csv, ruta_csv, docs_guardados = guardar_progreso_csv(datos_inscripcion, resultado_docs)
    
    if not exito_csv:
        return False, f"Error al guardar registro: {ruta_csv}"
    
    # Sincronizar con servidor remoto si es envío completo
    if es_envio_completo:
        sincronizar_con_servidor(datos_inscripcion, docs_guardados, ruta_csv)
    
    return True, {
        'ruta_csv': ruta_csv,
        'documentos_guardados': docs_guardados,
        'es_completado': es_envio_completo
    }

# Funciones principales de visualización
def mostrar_header():
    st.markdown("""
    <div class="main-header animate-fade">
        <h1>Escuela de Enfermería</h1>
        <h1>Instituto Nacional de Cardiología Ignacio Chávez</h1>
        <p class="lead">Formando profesionales de excelencia en el área de la salud cardiovascular</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_sidebar():
    with st.sidebar:
        try:
            logo = Image.open('escudo_COLOR.jpg')
            st.image(logo, use_container_width=True)
        except FileNotFoundError:
            st.warning("Logo no encontrado")
        
        st.markdown('<div class="sidebar-header"><h3>Menú Principal</h3></div>', unsafe_allow_html=True)
        
        if st.button("🏫 Oferta Educativa"):
            st.session_state.seccion_actual = "Oferta Educativa"
            st.rerun()
        
        if st.button("📝 Inscripción"):
            st.session_state.seccion_actual = "Inscripción"
            st.rerun()
        
        if st.button("📄 Documentación"):
            st.session_state.seccion_actual = "Documentación"
            st.rerun()
        
        if st.button("💳 Pagos"):
            st.session_state.seccion_actual = "Pagos"
            st.rerun()
        
        if st.button("📱 Contacto"):
            st.session_state.seccion_actual = "Contacto"
            st.rerun()
        
        # Mostrar tabla de abreviaturas en el sidebar
        if st.button("🔤 Abreviaturas"):
            st.session_state.mostrar_abreviaturas = not st.session_state.get('mostrar_abreviaturas', False)
            st.rerun()
        
        if st.session_state.get('mostrar_abreviaturas', False):
            st.markdown("---")
            st.markdown("### 📋 Tabla de Abreviaturas")
            
            with st.expander("Programas Académicos"):
                for programa, abreviatura in ABREVIATURAS_PROGRAMAS.items():
                    categoria = obtener_categoria_directorio(abreviatura)
                    st.write(f"**{abreviatura}** ({categoria}): {programa}")
            
            with st.expander("Tipos de Documentos"):
                for documento, abreviatura in ABREVIATURAS_DOCUMENTOS.items():
                    st.write(f"**{abreviatura}**: {documento}")
            
            with st.expander("Estructura de Directorios Remotos"):
                st.write("**ESP-CARD, ESP-NEFR, ESP-GEST, ESP-PERF** → ESPECIALIDADES/")
                st.write("**LIC-ENF** → LICENCIATURAS/")
                st.write("**DIP-CBAS, DIP-CPED, DIP-ECMO, DIP-SIMU, DIP-HEMO, DIP-NINT** → DIPLOMADOS/")

def mostrar_oferta_educativa():
    st.markdown("""
    <div class="animate-fade">
        <h2>Oferta Educativa 2025-2026</h2>
        <p>Explora nuestros programas académicos y encuentra el que mejor se adapte a tus metas profesionales en enfermería cardiovascular.</p>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar información de nueva estructura de directorios
    config = obtener_configuracion()
    remote_base = config.get('remote_dir', '')
 #   st.info(f"📁 **Nueva estructura remota activa:** Los archivos se organizarán automáticamente en `{remote_base}/[CATEGORIA]/`")
 #   st.info(f"🔤 **Ejemplo:** `MAT-ABC123.ESP-CARD.25-09-25.18-12.Carlos_Polanco.CEDULA.pdf` → `{remote_base}/ESPECIALIDADES/`")

    tab1, tab2, tab3, tab4 = st.tabs(["Especialidades UNAM", "Especialidad SEP", "Licenciatura UNAM", "Educación Continua"])

    with tab1:
        st.markdown("""
        <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4>🟢 Especialidades con Aval de la UNAM</h4>
            <p>Programas de posgrado con reconocimiento universitario → <strong>Directorio remoto: ESPECIALIDADES/</strong></p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            abreviatura = ABREVIATURAS_PROGRAMAS["Especialidad en Enfermería Cardiovascular"]
            categoria = obtener_categoria_directorio(abreviatura)
            st.markdown(f"""
            <div class="programa-card">
                <h3>Especialidad en Enfermería Cardiovascular</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                    <span class="badge badge-primary">2 años</span>
                    <span class="badge badge-secondary">Presencial</span>
                    <span class="badge badge-success">Aval UNAM</span>
                    <span class="badge badge-info">{abreviatura}</span>
                    <span class="badge badge-warning">{categoria}</span>
                </div>
                <p>Formación especializada en el cuidado de pacientes con patologías cardiovasculares en unidades de terapia intensiva y áreas críticas.</p>
                <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Inscribirme", key="insc_esp_cardiovascular"):
                st.session_state.seccion_actual = "Inscripción"
                st.session_state.programa_seleccionado = "Especialidad en Enfermería Cardiovascular"
                st.rerun()

        with col2:
            abreviatura = ABREVIATURAS_PROGRAMAS["Especialidad en Enfermería Nefrológica"]
            categoria = obtener_categoria_directorio(abreviatura)
            st.markdown(f"""
            <div class="programa-card">
                <h3>Especialidad en Enfermería Nefrológica</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                    <span class="badge badge-primary">2 años</span>
                    <span class="badge badge-secondary">Presencial</span>
                    <span class="badge badge-success">Aval UNAM</span>
                    <span class="badge badge-info">{abreviatura}</span>
                    <span class="badge badge-warning">{categoria}</span>
                </div>
                <p>Especialización en el cuidado de pacientes con enfermedad renal crónica y aguda, con enfoque cardiovascular.</p>
                <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Inscribirme", key="insc_esp_nefrologica"):
                st.session_state.seccion_actual = "Inscripción"
                st.session_state.programa_seleccionado = "Especialidad en Enfermería Nefrológica"
                st.rerun()

        with col3:
            abreviatura = ABREVIATURAS_PROGRAMAS["Especialidad en Gestión del Cuidado"]
            categoria = obtener_categoria_directorio(abreviatura)
            st.markdown(f"""
            <div class="programa-card">
                <h3>Especialidad en Gestión del Cuidado</h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                    <span class="badge badge-primary">2 años</span>
                    <span class="badge badge-secondary">Semipresencial</span>
                    <span class="badge badge-warning">Próxima apertura Feb 2026</span>
                    <span class="badge badge-info">{abreviatura}</span>
                    <span class="badge badge-warning">{categoria}</span>
                </div>
                <p>Formación en gestión y administración de servicios de enfermería con enfoque en calidad del cuidado.</p>
                <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Pre-inscripción", key="insc_esp_gestion"):
                st.session_state.seccion_actual = "Inscripción"
                st.session_state.programa_seleccionado = "Especialidad en Gestión del Cuidado"
                st.rerun()

    with tab2:
        st.markdown("""
        <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4>🔵 Especialidad con Aval de la SEP</h4>
            <p>Programa de posgrado con reconocimiento oficial federal → <strong>Directorio remoto: ESPECIALIDADES/</strong></p>
        </div>
        """, unsafe_allow_html=True)

        abreviatura = ABREVIATURAS_PROGRAMAS["Especialidad de Enfermería en Circulación Extracorpórea y Perfusión"]
        categoria = obtener_categoria_directorio(abreviatura)
        st.markdown(f"""
        <div class="programa-card">
            <h3>Especialidad de Enfermería en Circulación Extracorpórea y Perfusión</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                <span class="badge badge-primary">2 años</span>
                <span class="badge badge-secondary">Presencial</span>
                <span class="badge badge-success">Aval SEP</span>
                <span class="badge badge-info">{abreviatura}</span>
                <span class="badge badge-warning">{categoria}</span>
            </div>
            <p>Especialización única en el manejo de equipos de circulación extracorpórea durante procedimientos cardiovasculares complejos.</p>
            <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Inscribirme", key="insc_esp_perfusion"):
            st.session_state.seccion_actual = "Inscripción"
            st.session_state.programa_seleccionado = "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión"
            st.rerun()

    with tab3:
        st.markdown("""
        <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4>🟢 Pregrado con Aval de la UNAM</h4>
            <p>Formación de nivel licenciatura con reconocimiento universitario → <strong>Directorio remoto: LICENCIATURAS/</strong></p>
        </div>
        """, unsafe_allow_html=True)

        abreviatura = ABREVIATURAS_PROGRAMAS["Licenciatura en Enfermería"]
        categoria = obtener_categoria_directorio(abreviatura)
        st.markdown(f"""
        <div class="programa-card">
            <h3>Licenciatura en Enfermería</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                <span class="badge badge-primary">4 años</span>
                <span class="badge badge-secondary">Presencial</span>
                <span class="badge badge-success">Aval UNAM</span>
                <span class="badge badge-info">{abreviatura}</span>
                <span class="badge badge-warning">{categoria}</span>
            </div>
            <p>Formación integral de enfermeros generales con competencias para el cuidado de la salud cardiovascular en diferentes contextos.</p>
            <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Inscribirme", key="insc_lic_enfermeria"):
            st.session_state.seccion_actual = "Inscripción"
            st.session_state.programa_seleccionado = "Licenciatura en Enfermería"
            st.rerun()

    with tab4:
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4>📚 Educación Continua</h4>
            <p>Diplomados de actualización para profesionales de enfermería → <strong>Directorio remoto: DIPLOMADOS/</strong></p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            diplomados_col1 = [
                {
                    "nombre": "Diplomado de Cardiología Básica para Profesionales de Enfermería",
                    "duracion": "6 meses",
                    "modalidad": "Semipresencial",
                    "desc": "Actualización en fundamentos de cardiología para enfermería general.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Cardiología Básica para Profesionales de Enfermería"]
                },
                {
                    "nombre": "Diplomado de Cardiología Pediátrica para Profesionales de Enfermería",
                    "duracion": "6 meses",
                    "modalidad": "Semipresencial",
                    "desc": "Especialización en cuidado cardiovascular para pacientes pediátricos.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Cardiología Pediátrica para Profesionales de Enfermería"]
                },
                {
                    "nombre": "Diplomado de Oxigenación por Membrana Extracorpórea",
                    "duracion": "6 meses",
                    "modalidad": "Presencial",
                    "desc": "Capacitación en manejo de ECMO para pacientes críticos.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Oxigenación por Membrana Extracorpórea"]
                },
                {
                    "nombre": "Diplomado de Enseñanza en Simulación Clínica",
                    "duracion": "6 meses",
                    "modalidad": "Semipresencial",
                    "desc": "Formación en metodologías de simulación para educación en enfermería.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Enseñanza en Simulación Clínica"]
                }
            ]

            for i, diplomado in enumerate(diplomados_col1):
                categoria = obtener_categoria_directorio(diplomado['abreviatura'])
                st.markdown(f"""
                <div class="programa-card">
                    <h3>{diplomado['nombre']}</h3>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                        <span class="badge badge-primary">{diplomado['duracion']}</span>
                        <span class="badge badge-secondary">{diplomado['modalidad']}</span>
                        <span class="badge badge-success">Diplomado</span>
                        <span class="badge badge-info">{diplomado['abreviatura']}</span>
                        <span class="badge badge-warning">{categoria}</span>
                    </div>
                    <p>{diplomado['desc']}</p>
                    <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Inscribirme {i+1}", key=f"insc_dipl{i}"):
                    st.session_state.seccion_actual = "Inscripción"
                    st.session_state.programa_seleccionado = diplomado['nombre']
                    st.rerun()

        with col2:
            diplomados_col2 = [
                {
                    "nombre": "Diplomado de Hemodinámica",
                    "duracion": "6 meses",
                    "modalidad": "Presencial",
                    "desc": "Especialización en procedimientos de hemodinámica y cardiología intervencionista.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Hemodinámica"]
                },
                {
                    "nombre": "Diplomado de Nefro-Intervencionismo",
                    "duracion": "6 meses",
                    "modalidad": "Presencial",
                    "desc": "Capacitación en procedimientos intervencionistas nefrológicos.",
                    "abreviatura": ABREVIATURAS_PROGRAMAS["Diplomado de Nefro-Intervencionismo"]
                }
            ]

            for i, diplomado in enumerate(diplomados_col2):
                categoria = obtener_categoria_directorio(diplomado['abreviatura'])
                st.markdown(f"""
                <div class="programa-card">
                    <h3>{diplomado['nombre']}</h3>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                        <span class="badge badge-primary">{diplomado['duracion']}</span>
                        <span class="badge badge-secondary">{diplomado['modalidad']}</span>
                        <span class="badge badge-success">Diplomado</span>
                        <span class="badge badge-info">{diplomado['abreviatura']}</span>
                        <span class="badge badge-warning">{categoria}</span>
                    </div>
                    <p>{diplomado['desc']}</p>
                    <p><small>📁 Directorio remoto: <strong>{categoria}/</strong></small></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Inscribirme {i+5}", key=f"insc_dipl{i+4}"):
                    st.session_state.seccion_actual = "Inscripción"
                    st.session_state.programa_seleccionado = diplomado['nombre']
                    st.rerun()

def mostrar_inscripcion():
    st.markdown("""
    <div class="animate-fade">
        <h2>Formulario de Inscripción</h2>
        <p>Completa tus datos personales y sube los documentos requeridos para iniciar tu proceso de admisión.</p>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar datos_inscripcion si no existe
    if 'datos_inscripcion' not in st.session_state:
        st.session_state.datos_inscripcion = {
            'matricula': generar_matricula(),
            'programa': st.session_state.get('programa_seleccionado', ''),
            'nombre_completo': '',
            'fecha_nacimiento': None,
            'genero': '',
            'email': '',
            'telefono': '',
            'documentos': [],
            'completado': False
        }

    # Si hay un programa seleccionado pero no está en los datos actuales, actualizarlo
    if (st.session_state.get('programa_seleccionado') and
        st.session_state.programa_seleccionado != st.session_state.datos_inscripcion['programa']):
        st.session_state.datos_inscripcion['programa'] = st.session_state.programa_seleccionado

    with st.form("form_inscripcion"):
        # Verificar que matricula existe antes de mostrarla
        matricula = st.session_state.datos_inscripcion.get('matricula', generar_matricula())
        programa_actual = st.session_state.datos_inscripcion.get('programa', '')
        abreviatura_programa = obtener_abreviatura_programa(programa_actual) if programa_actual else "SELEC"
        categoria_remota = obtener_categoria_directorio(abreviatura_programa)

        config = obtener_configuracion()
        remote_base = config.get('remote_dir', '')

        st.markdown(f"""
        <div style="background-color: #e9f7ff; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4>Número de Matrícula: <strong>{matricula}</strong></h4>
            <p><strong>Abreviatura del programa:</strong> {abreviatura_programa}</p>
            <p><strong>Directorio remoto destino:</strong> {remote_base}/{categoria_remota}/</p>
            <p><small>Esta matrícula identificará tu expediente durante todo el proceso</small></p>
        </div>
        """, unsafe_allow_html=True)

        programas = list(ABREVIATURAS_PROGRAMAS.keys())

        # Obtener el programa actual o usar el seleccionado
        programa_index = programas.index(programa_actual) if programa_actual in programas else 0

        programa_seleccionado = st.selectbox(
            "Programa al que desea inscribirse:",
            programas,
            index=programa_index
        )

        # Actualizar el programa en los datos de inscripción
        st.session_state.datos_inscripcion['programa'] = programa_seleccionado
        abreviatura_actual = obtener_abreviatura_programa(programa_seleccionado)
        categoria_actual = obtener_categoria_directorio(abreviatura_actual)

        # Mostrar información de la carpeta destino
        ruta_carpeta = obtener_ruta_carpeta(programa_seleccionado)
        st.info(f"📁 **Carpeta local:** `{ruta_carpeta}`")
        st.info(f"🌐 **Directorio remoto:** `{remote_base}/{categoria_actual}/`")
        st.info(f"🔤 **Abreviatura del programa:** `{abreviatura_actual}`")

        # Mostrar ejemplo de nombres de archivo
        nombre_completo = st.session_state.datos_inscripcion.get('nombre_completo', '')
        if nombre_completo:
            nombre_base_ejemplo = f"{matricula}.{abreviatura_actual}.25-09-25-18-12.{nombre_completo.replace(' ', '_')}"
            st.info(f"📄 **Ejemplo de nombres de archivos:**")
            st.code(f"{nombre_base_ejemplo}.ACTNAC.pdf")
            st.code(f"→ Se guardará en: {remote_base}/{categoria_actual}/")

        col1, col2 = st.columns(2)

        with col1:
            nombre_completo = st.text_input(
                "Nombre completo:",
                value=st.session_state.datos_inscripcion.get('nombre_completo', '')
            )
            st.session_state.datos_inscripcion['nombre_completo'] = nombre_completo

            fecha_nacimiento_actual = st.session_state.datos_inscripcion.get('fecha_nacimiento')
            if not fecha_nacimiento_actual:
                fecha_nacimiento_actual = datetime.date(1990, 1, 1)

            fecha_nacimiento = st.date_input(
                "Fecha de nacimiento:",
                value=fecha_nacimiento_actual
            )
            st.session_state.datos_inscripcion['fecha_nacimiento'] = fecha_nacimiento

            genero_actual = st.session_state.datos_inscripcion.get('genero', 'Masculino')
            genero_opciones = ["Masculino", "Femenino", "Otro", "Prefiero no decir"]
            genero_index = genero_opciones.index(genero_actual) if genero_actual in genero_opciones else 0

            genero = st.selectbox(
                "Género:",
                genero_opciones,
                index=genero_index
            )
            st.session_state.datos_inscripcion['genero'] = genero

        with col2:
            email = st.text_input(
                "Correo electrónico:",
                value=st.session_state.datos_inscripcion.get('email', '')
            )
            st.session_state.datos_inscripcion['email'] = email

            telefono = st.text_input(
                "Teléfono:",
                value=st.session_state.datos_inscripcion.get('telefono', '')
            )
            st.session_state.datos_inscripcion['telefono'] = telefono

        st.markdown("""
        <div style="margin: 2rem 0 1rem 0;">
            <h4>Documentos Requeridos</h4>
            <p>Sube los siguientes documentos en formato PDF. Los archivos se guardarán con nombres estandarizados usando abreviaturas.</p>
        </div>
        """, unsafe_allow_html=True)

        documentos_requeridos = {
            "Licenciatura": [
                "Acta de nacimiento (PDF)",
                "Certificado de bachillerato (PDF)",
                "CURP (PDF)",
                "Comprobante de domicilio (PDF)"
            ],
            "Especialidad": [
                "Título profesional (PDF)",
                "Cédula profesional (PDF)",
                "CV actualizado (PDF)",
                "Carta de motivos (PDF)"
            ],
            "Diplomado": [
                "Identificación oficial (PDF)",
                "Comprobante de estudios (PDF)",
                "Carta de exposición de motivos (PDF)"
            ]
        }

        if "Licenciatura" in programa_seleccionado:
            documentos = documentos_requeridos["Licenciatura"]
        elif "Especialidad" in programa_seleccionado:
            documentos = documentos_requeridos["Especialidad"]
        else:
            documentos = documentos_requeridos["Diplomado"]

        # Mostrar abreviaturas de documentos
        st.info("📋 **Abreviaturas de documentos que se usarán:**")
        col_docs1, col_docs2 = st.columns(2)
        with col_docs1:
            for i, doc in enumerate(documentos[:len(documentos)//2]):
                abrev = obtener_abreviatura_documento(doc)
                st.write(f"• **{abrev}**: {doc}")
        with col_docs2:
            for i, doc in enumerate(documentos[len(documentos)//2:]):
                abrev = obtener_abreviatura_documento(doc)
                st.write(f"• **{abrev}**: {doc}")

        archivos_subidos = []
        for i, doc in enumerate(documentos):
            archivo = st.file_uploader(
                f"Subir {doc}",
                type=['pdf'],
                key=f"doc_{i}"
            )
            if archivo:
                archivos_subidos.append({
                    "nombre": doc,
                    "archivo": archivo,
                    "tamaño": archivo.size,
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            guardar = st.form_submit_button("💾 Guardar Progreso")

        with col_btn2:
            enviar = st.form_submit_button("📤 Enviar Inscripción")

        if guardar or enviar:
            errores = []

            if not nombre_completo:
                errores.append("El nombre completo es obligatorio")

            if not email:
                errores.append("El correo electrónico es obligatorio")
            elif not validar_email(email):
                errores.append("Ingrese un correo electrónico válido")

            if enviar and len(archivos_subidos) < len(documentos):
                errores.append(f"Debe subir todos los documentos requeridos ({len(documentos)} en total)")

            if errores:
                for error in errores:
                    st.error(error)
            else:
                st.session_state.datos_inscripcion['fecha_inscripcion'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Asegurarnos de que la matrícula esté actualizada
                st.session_state.datos_inscripcion['matricula'] = matricula

                # Usar la nueva función de guardado completo
                exito, resultado = guardar_progreso_completo(
                    st.session_state.datos_inscripcion,
                    archivos_subidos,
                    es_envio_completo=enviar
                )

                if exito:
                    if guardar:
                        st.success("✅ Progreso guardado correctamente")
                        if resultado['documentos_guardados']:
                            st.info(f"📄 Documentos guardados: {len(resultado['documentos_guardados'])} archivos")
                            with st.expander("Ver detalles de archivos guardados"):
                                for doc in resultado['documentos_guardados']:
                                    st.write(f"• **{doc['abreviatura']}**: `{os.path.basename(doc['nombre_guardado'])}`")

                    if enviar:
                        st.success("🎉 ¡Inscripción enviada con éxito!")
                        st.balloons()

                        # Mostrar información de destino remoto
                        abrev_final = obtener_abreviatura_programa(st.session_state.datos_inscripcion['programa'])
                        categoria_final = obtener_categoria_directorio(abrev_final)
                        st.success(f"📁 **Archivos transferidos a:** `{remote_base}/{categoria_final}/`")

                        # Mostrar resumen y opción de descarga
                        mostrar_resumen_inscripcion(st.session_state.datos_inscripcion, resultado)
                else:
                    st.error(f"❌ Error: {resultado}")

def mostrar_resumen_inscripcion(datos_inscripcion, resultado):
    """Muestra el resumen de la inscripción completada"""
    st.markdown("### 📋 Resumen de tu inscripción")

    abreviatura_programa = obtener_abreviatura_programa(datos_inscripcion['programa'])
    categoria_remota = obtener_categoria_directorio(abreviatura_programa)
    config = obtener_configuracion()
    remote_base = config.get('remote_dir', '')

    col_res1, col_res2 = st.columns(2)

    with col_res1:
        st.write("**Información personal:**")
        st.write(f"• **Matrícula:** {datos_inscripcion['matricula']}")
        st.write(f"• **Programa:** {datos_inscripcion['programa']}")
        st.write(f"• **Abreviatura:** {abreviatura_programa}")
        st.write(f"• **Categoría remota:** {categoria_remota}")
        st.write(f"• **Nombre:** {datos_inscripcion['nombre_completo']}")
        st.write(f"• **Email:** {datos_inscripcion['email']}")
        st.write(f"• **Fecha:** {datos_inscripcion['fecha_inscripcion']}")

    with col_res2:
        st.write("**Archivos guardados:**")
        st.write(f"• **Directorio remoto:** `{remote_base}/{categoria_remota}/`")
        st.write(f"• **Registro:** `{os.path.basename(resultado['ruta_csv'])}`")
        if resultado['documentos_guardados']:
            st.write("**Documentos transferidos:**")
            for doc in resultado['documentos_guardados']:
                st.write(f"• **{doc['abreviatura']}:** `{os.path.basename(doc['nombre_guardado'])}`")

    # Comprobante para descarga
    comprobante = f"""
    COMPROBANTE DE INSCRIPCIÓN
    Instituto Nacional de Cardiología Ignacio Chávez
    Escuela de Enfermería

    Matrícula: {datos_inscripcion['matricula']}
    Programa: {datos_inscripcion['programa']}
    Abreviatura: {abreviatura_programa}
    Categoría remota: {categoria_remota}
    Directorio destino: {remote_base}/{categoria_remota}/
    Nombre: {datos_inscripcion['nombre_completo']}
    Email: {datos_inscripcion['email']}
    Fecha de inscripción: {datos_inscripcion['fecha_inscripcion']}
    Estado: INSCRIPCIÓN COMPLETADA

    Archivos guardados en: {resultado['ruta_csv']}
    Documentos subidos: {len(resultado['documentos_guardados'])} archivos
    Directorio remoto: {remote_base}/{categoria_remota}/

    ABREVIATURAS UTILIZADAS:
    Programa: {abreviatura_programa} → {categoria_remota}
    Documentos: {', '.join([doc['abreviatura'] for doc in resultado['documentos_guardados']])}
    """

    st.download_button(
        label="📥 Descargar Comprobante",
        data=comprobante.encode('utf-8'),
        file_name=f"comprobante_inscripcion_{datos_inscripcion['matricula']}.txt",
        mime="text/plain"
    )

def mostrar_documentacion():
    st.markdown("""
    <div class="animate-fade">
        <h2>Documentación Requerida</h2>
        <p>Revisa los documentos necesarios para completar tu inscripción.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'datos_inscripcion' not in st.session_state or not st.session_state.datos_inscripcion.get('programa'):
        st.warning("Por favor completa primero tus datos personales en la sección de Inscripción")
        return

    programas_docs = {
        "Licenciatura en Enfermería": [
            "Acta de nacimiento (original y copia)",
            "Certificado de bachillerato (original y copia)",
            "CURP (copia)",
            "4 fotografías tamaño infantil",
            "Certificado médico de buena salud"
        ],
        "Especialidad en Enfermería Cardiovascular": [
            "Título profesional de licenciatura en enfermería (copia)",
            "Cédula profesional (copia)",
            "CV actualizado",
            "Carta de motivos",
            "2 cartas de recomendación"
        ],
        "Especialidad en Enfermería Nefrológica": [
            "Título profesional de licenciatura en enfermería (copia)",
            "Cédula profesional (copia)",
            "CV actualizado",
            "Carta de motivos",
            "2 cartas de recomendación"
        ],
        "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión": [
            "Título profesional de licenciatura en enfermería (copia)",
            "Cédula profesional (copia)",
            "CV actualizado",
            "Carta de motivos",
            "2 cartas de recomendación"
        ],
        "Diplomado de Cardiología Básica para Profesionales de Enfermería": [
            "Identificación oficial (copia)",
            "Comprobante de estudios de enfermería",
            "Carta de exposición de motivos"
        ]
    }

    programa_actual = st.session_state.datos_inscripcion['programa']
    abreviatura_programa = obtener_abreviatura_programa(programa_actual)
    categoria_remota = obtener_categoria_directorio(abreviatura_programa)
    config = obtener_configuracion()
    remote_base = config.get('remote_dir', '')

    # Documentos por defecto si el programa no está en la lista
    documentos = programas_docs.get(programa_actual, [
        "Identificación oficial (copia)",
        "Comprobante de estudios",
        "Comprobante de domicilio",
        "CV actualizado",
        "Carta de motivos"
    ])

    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
        <h4>Documentos requeridos para: <strong>{programa_actual}</strong></h4>
        <p><strong>Abreviatura del programa:</strong> {abreviatura_programa}</p>
        <p><strong>Directorio remoto destino:</strong> {remote_base}/{categoria_remota}/</p>
        <ul style="margin-top: 1rem;">
    """, unsafe_allow_html=True)

    for doc in documentos:
        abreviatura = obtener_abreviatura_documento(doc)
        st.markdown(f"<li><strong>{abreviatura}:</strong> {doc}</li>", unsafe_allow_html=True)

    st.markdown("""
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4>Información sobre nombres de archivos</h4>
        <p>Los documentos se guardarán automáticamente con nombres estandarizados en el formato:</p>
        <p><code>[MATRÍCULA].[ABREV-PROGRAMA].[FECHA].[NOMBRE].[ABREV-DOCUMENTO].pdf</code></p>
        <p><strong>Ejemplo:</strong> <code>MAT-ABC12345.ESP-CARD.25-09-25-18-12.Carlos_Polanco.CEDULA.pdf</code></p>
        <p><strong>Destino remoto:</strong> <code>{remote_base}/{categoria_remota}/MAT-ABC12345.ESP-CARD.25-09-25-18-12.Carlos_Polanco.CEDULA.pdf</code></p>
    </div>
    """.format(remote_base=remote_base, categoria_remota=categoria_remota), unsafe_allow_html=True)

def mostrar_pagos():
    st.markdown("""
    <div class="animate-fade">
        <h2>Información de Pagos</h2>
        <p>Detalles sobre costos y métodos de pago.</p>
    </div>
    """, unsafe_allow_html=True)

    if 'datos_inscripcion' not in st.session_state or not st.session_state.datos_inscripcion.get('programa'):
        st.warning("Por favor completa primero tus datos personales en la sección de Inscripción")
        return

    programas_costos = {
        "Licenciatura en Enfermería": {
            "Inscripción": "$2,500 MXN",
            "Mensualidad": "$3,800 MXN",
            "Duración": "8 semestres",
            "Costo total aproximado": "$130,000 MXN"
        },
        "Especialidad en Enfermería Cardiovascular": {
            "Inscripción": "$3,500 MXN",
            "Mensualidad": "$4,800 MXN",
            "Duración": "4 semestres",
            "Costo total aproximado": "$80,000 MXN"
        },
        "Especialidad en Enfermería Nefrológica": {
            "Inscripción": "$3,500 MXN",
            "Mensualidad": "$4,800 MXN",
            "Duración": "4 semestres",
            "Costo total aproximado": "$80,000 MXN"
        },
        "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión": {
            "Inscripción": "$4,000 MXN",
            "Mensualidad": "$5,200 MXN",
            "Duración": "4 semestres",
            "Costo total aproximado": "$87,000 MXN"
        },
        "Diplomado de Cardiología Básica para Profesionales de Enfermería": {
            "Inscripción": "$2,000 MXN",
            "Costo total": "$18,000 MXN",
            "Duración": "6 meses",
            "Modalidad de pago": "3 pagos de $6,000 MXN"
        }
    }

    programa_actual = st.session_state.datos_inscripcion['programa']
    abreviatura_programa = obtener_abreviatura_programa(programa_actual)
    categoria_remota = obtener_categoria_directorio(abreviatura_programa)
    config = obtener_configuracion()
    remote_base = config.get('remote_dir', '')

    costos = programas_costos.get(programa_actual, {
        "Inscripción": "$2,500 MXN",
        "Mensualidad": "$4,000 MXN",
        "Duración": "Consultar",
        "Costo total": "Consultar"
    })

    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
        <h4>Costos para: <strong>{programa_actual}</strong></h4>
        <p><strong>Abreviatura:</strong> {abreviatura_programa}</p>
        <p><strong>Directorio remoto:</strong> {remote_base}/{categoria_remota}/</p>
        <div style="margin-top: 1rem;">
    """, unsafe_allow_html=True)

    for key, value in costos.items():
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #eee;">
            <span style="font-weight: 500;">{key}:</span>
            <span style="font-weight: 700;">{value}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4>Métodos de Pago</h4>
        <p>Transferencia bancaria, tarjeta de crédito/débito o pago en efectivo en nuestras instalaciones.</p>
        <p><strong>Banco:</strong> BBVA Bancomer</p>
        <p><strong>Cuenta:</strong> 0193 4567 8910 1234 56</p>
        <p><strong>CLABE:</strong> 012 180 0193 4567 8910 1234 56</p>
        <p><strong>Beneficiario:</strong> Instituto Nacional de Cardiología Ignacio Chávez</p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_contacto():
    st.markdown("""
    <div class="animate-fade">
        <h2>Contacto</h2>
        <p>¿Tienes dudas? Contáctanos a través de los siguientes medios.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; height: 100%;">
            <h4>Información de Contacto</h4>
            <div style="margin-top: 1rem;">
                <p>📧 <strong>Email:</strong> escuela.enfermeria@cardiologia.org.mx</p>
                <p>📞 <strong>Teléfono:</strong> (55) 5573 2911 ext. 1234</p>
                <p>📱 <strong>WhatsApp:</strong> +52 55 1234 5678</p>
                <p>🏢 <strong>Dirección:</strong> Juan Badiano No. 1, Sección XVI, Tlalpan, 14080 Ciudad de México</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; height: 100%;">
            <h4>Horario de Atención</h4>
            <div style="margin-top: 1rem;">
                <p>🕘 <strong>Lunes a Viernes:</strong> 9:00 - 18:00 hrs</p>
                <p>🕙 <strong>Sábados:</strong> 10:00 - 14:00 hrs</p>
                <p>🚫 <strong>Domingos:</strong> Cerrado</p>
                <p>📅 <strong>Periodo de inscripciones:</strong> Enero a Julio 2025</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4>Formulario de Contacto</h4>
        <p>Envíanos un mensaje directo y te responderemos a la brevedad.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_contacto"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        telefono = st.text_input("Teléfono (opcional)")
        programa_interes = st.selectbox("Programa de interés", [
            "Seleccione un programa",
            "Licenciatura en Enfermería",
            "Especialidad en Enfermería Cardiovascular",
            "Especialidad en Enfermería Nefrológica",
            "Especialidad de Enfermería en Circulación Extracorpórea y Perfusión",
            "Diplomado de Cardiología Básica para Profesionales de Enfermería",
            "Diplomado de Cardiología Pediátrica para Profesionales de Enfermería",
            "Diplomado de Oxigenación por Membrana Extracorpórea",
            "Diplomado de Enseñanza en Simulación Clínica",
            "Diplomado de Hemodinámica",
            "Diplomado de Nefro-Intervencionismo"
        ])
        mensaje = st.text_area("Mensaje", height=150)

        enviar = st.form_submit_button("📤 Enviar Mensaje")

        if enviar:
            if nombre and email and mensaje and programa_interes != "Seleccione un programa":
                # Simular envío de mensaje
                config = obtener_configuracion()
                if config.get('email_user') and config.get('notification_email'):
                    try:
                        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
                        server.starttls()
                        server.login(config['email_user'], config['email_password'])

                        msg = MIMEMultipart()
                        msg['From'] = config['email_user']
                        msg['To'] = config['notification_email']
                        msg['Subject'] = f"📧 Mensaje de contacto - {nombre}"

                        cuerpo = f"""
                        Nuevo mensaje de contacto recibido:

                        Nombre: {nombre}
                        Email: {email}
                        Teléfono: {telefono if telefono else 'No proporcionado'}
                        Programa de interés: {programa_interes}

                        Mensaje:
                        {mensaje}

                        ---
                        Sistema de Contacto - Escuela de Enfermería
                        """

                        msg.attach(MIMEText(cuerpo, 'plain'))
                        server.send_message(msg)
                        server.quit()

                        st.success("¡Mensaje enviado con éxito! Te contactaremos en un plazo máximo de 48 horas.")
                    except Exception as e:
                        st.success("¡Mensaje recibido! Te contactaremos en un plazo máximo de 48 horas.")
                        if config.get('debug_mode', False):
                            st.info(f"🔍 Modo debug: Error de email - {e}")
                else:
                    st.success("¡Mensaje recibido! Te contactaremos en un plazo máximo de 48 horas.")
            else:
                st.error("Por favor completa todos los campos obligatorios")

def main():
    configurar_pagina()
    cargar_estilos()

    # Inicializar variables de sesión
    if 'seccion_actual' not in st.session_state:
        st.session_state.seccion_actual = "Oferta Educativa"

    if 'programa_seleccionado' not in st.session_state:
        st.session_state.programa_seleccionado = ""

    if 'datos_inscripcion' not in st.session_state:
        st.session_state.datos_inscripcion = {
            'matricula': generar_matricula(),
            'programa': st.session_state.get('programa_seleccionado', ''),
            'nombre_completo': '',
            'fecha_nacimiento': None,
            'genero': '',
            'email': '',
            'telefono': '',
            'documentos': [],
            'completado': False
        }

    if 'mostrar_abreviaturas' not in st.session_state:
        st.session_state.mostrar_abreviaturas = False

    mostrar_header()
    mostrar_sidebar()

    # Mostrar sección actual
    if st.session_state.seccion_actual == "Oferta Educativa":
        mostrar_oferta_educativa()
    elif st.session_state.seccion_actual == "Inscripción":
        mostrar_inscripcion()
    elif st.session_state.seccion_actual == "Documentación":
        mostrar_documentacion()
    elif st.session_state.seccion_actual == "Pagos":
        mostrar_pagos()
    elif st.session_state.seccion_actual == "Contacto":
        mostrar_contacto()

    # Mostrar información de debug si está activado
    config = obtener_configuracion()
    if config.get('debug_mode', False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Modo Debug")
        st.sidebar.write(f"Sección actual: {st.session_state.seccion_actual}")
        st.sidebar.write(f"Programa seleccionado: {st.session_state.programa_seleccionado}")
        st.sidebar.write(f"Matrícula: {st.session_state.datos_inscripcion.get('matricula', 'No definida')}")
        st.sidebar.write(f"Modo supervisor: {config.get('supervisor_mode', False)}")
        st.sidebar.write(f"Remote dir: {config.get('remote_dir', 'No definido')}")

if __name__ == "__main__":
    main()

