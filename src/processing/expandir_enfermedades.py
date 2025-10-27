import pandas as pd
import os

def expandir_enfermedades():
    """
    Expande el CSV de enfermedades añadiendo 15 nuevas patologías
    que cubren los 580 medicamentos sin mapeo
    """
    
    # Enfermedades NUEVAS que añadimos
    nuevas_enfermedades = [
        # INMUNIZACIÓN/VACUNACIÓN (cubre 203 medicamentos)
        {
            'enfermedad': 'Inmunización - Moquillo/Parvovirus',
            'categoria': 'Inmunización',
            'especie': 'Perro',
            'principios_activos': 'Virus del Moquillo Canino;Parvovirus Canino;Vivo Atenuado;Inactivada',
            'indicaciones': 'Vacunación contra moquillo y parvovirus canino. Protección ante virus respiratorios.',
            'contraindicaciones': 'Animales inmunodeprimidos. Embarazo. Enfermedad activa.',
            'notas': 'Vacunas polivalentes disponibles. Protección de 1 año. Refuerzo anual recomendado.'
        },
        {
            'enfermedad': 'Inmunización - Leptospira',
            'categoria': 'Inmunización',
            'especie': 'Perro',
            'principios_activos': 'Leptospira Interrogans;Inactivada;Serovariedad Canicola',
            'indicaciones': 'Vacunación contra Leptospira. Protección de enfermedades zoonóticas.',
            'contraindicaciones': 'Enfermedad activa. Inmunodepresión.',
            'notas': 'Importante en zonas de riesgo. Vacunas combinadas disponibles.'
        },
        {
            'enfermedad': 'Inmunización - Rabia',
            'categoria': 'Inmunización',
            'especie': 'Perro',
            'principios_activos': 'Virus Rabia;Inactivado',
            'indicaciones': 'Vacunación contra rabia. Obligatorio en muchas regiones.',
            'contraindicaciones': 'Enfermedad aguda. Inmunodepresión severa.',
            'notas': 'Dosis inicial + refuerzo a 1 año. Luego cada 3 años.'
        },
        {
            'enfermedad': 'Inmunización - Respiratorio',
            'categoria': 'Inmunización',
            'especie': 'Perro',
            'principios_activos': 'Bordetella Bronchiseptica;Parainfluenza Canina;Adenovirus Canino',
            'indicaciones': 'Vacunación contra tos de las perreras y virus respiratorios.',
            'contraindicaciones': 'Enfermedad activa.',
            'notas': 'Importante en perros con exposición a otros perros (guarderías, parques).'
        },
        {
            'enfermedad': 'Inmunización - Felina',
            'categoria': 'Inmunización',
            'especie': 'Gato',
            'principios_activos': 'Panleucopenia Felina;Calicivirus Felino;Vivo Atenuado;Inactivada',
            'indicaciones': 'Vacunación felina trivalente. Protección contra enfermedades vírales.',
            'contraindicaciones': 'Embarazo. Enfermedad activa.',
            'notas': 'Refuerzo anual. Vacunas combinadas (FVRCP) disponibles.'
        },
        
        # SEDACIÓN/ANESTESIA
        {
            'enfermedad': 'Sedación prequirúrgica',
            'categoria': 'Anestesia',
            'especie': 'Perro',
            'principios_activos': 'Medetomidina Hidrocloruro;Dexmedetomidina;Acepromazina;Xilacina',
            'indicaciones': 'Sedación para procedimientos. Tranquilización previa a anestesia.',
            'contraindicaciones': 'Enfermedad cardíaca severa. Hipertensión. Diabetes descontrolada.',
            'notas': 'Medetomidina reversible con atipamezol. Requiere monitoreo.'
        },
        {
            'enfermedad': 'Anestesia general',
            'categoria': 'Anestesia',
            'especie': 'Perro',
            'principios_activos': 'Propofol;Ketamina;Tiletamina;Alfaxalona;Isoflurano;Sevoflurano',
            'indicaciones': 'Anestesia para cirugía. Anestesia inhalatoria.',
            'contraindicaciones': 'Hipotensión. Insuficiencia cardiopulmonar. Hipocalcemia.',
            'notas': 'Anestesias inyectables vs inhalatorias. Requiere asistencia veterinaria especializada.'
        },
        
        # ANTIPARASITARIOS ORALES ESPECÍFICOS
        {
            'enfermedad': 'Pulgas/Garrapatas orales',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Afoxolaner;Lotilaner;Spinosad;Nitenpiram',
            'indicaciones': 'Tratamiento de pulgas y garrapatas con comprimidos orales. Prevención mensual.',
            'contraindicaciones': 'Hipersensibilidad. Gestación no confirmada.',
            'notas': 'Nexgard/Frontpro (Afoxolaner), Credelio (Lotilaner), Comfortis (Spinosad).'
        },
        {
            'enfermedad': 'Pulgas/Garrapatas orales',
            'categoria': 'Parasitología',
            'especie': 'Gato',
            'principios_activos': 'Lotilaner;Spinosad;Lufenuron;Indoxacarb',
            'indicaciones': 'Antiparasitarios orales para gatos. Prevención mensual.',
            'contraindicaciones': 'Hipersensibilidad.',
            'notas': 'Credelio (Lotilaner) oral en gatos. Activyl (Indoxacarb) spot-on.'
        },
        
        # ANTIARRÍTMICOS Y CARDÍACOS AVANZADOS
        {
            'enfermedad': 'Arritmias cardíacas',
            'categoria': 'Cardiología',
            'especie': 'Perro',
            'principios_activos': 'Diltiazem;Atenolol;Propranolol;Digoxina',
            'indicaciones': 'Control de arritmias. Cardiopatía dilatada. Fibrilación auricular.',
            'contraindicaciones': 'Bloqueo AV. Bradicardia severa. Insuficiencia cardíaca descompensada.',
            'notas': 'Requiere ECG y seguimiento. Dosificación ajustada por clínica.'
        },
        
        # INSUFICIENCIA CARDÍACA AVANZADA
        {
            'enfermedad': 'Edema/Congestión cardíaca',
            'categoria': 'Cardiología',
            'especie': 'Perro',
            'principios_activos': 'Furosemida;Torasemida;Espironolactona;Clorotiazida',
            'indicaciones': 'Tratamiento del edema pulmonar. Ascitis. Insuficiencia cardíaca congestiva.',
            'contraindicaciones': 'Deshidratación severa. Insuficiencia renal avanzada.',
            'notas': 'Diuréticos de asa (furosemida, torasemida). Ahorradores de potasio (espironolactona).'
        },
        
        # ENFERMEDADES INMUNOMEDIADAS
        {
            'enfermedad': 'Enfermedad inmunomediada',
            'categoria': 'Inmunología',
            'especie': 'Perro',
            'principios_activos': 'Ciclosporina;Azatioprina;Corticoides',
            'indicaciones': 'Enfermedades autoinmunes. Anemias hemolíticas. Trombocitopenia inmunomediada.',
            'contraindicaciones': 'Infecciones activas. Neoplasia sospechada.',
            'notas': 'Ciclosporina efectiva en muchas condiciones. Requiere monitoreo.'
        },
        
        # DEFICIENCIAS VITAMÍNICAS
        {
            'enfermedad': 'Deficiencia vitamínica B12',
            'categoria': 'Nutrición',
            'especie': 'Perro',
            'principios_activos': 'Cianocobalamina;Butafosfan',
            'indicaciones': 'Deficiencia de B12. Anemia macrocítica. Problemas neurológicos.',
            'contraindicaciones': 'Hipersensibilidad.',
            'notas': 'Inyecciones mensuales típicamente. Complementa con dieta adecuada.'
        },
        
        # CONTROL DE NÁUSEAS
        {
            'enfermedad': 'Náuseas/Vómitos',
            'categoria': 'Gastroenterología',
            'especie': 'Perro',
            'principios_activos': 'Maropitant;Metoclopramida;Metadona',
            'indicaciones': 'Prevención de vómitos. Postoperatorio. Quimioterapia. Cinetosis.',
            'contraindicaciones': 'Obstrucción intestinal (maropitant).',
            'notas': 'Maropitant inyectable es más efectivo. Metoclopramida oral.'
        },
        
        # INFECCIONES PARASITARIAS ESPECÍFICAS
        {
            'enfermedad': 'Leishmaniasis',
            'categoria': 'Parasitología',
            'especie': 'Perro',
            'principios_activos': 'Meglumina Antimonato;Miltefosina;Domperidona',
            'indicaciones': 'Tratamiento de leishmaniasis visceral. Profilaxis post-infección.',
            'contraindicaciones': 'Insuficiencia renal/hepática grave.',
            'notas': 'Enfermedad compleja. Requiere tratamiento prolongado. Zoonótica.'
        },
        
        # ANTIHISTAMÍNICOS
        {
            'enfermedad': 'Reacción alérgica aguda',
            'categoria': 'Dermatología',
            'especie': 'Perro',
            'principios_activos': 'Difenhidramina;Cetirizina;Loratadina;Ketamina',
            'indicaciones': 'Anafilaxia. Reacciones alérgicas sistémicas. Angioedema.',
            'contraindicaciones': 'Hipersensibilidad conocida.',
            'notas': 'Difenhidramina de acción rápida IM/IV. Cetirizina oral crónica.'
        },
        
        # INFECCIONES FÚNGICAS
        {
            'enfermedad': 'Infección fúngica sistémica',
            'categoria': 'Infectología',
            'especie': 'Perro',
            'principios_activos': 'Itraconazol;Ketoconazol;Fluconazol;Enilconazol',
            'indicaciones': 'Infecciones por hongos. Dermatofitosis. Histoplasmosis.',
            'contraindicaciones': 'Insuficiencia hepática severa.',
            'notas': 'Tratamiento prolongado típicamente (6-12 semanas). Monitoreo hepático.'
        },
    ]
    
    # Carga CSV existente
    df_existente = pd.read_csv('data/raw/enfermedades_medicamentos_cimavet.csv')
    
    # Crea DataFrame con nuevas enfermedades
    df_nuevas = pd.DataFrame(nuevas_enfermedades)
    
    # Combina
    df_expandido = pd.concat([df_existente, df_nuevas], ignore_index=True)
    
    # Guarda
    output_path = 'data/raw/enfermedades_medicamentos_cimavet_expandido.csv'
    df_expandido.to_csv(output_path, index=False, encoding='utf-8')
    
    print("\n" + "="*80)
    print("✅ CSV DE ENFERMEDADES EXPANDIDO")
    print("="*80 + "\n")
    
    print(f"Enfermedades originales: {len(df_existente)}")
    print(f"Enfermedades nuevas: {len(df_nuevas)}")
    print(f"Total enfermedades: {len(df_expandido)}")
    print(f"\nGuardado en: {output_path}\n")
    
    print("📋 NUEVAS ENFERMEDADES AÑADIDAS:")
    print("-" * 80)
    
    for idx, row in df_nuevas.iterrows():
        print(f"\n{idx + len(df_existente) + 1}. {row['enfermedad']}")
        print(f"   Especie: {row['especie']}")
        print(f"   Categoría: {row['categoria']}")
        print(f"   Principios: {row['principios_activos'][:60]}...")
    
    print("\n" + "="*80)
    print("📊 RESUMEN POR CATEGORÍA (EXPANDIDO):")
    print("="*80 + "\n")
    
    for cat in df_expandido['categoria'].unique():
        count = len(df_expandido[df_expandido['categoria'] == cat])
        print(f"  - {cat}: {count} patologías")
    
    print("\n📈 DISTRIBUCIÓN POR ESPECIE:")
    print(f"  - Perros: {len(df_expandido[df_expandido['especie']=='Perro'])} patologías")
    print(f"  - Gatos: {len(df_expandido[df_expandido['especie']=='Gato'])} patologías")
    print(f"  - Perras: {len(df_expandido[df_expandido['especie']=='Perra'])} patologías")
    
    print("\n" + "="*80)
    print("⚠️  PRÓXIMO PASO:")
    print("="*80)
    print("\nRenombra el nuevo CSV y re-ejecuta el mapeo:")
    print("  1. cp data/raw/enfermedades_medicamentos_cimavet_expandido.csv data/raw/enfermedades_medicamentos_cimavet.csv")
    print("  2. python src/processing/mapear_medicamentos_enfermedades.py")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    expandir_enfermedades()