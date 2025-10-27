import pandas as pd
import os

def crear_enfermedades_medicamentos():
    """
    Crea CSV de enfermedades-medicamentos basado en:
    - Patologías veterinarias comunes
    - Principios activos que REALMENTE tienes en Cimavet
    """
    
    # Define enfermedades comunes y sus principios activos recomendados
    enfermedades_data = [
        # PARASITOLOGÍA
        {
            'enfermedad': 'Pulgas',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Fipronilo;Imidacloprid;Fluralaner;Fipronil;Selamectina',
            'indicaciones': 'Infestación por pulgas (Ctenocephalides). Tratamiento y prevención.',
            'contraindicaciones': 'Hipersensibilidad conocida al principio activo',
            'notas': 'Fipronilo es el más disponible. Aplicar mensual o según producto.'
        },
        {
            'enfermedad': 'Pulgas',
            'categoria': 'Parasitología',
            'especie': 'Gato',
            'principios_activos': 'Fipronilo;Imidacloprid;Selamectina;Fluralaner',
            'indicaciones': 'Infestación por pulgas en gatos',
            'contraindicaciones': 'Hipersensibilidad. Evitar productos no específicos para gatos',
            'notas': 'Usar solo productos formulados para gatos'
        },
        {
            'enfermedad': 'Garrapatas',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Fipronilo;Permetrina;Imidacloprid;Fluralaner;Deltametrina',
            'indicaciones': 'Infestación por garrapatas. Prevención de enfermedades transmitidas por garrapatas.',
            'contraindicaciones': 'Hipersensibilidad. En gatos evitar piretroides',
            'notas': 'Aplicación mensual. Considera desparasitantes periódicos.'
        },
        {
            'enfermedad': 'Sarna sarcóptica',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Ivermectina;Milbemicina Oxima;Selamectina;Moxidectina;Fluralaner',
            'indicaciones': 'Sarcoptes scabiei. Causa picazón severa y alopecia.',
            'contraindicaciones': 'Razas sensibles a ivermectina (Collie, Shetland). Menores de 6 semanas.',
            'notas': 'Tratar contactos cercanos. Repetir en 7-14 días según producto.'
        },
        {
            'enfermedad': 'Sarna sarcóptica',
            'categoria': 'Parasitología',
            'especie': 'Gato',
            'principios_activos': 'Milbemicina Oxima;Selamectina;Moxidectina;Ivermectina',
            'indicaciones': 'Sarcoptes scabiei en gatos. Menos frecuente que en perros.',
            'contraindicaciones': 'Hipersensibilidad. Gatos sensibles a ivermectina',
            'notas': 'Preferir milbemicina u otros macrolídicos en gatos'
        },
        {
            'enfermedad': 'Nematodos intestinales',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Prazicuantel;Pirantel Embonato;Febantel;Moxidectina;Milbemicina Oxima',
            'indicaciones': 'Ascaris, Uncinaria, Trichuris. Desparasitación intestinal.',
            'contraindicaciones': 'Hipersensibilidad. Animales muy debilitados',
            'notas': 'Repetir cada 3 meses. Cachorros cada 2 semanas hasta 3 meses.'
        },
        {
            'enfermedad': 'Nematodos intestinales',
            'categoria': 'Parasitología',
            'especie': 'Gato',
            'principios_activos': 'Prazicuantel;Pirantel Embonato;Moxidectina;Milbemicina Oxima;Emodepsida',
            'indicaciones': 'Desparasitación en gatos',
            'contraindicaciones': 'Hipersensibilidad',
            'notas': 'Repetir según recomendaciones veterinarias'
        },
        
        # DERMATOLOGÍA
        {
            'enfermedad': 'Otitis externa',
            'categoria': 'Dermatología',
            'especie': 'Perro',
            'principios_activos': 'Enrofloxacino;Marbofloxacino;Clindamicina Hidrocloruro;Metronidazol',
            'indicaciones': 'Inflamación del conducto auditivo. Infecciones bacterianas u hongos.',
            'contraindicaciones': 'Tímpano perforado con estos sistémicos',
            'notas': 'Limpiar conducto antes del tratamiento. Considerar causa subyacente.'
        },
        {
            'enfermedad': 'Otitis externa',
            'categoria': 'Dermatología',
            'especie': 'Gato',
            'principios_activos': 'Enrofloxacino;Marbofloxacino;Clindamicina Hidrocloruro;Metronidazol',
            'indicaciones': 'Otitis en gatos',
            'contraindicaciones': 'Tímpano perforado',
            'notas': 'Menos frecuente que en perros. Investigar causa (ácaros, hongos, etc).'
        },
        {
            'enfermedad': 'Dermatitis alérgica',
            'categoria': 'Dermatología',
            'especie': 'Perro',
            'principios_activos': 'Prednisolona;Dexametasona Fosfato Sodio;Carprofeno;Meloxicam;Oclacitinib Maleato',
            'indicaciones': 'Dermatitis atópica. Alergia a alimentos o ambiente. Reacciones de hipersensibilidad.',
            'contraindicaciones': 'Infecciones bacterianas activas sin tratar. Diabetes descontrolada.',
            'notas': 'Identificar causa. Corticoides a dosis bajas para crónico. Considerar ciclosporina.'
        },
        {
            'enfermedad': 'Dermatitis alérgica',
            'categoria': 'Dermatología',
            'especie': 'Gato',
            'principios_activos': 'Prednisolona;Dexametasona Fosfato Sodio;Meloxicam',
            'indicaciones': 'Dermatitis en gatos',
            'contraindicaciones': 'Infecciones activas',
            'notas': 'Gatos son sensibles a muchos fármacos. Preferir prednisolona.'
        },
        
        # INFECTOLOGÍA
        {
            'enfermedad': 'Infección bacteriana sistémica',
            'categoria': 'Infectología',
            'especie': 'Perro',
            'principios_activos': 'Amoxicilina Trihidrato;Clavulanato Potasio;Enrofloxacino;Marbofloxacino;Cefalexina Monohidrato;Clindamicina Hidrocloruro',
            'indicaciones': 'Infecciones bacterianas (pneumonía, pielonefritis, etc). Realizar cultivo si es posible.',
            'contraindicaciones': 'Alergia a beta-lactámicos. Hipersensibilidad al fármaco.',
            'notas': 'Primera línea: Amoxicilina-clavulánico. Ajustar según cultivo y sensibilidad.'
        },
        {
            'enfermedad': 'Infección bacteriana sistémica',
            'categoria': 'Infectología',
            'especie': 'Gato',
            'principios_activos': 'Amoxicilina Trihidrato;Clavulanato Potasio;Enrofloxacino;Marbofloxacino;Clindamicina Hidrocloruro',
            'indicaciones': 'Infecciones bacterianas en gatos',
            'contraindicaciones': 'Alergia a betalactámicos',
            'notas': 'Gatos sensibles. Realizar cultivo. Considerar dosis adaptadas a peso corporal.'
        },
        {
            'enfermedad': 'Infección urinaria',
            'categoria': 'Infectología',
            'especie': 'Perro',
            'principios_activos': 'Amoxicilina Trihidrato;Clavulanato Potasio;Enrofloxacino;Marbofloxacino;Cefalexina Monohidrato',
            'indicaciones': 'Cistitis bacteriana. Pielonefritis. Requiere cultivo de orina.',
            'contraindicaciones': 'Insuficiencia renal severa (ajustar dosis)',
            'notas': 'Realizar cultivo y antibiograma. Tratamiento 7-14 días mínimo.'
        },
        {
            'enfermedad': 'Infección urinaria',
            'categoria': 'Infectología',
            'especie': 'Gato',
            'principios_activos': 'Amoxicilina Trihidrato;Clavulanato Potasio;Enrofloxacino;Marbofloxacino',
            'indicaciones': 'Cistitis en gatos',
            'contraindicaciones': 'Insuficiencia renal',
            'notas': 'Común en gatos. Investigar causa subyacente (cristales, obstrucción).'
        },
        
        # GASTROENTEROLOGÍA
        {
            'enfermedad': 'Gastroenteritis',
            'categoria': 'Gastroenterología',
            'especie': 'Perro',
            'principios_activos': 'Metronidazol;Clindamicina Hidrocloruro;Enrofloxacino;Marbofloxacino',
            'indicaciones': 'Diarrea bacteriana o parasitaria. Inflamación gastrointestinal. IBD canina.',
            'contraindicaciones': 'Embarazo (metronidazol). Lactancia.',
            'notas': 'Soporte: dieta blanda, probióticos. Metronidazol si es protozoaria.'
        },
        {
            'enfermedad': 'Gastroenteritis',
            'categoria': 'Gastroenterología',
            'especie': 'Gato',
            'principios_activos': 'Metronidazol;Clindamicina Hidrocloruro;Enrofloxacino;Marbofloxacino',
            'indicaciones': 'Gastroenteritis en gatos',
            'contraindicaciones': 'Embarazo. Lactancia.',
            'notas': 'IBD felina. Considerar causas (alimento, estrés, infecciones).'
        },
        
        # ANALGESIA
        {
            'enfermedad': 'Dolor/Inflamación articular',
            'categoria': 'Analgesia',
            'especie': 'Perro',
            'principios_activos': 'Meloxicam;Carprofeno;Robenacoxib;Firocoxib;Tramadol Hidrocloruro',
            'indicaciones': 'Osteoartritis. Dolor postquirúrgico. Displasia de cadera. AINE recomendados.',
            'contraindicaciones': 'Insuficiencia renal/hepática. Úlcera gástrica. Menores de 8 semanas.',
            'notas': 'Usar protector gástrico si es crónico. Considerar condroprotectores.'
        },
        {
            'enfermedad': 'Dolor/Inflamación articular',
            'categoria': 'Analgesia',
            'especie': 'Gato',
            'principios_activos': 'Meloxicam;Tramadol Hidrocloruro;Robenacoxib',
            'indicaciones': 'Dolor articular en gatos. Osteoartritis.',
            'contraindicaciones': 'Insuficiencia renal',
            'notas': 'Meloxicam es preferido. Gatos menos toleran AINE que perros. Dosis adaptadas.'
        },
        
        # CARDIOLOGÍA
        {
            'enfermedad': 'Insuficiencia cardíaca',
            'categoria': 'Cardiología',
            'especie': 'Perro',
            'principios_activos': 'Pimobendan;Benazepril Hidrocloruro;Doxorrubicina',
            'indicaciones': 'Enfermedad degenerativa de válvula mitral. Cardiomiopatía. Insuficiencia cardíaca congestiva.',
            'contraindicaciones': 'Hipotensión severa. Hipertrofia asimétrica del tabique (pimobendan).',
            'notas': 'Pimobendan mejora contractilidad. Benazepril reduce presión. Requiere seguimiento.'
        },
        
        # ENDOCRINOLOGÍA
        {
            'enfermedad': 'Hipertiroidismo',
            'categoria': 'Endocrinología',
            'especie': 'Gato',
            'principios_activos': 'Tiamazol;Levotiroxina Sodica',
            'indicaciones': 'Hipertiroidismo felino. Control de hormona tiroidea elevada.',
            'contraindicaciones': 'Hipersensibilidad. Anemia severa.',
            'notas': 'Tiamazol reduce síntesis. Requiere monitoreo regular de T3/T4.'
        },
        {
            'enfermedad': 'Diabetes mellitus',
            'categoria': 'Endocrinología',
            'especie': 'Perro',
            'principios_activos': 'Insulina',
            'indicaciones': 'Diabetes mellitus tipo 1. Hiperglucemia.',
            'contraindicaciones': 'Hipoglucemia severa',
            'notas': 'Requiere inyecciones diarias. Dieta y ejercicio importante.'
        },
        
        # NEUROLOGÍA
        {
            'enfermedad': 'Convulsiones/Epilepsia',
            'categoria': 'Neurología',
            'especie': 'Perro',
            'principios_activos': 'Fenobarbital;Levotiroxina Sodica;Trilostano',
            'indicaciones': 'Epilepsia idiopática. Crisis convulsivas.',
            'contraindicaciones': 'Hepatopatía severa. Alergia al fármaco.',
            'notas': 'Fenobarbital es gold standard. Requiere monitoreo hepático.'
        },
        
        # REPRODUCCIÓN
        {
            'enfermedad': 'Control de celo',
            'categoria': 'Reproducción',
            'especie': 'Perra',
            'principios_activos': 'Medroxiprogesterona Acetato',
            'indicaciones': 'Supresión de celo. Proestro. Debe usarse ANTES del celo.',
            'contraindicaciones': 'Embarazo confirmado. Hipersensibilidad.',
            'notas': 'Usar solo si animal está en proestro. Eficacia limitada en estro establecido.'
        }
    ]
    
    # Crea DataFrame
    df_enfermedades = pd.DataFrame(enfermedades_data)
    
    # Crea carpeta si no existe
    os.makedirs('data/raw', exist_ok=True)
    
    # Guarda CSV
    output_path = 'data/raw/enfermedades_medicamentos_cimavet.csv'
    df_enfermedades.to_csv(output_path, index=False, encoding='utf-8')
    
    print("\n" + "="*80)
    print("✅ CSV DE ENFERMEDADES-MEDICAMENTOS CREADO")
    print("="*80)
    print(f"Total de patologías: {len(df_enfermedades)}")
    print(f"Guardado en: {output_path}\n")
    
    # Análisis
    print("📊 RESUMEN:")
    print(f"  - Perros: {len(df_enfermedades[df_enfermedades['especie']=='Perro'])} patologías")
    print(f"  - Gatos: {len(df_enfermedades[df_enfermedades['especie']=='Gato'])} patologías")
    print(f"  - Categorías: {df_enfermedades['categoria'].nunique()} tipos\n")
    
    print("📋 PATOLOGÍAS POR CATEGORÍA:")
    for cat in df_enfermedades['categoria'].unique():
        count = len(df_enfermedades[df_enfermedades['categoria']==cat])
        print(f"  - {cat}: {count}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    crear_enfermedades_medicamentos()